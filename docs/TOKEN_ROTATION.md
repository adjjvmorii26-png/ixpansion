# Token rotation

## Telegram (Aleph bot)

1. BotFather → /revoke or issue new token for the bot
2. Set `TELEGRAM_BOT_TOKEN` on Vercel/host (no git)
3. Source must use: `os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()` only
4. Helper: `api/secrets_env.py`
5. Confirm GitHub secret-scanning alerts close after rotation

## LAB API token

```bash
python3 artifacts/sandboxes/lab/scripts/rotate_lab_token.py
# restart server; update localStorage LAB_API_TOKEN
```

## Automation status

| Token | Auto-rotate | Auto-scrub source |
|-------|-------------|-------------------|
| LAB_API_TOKEN | yes | n/a |
| TELEGRAM_BOT_TOKEN | operator (BotFather) | secrets_env + CI guard |
