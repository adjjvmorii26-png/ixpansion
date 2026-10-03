from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def test_dashboard_does_not_contain_hardcoded_vibe_token():
    source = (ROOT / "dashboard" / "VibeDashboardApp.jsx").read_text()
    assert "9bb7866ec849391842c1f93732109d4883c7e98849060447b98436a202f41a40" not in source
    assert "process.env.VIBE_BOT || ''" in source

def test_cloudflare_tunnel_token_is_shell_quoted_and_minimal():
    source = (ROOT / ".github" / "workflows" / "deploy-api.yml").read_text()
    assert 'cloudflared tunnel run --token "$CF_TUNNEL_TOKEN"' in source
    assert "CF_API_TOKEN:" not in source
    assert "CF_ACCOUNT_ID:" not in source
