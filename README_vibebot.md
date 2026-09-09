# VibeBot — Creative Resonance System

## Overview
VibeBot is a creative resonance system for the ixpansion organism that monitors system state and broadcasts "vibe" pulses to connected agents. It integrates with the Telegram aleph_bot and provides API endpoints for vibe state management.

## Features

### Vibe Pulse Generation
- Generates random vibe pulses with types: surge, ebb, ripple, tsunami, whisper, crescendo, decay, explosion, stillness, pulse
- Each pulse has 10 vector fields: coherence, entropy, creativity, stability, consciousness, resonance, harmony, discord, growth, decay
- Intensity ranges from 0.1 to 1.0
- History tracking limited to 50 most recent pulses

### API Endpoints
- `GET /api/vibebot/state` - Get current vibe state
- `POST /api/vibebot/pulse` - Generate and broadcast a new vibe pulse
- `GET /api/vibebot/history` - Get recent vibe pulse history

### Telegram Integration
- Broadcasts vibe pulses to registered Telegram chat IDs
- Uses bot token from environment variable `VIBE_BOT`
- Can send custom messages alongside auto-generated pulses

### Dashboard Component
- React component `dashboard/components/VibeDashboard.jsx` displays current vibe state
- Shows: current type, intensity, vector values, history count
- Auto-refreshes every 30 seconds

## Usage

### Generate a vibe pulse (Python)
```python
from api.vibebot import generate_vibe_pulse
pulse = generate_vibe_pulse()
print(json.dumps(pulse, indent=2))
```

### Broadcast a pulse
```python
from api.vibebot import broadcast_vibe
result = broadcast_vibe()
```

### Check current state
```python
from api.vibebot import get_current_vibe
state = get_current_vibe()
```

## Configuration
- Set `VIBE_BOT` environment variable with Telegram bot token
- Default token is a placeholder; replace with actual bot token for Telegram integration
- API routes auto-register with the Flask app

## Development
- Module located at `api/vibebot.py`
- API routes at `api/vibebot_routes.py`
- Dashboard component at `dashboard/components/VibeDashboard.jsx`
- Data stored in `/root/.codex/` memories and sessions
