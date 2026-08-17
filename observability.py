#!/usr/bin/env python3
"""IXPANSION Observability: Metrics, tracing, and monitoring.

Provides a comprehensive observability framework with:
- Metrics collection and reporting
- Event tracing and correlation
- Health checks and diagnostics
- Performance profiling
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional
from collections import defaultdict


class MetricType(Enum):
    """Types of metrics."""
    COUNTER = "counter"          # Monotonically increasing
    GAUGE = "gauge"              # Current value
    HISTOGRAM = "histogram"       # Distribution of values
    TIMER = "timer"              # Duration measurements


class EventLevel(Enum):
    """Event severity levels."""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass(frozen=True)
class Metric:
    """A single metric measurement."""
    
    name: str
    value: float
    timestamp: float
    metric_type: MetricType
    tags: Dict[str, str] = field(default_factory=dict)
    unit: str = ""
    
    def __lt__(self, other: Metric) -> bool:
        """For sorting by timestamp."""
        return self.timestamp < other.timestamp


@dataclass(frozen=True)
class Event:
    """A traced event for observability."""
    
    name: str
    level: EventLevel
    timestamp: float
    trace_id: str
    span_id: str
    duration_ms: float = 0.0
    message: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    parent_span_id: Optional[str] = None


class MetricsCollector:
    """Collects and aggregates metrics."""
    
    def __init__(self):
        """Initialize metrics collector."""
        self.metrics: Dict[str, List[Metric]] = defaultdict(list)
        self.counters: Dict[str, float] = {}
        self.gauges: Dict[str, float] = {}
        self.histograms: Dict[str, List[float]] = defaultdict(list)
        self.last_reset = time.time()
    
    def counter(self, name: str, value: float = 1.0, tags: Optional[Dict[str, str]] = None) -> None:
        """Record a counter metric (monotonically increasing)."""
        self.counters[name] = self.counters.get(name, 0.0) + value
        metric = Metric(
            name=name,
            value=self.counters[name],
            timestamp=time.time(),
            metric_type=MetricType.COUNTER,
            tags=tags or {},
        )
        self.metrics[name].append(metric)
    
    def gauge(self, name: str, value: float, tags: Optional[Dict[str, str]] = None) -> None:
        """Record a gauge metric (current value)."""
        self.gauges[name] = value
        metric = Metric(
            name=name,
            value=value,
            timestamp=time.time(),
            metric_type=MetricType.GAUGE,
            tags=tags or {},
        )
        self.metrics[name].append(metric)
    
    def histogram(self, name: str, value: float, tags: Optional[Dict[str, str]] = None) -> None:
        """Record a histogram metric (distribution)."""
        self.histograms[name].append(value)
        metric = Metric(
            name=name,
            value=value,
            timestamp=time.time(),
            metric_type=MetricType.HISTOGRAM,
            tags=tags or {},
        )
        self.metrics[name].append(metric)
    
    def timer(self, name: str, duration_ms: float, tags: Optional[Dict[str, str]] = None) -> None:
        """Record a timer metric (duration)."""
        metric = Metric(
            name=name,
            value=duration_ms,
            timestamp=time.time(),
            metric_type=MetricType.TIMER,
            tags=tags or {},
            unit="ms",
        )
        self.metrics[name].append(metric)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of all metrics."""
        def compute_stats(values: List[float]) -> Dict[str, float]:
            if not values:
                return {}
            sorted_vals = sorted(values)
            return {
                "count": len(values),
                "min": min(values),
                "max": max(values),
                "mean": sum(values) / len(values),
                "median": sorted_vals[len(values) // 2],
                "p95": sorted_vals[int(len(values) * 0.95)],
                "p99": sorted_vals[int(len(values) * 0.99)],
            }
        
        return {
            "counters": self.counters.copy(),
            "gauges": self.gauges.copy(),
            "histograms": {
                name: compute_stats(values)
                for name, values in self.histograms.items()
            },
            "uptime_seconds": time.time() - self.last_reset,
        }
    
    def reset(self) -> None:
        """Reset all metrics."""
        self.metrics.clear()
        self.counters.clear()
        self.gauges.clear()
        self.histograms.clear()
        self.last_reset = time.time()


class EventTracer:
    """Traces events with distributed tracing support."""
    
    def __init__(self):
        """Initialize event tracer."""
        self.events: List[Event] = []
        self.active_spans: Dict[str, float] = {}  # span_id -> start_time
        self._span_counter = 0
    
    def start_span(self, trace_id: str, name: str) -> str:
        """Start a new span and return its ID."""
        span_id = f"span-{self._span_counter}"
        self._span_counter += 1
        self.active_spans[span_id] = time.time()
        
        event = Event(
            name=name,
            level=EventLevel.DEBUG,
            timestamp=time.time(),
            trace_id=trace_id,
            span_id=span_id,
            message="span started",
        )
        self.events.append(event)
        return span_id
    
    def end_span(self, span_id: str, trace_id: str, name: str) -> None:
        """End a span."""
        if span_id not in self.active_spans:
            return
        
        start_time = self.active_spans.pop(span_id)
        duration_ms = (time.time() - start_time) * 1000
        
        event = Event(
            name=name,
            level=EventLevel.DEBUG,
            timestamp=time.time(),
            trace_id=trace_id,
            span_id=span_id,
            duration_ms=duration_ms,
            message="span completed",
        )
        self.events.append(event)
    
    def log_event(
        self,
        name: str,
        level: EventLevel,
        trace_id: str,
        span_id: str,
        message: str = "",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Log an event."""
        event = Event(
            name=name,
            level=level,
            timestamp=time.time(),
            trace_id=trace_id,
            span_id=span_id,
            message=message,
            metadata=metadata or {},
        )
        self.events.append(event)
    
    def get_trace(self, trace_id: str) -> List[Event]:
        """Get all events for a trace."""
        return [e for e in self.events if e.trace_id == trace_id]
    
    def clear(self) -> None:
        """Clear all events."""
        self.events.clear()
        self.active_spans.clear()


class HealthCheck:
    """Health check for system components."""
    
    def __init__(self, name: str):
        """Initialize health check."""
        self.name = name
        self.status = "unknown"
        self.last_checked: Optional[float] = None
        self.details: Dict[str, Any] = {}
        self.error: Optional[str] = None
    
    def check(self, callback: Any) -> bool:
        """Run a health check."""
        try:
            result = callback()
            self.status = "healthy" if result else "unhealthy"
            self.last_checked = time.time()
            self.error = None
            return result
        except Exception as e:
            self.status = "error"
            self.last_checked = time.time()
            self.error = str(e)
            return False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "status": self.status,
            "last_checked": self.last_checked,
            "details": self.details,
            "error": self.error,
        }


class HealthChecker:
    """Manages multiple health checks."""
    
    def __init__(self):
        """Initialize health checker."""
        self.checks: Dict[str, HealthCheck] = {}
    
    def register(self, name: str, callback: Any) -> HealthCheck:
        """Register a health check."""
        check = HealthCheck(name)
        check.check(callback)
        self.checks[name] = check
        return check
    
    def check_all(self, callbacks: Dict[str, Any]) -> Dict[str, bool]:
        """Run all health checks."""
        results = {}
        for name, callback in callbacks.items():
            if name not in self.checks:
                self.register(name, callback)
            results[name] = self.checks[name].check(callback)
        return results
    
    def get_status(self) -> Dict[str, Any]:
        """Get overall health status."""
        all_checks = [c.to_dict() for c in self.checks.values()]
        healthy_count = sum(1 for c in self.checks.values() if c.status == "healthy")
        total_count = len(self.checks)
        
        return {
            "overall": "healthy" if healthy_count == total_count else "degraded",
            "healthy_checks": healthy_count,
            "total_checks": total_count,
            "checks": all_checks,
        }


class PerformanceProfiler:
    """Profiles code performance."""
    
    def __init__(self):
        """Initialize profiler."""
        self.measurements: Dict[str, List[float]] = defaultdict(list)
    
    def measure(self, name: str, duration_ms: float) -> None:
        """Record a performance measurement."""
        self.measurements[name].append(duration_ms)
    
    def get_report(self) -> Dict[str, Dict[str, float]]:
        """Get performance report."""
        report = {}
        for name, durations in self.measurements.items():
            if not durations:
                continue
            sorted_durations = sorted(durations)
            report[name] = {
                "count": len(durations),
                "min_ms": min(durations),
                "max_ms": max(durations),
                "avg_ms": sum(durations) / len(durations),
                "median_ms": sorted_durations[len(durations) // 2],
                "p95_ms": sorted_durations[int(len(durations) * 0.95)],
                "p99_ms": sorted_durations[int(len(durations) * 0.99)],
            }
        return report
    
    def clear(self) -> None:
        """Clear all measurements."""
        self.measurements.clear()


# Global instances
_metrics_collector: Optional[MetricsCollector] = None
_event_tracer: Optional[EventTracer] = None
_health_checker: Optional[HealthChecker] = None
_performance_profiler: Optional[PerformanceProfiler] = None


def get_metrics_collector() -> MetricsCollector:
    """Get global metrics collector."""
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = MetricsCollector()
    return _metrics_collector


def get_event_tracer() -> EventTracer:
    """Get global event tracer."""
    global _event_tracer
    if _event_tracer is None:
        _event_tracer = EventTracer()
    return _event_tracer


def get_health_checker() -> HealthChecker:
    """Get global health checker."""
    global _health_checker
    if _health_checker is None:
        _health_checker = HealthChecker()
    return _health_checker


def get_performance_profiler() -> PerformanceProfiler:
    """Get global performance profiler."""
    global _performance_profiler
    if _performance_profiler is None:
        _performance_profiler = PerformanceProfiler()
    return _performance_profiler
