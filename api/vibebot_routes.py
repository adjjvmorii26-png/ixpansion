"""VibeBot API routes for the ixpansion organism."""
from flask import Blueprint, jsonify, request
from .vibebot import get_current_vibe, broadcast_vibe

vibebot_bp = Blueprint('vibebot', __name__)

@vibebot_bp.route('/state', methods=['GET'])
def state():
    """Get current vibe state."""
    try:
        state = get_current_vibe()
        return jsonify(state)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@vibebot_bp.route('/pulse', methods=['POST'])
def pulse():
    """Generate and broadcast a new vibe pulse."""
    try:
        result = broadcast_vibe()
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@vibebot_bp.route('/history', methods=['GET'])
def history():
    """Get vibe pulse history."""
    from api.vibebot import _vibe_state
    return jsonify({"history": _vibe_state.get("history", [])[-20:]})
