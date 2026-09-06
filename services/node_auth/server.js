/**
 * IXpansion Node.js Auth Server
 * JWT-based login with bcrypt password hashing, cookie sessions,
 * and role-based access to the organism's API surface.
 *
 * Ports: 4000 (auth) — proxies /api/* requests to the Python server on 3000.
 */
"use strict";
const express = require("express");
const jwt = require("jsonwebtoken");
const bcrypt = require("bcryptjs");
const cookieParser = require("cookie-parser");
const cors = require("cors");
const crypto = require("crypto");
const fs = require("fs");
const path = require("path");
const http = require("http");

const app = express();
const PORT = parseInt(process.env.AUTH_PORT || "4000", 10);
const API_ORIGIN = process.env.API_ORIGIN || "http://127.0.0.1:3000";
const JWT_SECRET = process.env.JWT_SECRET || crypto.randomBytes(32).toString("hex");
const JWT_EXPIRY = process.env.JWT_EXPIRY || "24h";
const USERS_FILE = path.join(__dirname, "users.json");

// ─── Middleware ───────────────────────────────────────────────
app.use(cors({ origin: true, credentials: true }));
app.use(express.json());
app.use(cookieParser());

// ─── User store ──────────────────────────────────────────────
function loadUsers() {
  try { return JSON.parse(fs.readFileSync(USERS_FILE, "utf8")); }
  catch { return {}; }
}
function saveUsers(db) {
  fs.writeFileSync(USERS_FILE, JSON.stringify(db, null, 2));
}
function hashPassword(pw) {
  return bcrypt.hashSync(pw, 10);
}
function checkPassword(pw, hash) {
  return bcrypt.compareSync(pw, hash);
}

// Seed default admin if no users exist
const db = loadUsers();
if (Object.keys(db).length === 0) {
  const adminHash = hashPassword("organism");
  db["admin"] = {
    username: "admin",
    password: adminHash,
    role: "admin",
    created: new Date().toISOString(),
    tier: "enterprise",
    display_name: "ALEPH",
  };
  saveUsers(db);
  console.log("[auth] seeded default admin user (admin / organism)");
}

// ─── JWT helpers ─────────────────────────────────────────────
function signToken(user) {
  return jwt.sign(
    { sub: user.username, role: user.role, tier: user.tier, display: user.display_name },
    JWT_SECRET,
    { expiresIn: JWT_EXPIRY }
  );
}
function verifyToken(token) {
  try { return jwt.verify(token, JWT_SECRET); }
  catch { return null; }
}
function authMiddleware(req, res, next) {
  const token =
    req.cookies?.ixp_token ||
    (req.headers.authorization || "").replace("Bearer ", "");
  if (!token) return res.status(401).json({ error: "no token — please log in" });
  const payload = verifyToken(token);
  if (!payload) return res.status(401).json({ error: "invalid or expired token" });
  req.user = payload;
  next();
}

// ─── Routes ──────────────────────────────────────────────────

// Health check
app.get("/auth/health", (_req, res) => {
  res.json({ status: "ok", service: "ixpansion-node-auth", users: Object.keys(db).length });
});

// Login
app.post("/auth/login", (req, res) => {
  const { username, password } = req.body || {};
  if (!username || !password)
    return res.status(400).json({ error: "username and password required" });
  const user = db[username.toLowerCase()];
  if (!user || !checkPassword(password, user.password))
    return res.status(401).json({ error: "invalid credentials" });
  const token = signToken(user);
  res.cookie("ixp_token", token, { httpOnly: true, maxAge: 86400000, sameSite: "lax" });
  res.json({ ok: true, token, user: { username: user.username, role: user.role, tier: user.tier, display_name: user.display_name } });
});

// Register (open for free tier, or protected for higher tiers)
app.post("/auth/register", (req, res) => {
  const { username, password, display_name, tier } = req.body || {};
  if (!username || !password)
    return res.status(400).json({ error: "username and password required" });
  const key = username.toLowerCase();
  if (db[key])
    return res.status(409).json({ error: "user already exists" });
  db[key] = {
    username: key,
    password: hashPassword(password),
    role: "user",
    created: new Date().toISOString(),
    tier: tier || "free",
    display_name: display_name || username,
  };
  saveUsers(db);
  const token = signToken(db[key]);
  res.cookie("ixp_token", token, { httpOnly: true, maxAge: 86400000, sameSite: "lax" });
  res.json({ ok: true, token, user: { username: key, role: "user", tier: db[key].tier } });
});

// Logout
app.post("/auth/logout", (_req, res) => {
  res.clearCookie("ixp_token");
  res.json({ ok: true, message: "logged out" });
});

// Current user
app.get("/auth/me", authMiddleware, (req, res) => {
  const u = db[req.user.sub] || {};
  res.json({
    username: req.user.sub,
    role: req.user.role,
    tier: req.user.tier,
    display_name: req.user.display,
    created: u.created,
  });
});

// List users (admin only)
app.get("/auth/users", authMiddleware, (req, res) => {
  if (req.user.role !== "admin")
    return res.status(403).json({ error: "admin only" });
  const list = Object.values(db).map(({ password, ...rest }) => rest);
  res.json({ users: list, count: list.length });
});

// Delete user (admin only)
app.delete("/auth/users/:username", authMiddleware, (req, res) => {
  if (req.user.role !== "admin")
    return res.status(403).json({ error: "admin only" });
  const u = req.params.username.toLowerCase();
  if (!db[u]) return res.status(404).json({ error: "not found" });
  delete db[u];
  saveUsers(db);
  res.json({ ok: true, deleted: u });
});

// ─── Token refresh ───────────────────────────────────────────
app.post("/auth/refresh", authMiddleware, (req, res) => {
  const user = db[req.user.sub];
  if (!user) return res.status(401).json({ error: "user not found" });
  const token = signToken(user);
  res.cookie("ixp_token", token, { httpOnly: true, maxAge: 86400000, sameSite: "lax" });
  res.json({ ok: true, token });
});

// ─── Serve login page ────────────────────────────────────────
app.get("/", (_req, res) => {
  res.sendFile(path.join(__dirname, "login.html"));
});

// ─── Proxy authenticated requests to the Python API ──────────
app.all("/api/*", authMiddleware, (req, res) => {
  const url = new URL(req.url, API_ORIGIN);
  const headers = { ...req.headers, host: url.host };
  delete headers.cookie;
  delete headers["content-length"];
  if (req.user) headers["X-Auth-User"] = req.user.sub;
  if (req.user) headers["X-Auth-Role"] = req.user.role;
  if (req.user) headers["X-Auth-Tier"] = req.user.tier;

  const proxyReq = http.request(
    {
      hostname: url.hostname,
      port: url.port,
      path: url.pathname + url.search,
      method: req.method,
      headers,
    },
    (proxyRes) => {
      res.writeHead(proxyRes.statusCode, proxyRes.headers);
      proxyRes.pipe(res);
    }
  );
  proxyReq.on("error", (err) => {
    res.status(502).json({ error: "upstream api unavailable", detail: err.message });
  });
  req.pipe(proxyReq);
});

// ─── Start ───────────────────────────────────────────────────
app.listen(PORT, () => {
  console.log(`[ixpansion-auth] listening on http://127.0.0.1:${PORT}`);
  console.log(`[ixpansion-auth] JWT secret: ${JWT_SECRET.slice(0, 8)}…`);
  console.log(`[ixpansion-auth] users: ${Object.keys(db).join(", ") || "(none)"}`);
});
