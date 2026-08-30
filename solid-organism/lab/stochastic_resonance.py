#!/usr/bin/env python3
"""Stochastic Resonance: adding noise amplifies weak signals.

In certain nonlinear systems, adding random noise to a weak periodic signal
makes the signal MORE detectable, not less. This is how crayfish detect
predator footsteps in noisy water. How neurons fire more precisely with
jitter. How neurons in the auditory cortex respond better with background noise.

This module demonstrates stochastic resonance: a threshold detector that
fails to detect a weak signal until noise is added at just the right level.

Usage:
    python3 stochastic_resonance.py --signal-amp 0.3 --noise-level 0.5 --samples 5000
    python3 stochastic_resonance.py --sweep          # sweep noise levels, find optimal
"""
from __future__ import annotations

import argparse
import json
import math
import random
from typing import Any, Dict, List, Tuple


def _sine_signal(t: float, frequency: float, amplitude: float, phase: float) -> float:
    """Generate a clean sine wave signal."""
    return amplitude * math.sin(2 * math.pi * frequency * t + phase)


def _threshold_detect(signal: float, threshold: float) -> int:
    """Binary threshold detector: 1 if signal > threshold, else 0."""
    return 1 if signal > threshold else 0


def _signal_quality(detected: List[int], frequency: float, dt: float,
                   num_samples: int) -> float:
    """Measure how well the detector captures the input frequency.

    Uses autocorrelation at the signal period to measure spectral purity.
    """
    n = len(detected)
    if n < 4:
        return 0.0

    period = int(round(1.0 / (frequency * dt)))
    if period < 2 or period >= n // 2:
        return 0.0

    mean_val = sum(detected) / n
    if mean_val == 0 or mean_val == 1:
        return 0.0

    variance = sum((d - mean_val) ** 2 for d in detected) / n
    if variance == 0:
        return 0.0

    # autocorrelation at the signal period
    autocorr = 0.0
    count = 0
    for i in range(n - period):
        autocorr += (detected[i] - mean_val) * (detected[i + period] - mean_val)
        count += 1

    autocorr /= (count * variance)
    return max(0.0, autocorr)


def detect(signal_amp: float, noise_level: float, threshold: float,
           num_samples: int = 5000, frequency: float = 0.05,
           seed: int = 42) -> Dict[str, Any]:
    """Run a single detection experiment.

    A weak sine signal is fed into a threshold detector.
    When the signal amplitude is below the threshold, the clean signal
    produces NO detections. Adding noise at the right level amplifies
    the signal above the threshold.
    """
    rng = random.Random(seed)
    dt = 1.0  # each sample is one time unit

    # Generate composite signal: signal + noise
    composite = []
    clean_signal = []
    for i in range(num_samples):
        t = i * dt
        sig = _sine_signal(t, frequency, signal_amp, 0)
        noise = rng.gauss(0, noise_level)
        clean_signal.append(sig)
        composite.append(sig + noise)

    # Detect
    detected_clean = [_threshold_detect(s, threshold) for s in clean_signal]
    detected_noisy = [_threshold_detect(s, threshold) for s in composite]

    # Quality metrics
    quality_clean = _signal_quality(detected_clean, frequency, dt, num_samples)
    quality_noisy = _signal_quality(detected_noisy, frequency, dt, num_samples)

    detection_rate_clean = sum(detected_clean) / num_samples
    detection_rate_noisy = sum(detected_noisy) / num_samples

    return {
        "signal_amp": signal_amp,
        "noise_level": noise_level,
        "threshold": threshold,
        "frequency": frequency,
        "num_samples": num_samples,
        "clean": {
            "detection_rate": round(detection_rate_clean, 4),
            "signal_quality": round(quality_clean, 4),
            "detections": sum(detected_clean),
        },
        "noisy": {
            "detection_rate": round(detection_rate_noisy, 4),
            "signal_quality": round(quality_noisy, 4),
            "detections": sum(detected_noisy),
        },
        "resonance_detected": quality_noisy > quality_clean and quality_clean < 0.1,
        "amplification_ratio": round(quality_noisy / max(quality_clean, 0.001), 2),
        "philosophy": (
            "In the right conditions, noise is not the enemy of signal — "
            "it is the collaborator. A crayfish detects predators only when "
            "the water is noisy. A neuron fires more precisely with jitter."
        ),
    }


def sweep(signal_amp: float, threshold: float, num_samples: int = 5000,
          frequency: float = 0.05, seed: int = 42,
          noise_levels: int = 50) -> Dict[str, Any]:
    """Sweep through noise levels to find the optimal stochastic resonance.

    Returns the full curve of signal quality vs noise level.
    """
    results = []
    for i in range(noise_levels + 1):
        noise = i * (threshold * 2) / noise_levels  # sweep from 0 to 2x threshold
        r = detect(signal_amp, noise, threshold, num_samples, frequency, seed + i)
        results.append({
            "noise_level": round(noise, 4),
            "quality_noisy": r["noisy"]["signal_quality"],
            "quality_clean": r["clean"]["signal_quality"],
            "detection_rate": r["noisy"]["detection_rate"],
        })

    # Find optimal noise level
    best = max(results, key=lambda x: x["quality_noisy"])
    peak_index = results.index(best)

    return {
        "signal_amp": signal_amp,
        "threshold": threshold,
        "sweep_results": results,
        "optimal_noise": best["noise_level"],
        "optimal_quality": best["quality_noisy"],
        "peak_index": peak_index,
        "quality_without_noise": results[0]["quality_noisy"],
        "resonance_strength": round(best["quality_noisy"] - results[0]["quality_noisy"], 4),
        "frequency": frequency,
        "philosophy": (
            "There exists a precise amount of chaos that makes order more visible. "
            "Too little noise: the signal drowns in silence. Too much: the signal "
            "drowns in noise. Just right: the signal emerges like a star at twilight."
        ),
    }


def main():
    ap = argparse.ArgumentParser(description="Stochastic Resonance demonstration")
    ap.add_argument("--signal-amp", type=float, default=0.3,
                   help="Amplitude of the weak signal (must be < threshold)")
    ap.add_argument("--noise-level", type=float, default=0.5,
                   help="Standard deviation of added Gaussian noise")
    ap.add_argument("--threshold", type=float, default=1.0,
                   help="Detection threshold")
    ap.add_argument("--samples", type=int, default=5000,
                   help="Number of time samples")
    ap.add_argument("--frequency", type=float, default=0.05,
                   help="Signal frequency (cycles per sample)")
    ap.add_argument("--sweep", action="store_true",
                   help="Sweep noise levels to find optimal resonance")
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    if args.sweep:
        result = sweep(args.signal_amp, args.threshold, args.samples,
                      args.frequency, args.seed)
    else:
        result = detect(args.signal_amp, args.noise_level, args.threshold,
                       args.samples, args.frequency, args.seed)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
