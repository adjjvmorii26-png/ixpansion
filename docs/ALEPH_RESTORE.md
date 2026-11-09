# Aleph bot security restore (required)

`api/aleph_bot.py` was temporarily replaced during automated token scrub.

## Restore (one local sequence)

```bash
git fetch origin
git show a83defc5b5fa438fd6054d378f756ecbf1a35a8d:api/aleph_bot.py > api/aleph_bot.py
python3 scripts/scrub_telegram_token.py api/aleph_bot.py
grep -n TELEGRAM_BOT_TOKEN api/aleph_bot.py
git add api/aleph_bot.py
git commit -m "security: restore aleph_bot scrubbed — env-only TELEGRAM_BOT_TOKEN"
git push
```

## After restore

1. BotFather: revoke old tokens; set new TELEGRAM_BOT_TOKEN on Vercel only
2. Redeploy
3. Confirm secret-scanning alerts close

## Do not

- Commit tokens
- Redeploy until env var is set (bot fails closed without token)
