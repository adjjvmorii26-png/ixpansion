"""Tests for Oracle Engine."""
import pytest
from oracle_engine import OracleEngine, PERSPECTIVES, _hash


def test_hash_is_deterministic():
    assert _hash("a", "b") == _hash("a", "b")
    assert _hash("a", "b") != _hash("a", "c")


def test_perspectives_complete():
    expected = {"strategist", "scientist", "philosopher", "poet", "critic", "synthesizer"}
    assert set(PERSPECTIVES.keys()) == expected


def test_query_returns_all_perspectives():
    engine = OracleEngine()
    result = engine.query("What is consciousness?")
    assert result["perspectives_used"] == 6
    assert len(result["analyses"]) == 6
    assert all("confidence" in a for a in result["analyses"])


def test_query_confidence_in_range():
    engine = OracleEngine()
    result = engine.query("Test question")
    assert 0 <= result["total_confidence"] <= 1
    assert 0 <= result["consensus"] <= 1


def test_query_with_subset():
    engine = OracleEngine()
    result = engine.query("Test", perspectives=["scientist", "critic"])
    assert result["perspectives_used"] == 2


def test_history_tracking():
    engine = OracleEngine()
    engine.query("First question")
    engine.query("Second question")
    assert engine.query_count == 2
    assert len(engine.history_view()) == 2


def test_stats():
    engine = OracleEngine()
    engine.query("Test 1")
    stats = engine.stats()
    assert stats["total_queries"] == 1
    assert 0 <= stats["avg_confidence"] <= 1


def test_synthesis_has_consensus():
    engine = OracleEngine()
    result = engine.query("Deep question about reality")
    assert "consensus_score" in result["synthesis"]
    assert "dimensions" in result["synthesis"]
    assert "synthesis_text" in result["synthesis"]
