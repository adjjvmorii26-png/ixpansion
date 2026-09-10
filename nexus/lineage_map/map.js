const lineage = require("./lineage.json");
function list() { return lineage.systems; }
function byTheme(theme) { return lineage.themes[theme] || []; }
function themes() { return Object.keys(lineage.themes); }
function count() { return lineage.systems.length; }
module.exports = { list, byTheme, themes, count };
