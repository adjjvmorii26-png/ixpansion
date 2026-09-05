"""Wave 447 — Satellite Telemetry Parser

Parses and validates satellite pass telemetry data, checking for
anomalies, computing orbital parameters, and generating summary
reports. The organism tracks its own presence in orbit.
"""
from __future__ import annotations
import json, math, datetime, sys
from pathlib import Path
from dataclasses import dataclass
from typing import Optional

API_DIR = Path(__file__).parent
DATA_DIR = API_DIR.parent / "data"


@dataclass
class SatelliteState:
    """Current state of a satellite in orbit."""
    timestamp: datetime.datetime
    latitude: float      # degrees, -90 to 90
    longitude: float     # degrees, -180 to 180
    altitude: float      # kilometers, above Earth surface
    velocity: float      # km/s
    attitude: float      # roll angle, degrees
    power: float         # volts
    signal_strength: int # 0-100


# Earth constants
EARTH_RADIUS_KM = 6371.0


def validate_state(state: SatelliteState) -> list[str]:
    """Validate a satellite state vector, return list of issues."""
    issues = []
    
    # Latitude must be -90 to 90
    if not -90 <= state.latitude <= 90:
        issues.append(f"Invalid latitude: {state.latitude}")
    
    # Longitude must be -180 to 180
    if not -180 <= state.longitude <= 180:
        issues.append(f"Invalid longitude: {state.longitude}")
    
    # Altitude must be positive (above surface)
    if state.altitude <= 0:
        issues.append(f"Invalid altitude: {state.altitude} km (must be > 0)")
    
    # Typical LEO altitude range: 160-2000 km
    if state.altitude > 2000:
        issues.append(f"Altitude too high for LEO: {state.altitude} km")
    if state.altitude > 0 and state.altitude < 160:
        issues.append(f"Altitude too low (decay risk): {state.altitude} km")
    
    # Velocity must be positive
    if state.velocity <= 0:
        issues.append(f"Invalid velocity: {state.velocity} km/s")
    
    # Typical LEO velocity: 7-8 km/s
    if state.velocity > 10:
        issues.append(f"Velocity too high: {state.velocity} km/s")
    if state.velocity > 0 and state.velocity < 5:
        issues.append(f"Velocity too low for orbit: {state.velocity} km/s")
    
    # Attitude should be 0-360
    if not 0 <= state.attitude < 360:
        issues.append(f"Invalid attitude: {state.attitude}")
    
    # Power must be positive
    if state.power <= 0:
        issues.append(f"Invalid power: {state.power}V")
    
    # Signal strength 0-100
    if not 0 <= state.signal_strength <= 100:
        issues.append(f"Invalid signal strength: {state.signal_strength}")
    
    return issues


def compute_orbital_params(state: SatelliteState) -> dict:
    """Compute derived orbital parameters."""
    r = EARTH_RADIUS_KM + state.altitude  # distance from center
    
    # Circular orbit velocity check
    expected_velocity = math.sqrt(398600.4418 / r)  # km/s from vis-viva
    velocity_diff = abs(state.velocity - expected_velocity)
    
    return {
        "distance_from_center_km": r,
        "escape_velocity_km_s": math.sqrt(2 * 398600.4418 / r),
        "expected_velocity_km_s": round(expected_velocity, 4),
        "velocity_deviation_km_s": round(abs(state.velocity - expected_velocity), 4),
        "orbit_type": "circular" if abs(state.velocity - expected_velocity) < 0.1 else "elliptical",
    }


def parse_telemetry(data: dict) -> Optional[SatelliteState]:
    """Parse raw telemetry dict into SatelliteState, validating fields."""
    try:
        # Extract fields (support various key names)
        def get_val(keys):
            for key in keys:
                if key in data:
                    v = data[key]
                    # Convert various types to float
                    try:
                        return float(v)
                    except (TypeError, ValueError):
                        continue
            return None
        
        timestamp_str = data.get("timestamp", "")
        if isinstance(timestamp_str, (int, float)):
            timestamp = datetime.datetime.utcfromtimestamp(timestamp_str)
        elif isinstance(timestamp_str, str):
            # Try ISO format
            try:
                timestamp = datetime.datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            except ValueError:
                try:
                    timestamp = datetime.datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                except ValueError:
                    timestamp = datetime.datetime.utcnow()
        else:
            timestamp = datetime.datetime.utcnow()
        
        state = SatelliteState(
            timestamp=timestamp,
            latitude=get_val(["latitude", "lat", "LAT"]),
            longitude=get_val(["longitude", "lon", "LON"]),
            altitude=get_val(["altitude", "alt", "HEIGHT"]),
            velocity=get_val(["velocity", "v", "VEL"]),
            attitude=get_val(["attitude", "att", "ROLL"]),
            power=get_val(["power", "POWER", "VOLTS"]),
            signal_strength=get_val(["signal_strength", "STR", "SIG"]) or 50,  # default
        )
        
        return state
    except Exception:
        return None


def generate_report(state: SatelliteState, issues: list[str]) -> str:
    """Generate a human-readable telemetry report."""
    lines = [
        "=" * 50,
        "SATELLITE TELEMETRY REPORT",
        "=" * 50,
        f"Timestamp: {state.timestamp.isoformat()}",
        f"Latitude:  {state.latitude:.4f}°",
        f"Longitude: {state.longitude:.4f}°",
        f"Altitude:  {state.altitude:.1f} km above Earth",
        f"Velocity:  {state.velocity:.2f} km/s",
        f"Attitude:  {state.attitude:.2f}° roll",
        f"Power:     {state.power:.2f} V",
        f"Signal:    {state.signal_strength}/100",
        "=" * 50,
    ]
    
    if issues:
        lines.append("")
        lines.append("VALIDATION ISSUES:")
        for issue in issues:
            lines.append(f"  - {issue}")
    
    # Orbital parameters
    params = compute_orbital_params(state)
    lines.append("")
    lines.append("ORBITAL PARAMETERS:")
    lines.append(f"  Distance from Earth center: {params['distance_from_center_km']:.1f} km")
    lines.append(f"  Escape velocity: {params['escape_velocity_km_s']:.2f} km/s")
    lines.append(f"  Expected orbital velocity: {params['expected_velocity_km_s']:.2f} km/s")
    lines.append(f"  Velocity deviation: {params['velocity_deviation_km_s']:.2f} km/s")
    lines.append(f"  Orbit type: {params['orbit_type']}")
    
    lines.append("")
    lines.append("=" * 50)
    
    return "\n".join(lines)


def parse_and_report(data: dict) -> str:
    """Parse telemetry data and generate a full report."""
    state = parse_telemetry(data)
    if state is None:
        return "Could not parse telemetry data — missing or invalid fields."
    
    issues = validate_state(state)
    return generate_report(state, issues)


# For command-line usage
if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        try:
            with open(sys.argv[1]) as f:
                data = json.load(f)
            report = parse_and_report(data)
            print(report)
        except Exception as e:
            print(f"Error: {e}")
    else:
        # Demo with sample data
        sample = {
            "timestamp": "2026-01-15T12:30:00Z",
            "latitude": 45.0,
            "longitude": -122.0,
            "altitude": 400.0,
            "velocity": 7.66,
            "attitude": 10.0,
            "power": 3.3,
            "signal_strength": 85
        }
        report = parse_and_report(sample)
        print(report)
