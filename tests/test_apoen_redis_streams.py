import unittest
from api.apoen_redis_streams import evaluate_heartbeats, read_heartbeats
from api.apoen_somatic_gc import GCPolicy, SomaticGarbageCollector, sign_heartbeat

class FakeRedis:
    def __init__(self, response):
        self.response = response
        self.calls = []
    def xread(self, streams, *, count, block):
        self.calls.append((streams, count, block))
        return self.response

class ApoenRedisStreamTests(unittest.TestCase):
    def setUp(self):
        self.payload = {"branch_id":"branch-a","cluster_id":"CLUSTER-OMEGA","created_at":100,"last_heartbeat":200,"interaction_count":1}
        self.secret = b"stream-test-secret"
        self.signature = sign_heartbeat(self.payload, self.secret)

    def test_reads_bounded_batch_without_ack_or_delete(self):
        fields = {key:str(value).encode() for key,value in self.payload.items()}
        fields[b"signature"] = self.signature.encode()
        redis = FakeRedis([(b"apoen:telemetry", [(b"1-0", fields)])])
        records = read_heartbeats(redis, "apoen:telemetry", count=5, block_ms=250)
        self.assertEqual(records[0]["heartbeat_payload"], self.payload)
        self.assertEqual(redis.calls, [({"apoen:telemetry":"$"},5,250)])

    def test_rejects_malformed_or_missing_fields(self):
        redis = FakeRedis([("apoen:telemetry", [("1-0", {"branch_id":"x"})])])
        with self.assertRaisesRegex(ValueError, "missing fields"):
            read_heartbeats(redis, "apoen:telemetry")

    def test_rejects_unbounded_read_parameters(self):
        with self.assertRaises(ValueError):
            read_heartbeats(FakeRedis([]), "apoen:telemetry", count=501)
        with self.assertRaises(ValueError):
            read_heartbeats(FakeRedis([]), "apoen:telemetry", block_ms=6000)

    def test_valid_stream_heartbeat_can_only_produce_candidate(self):
        fields = {key:str(value) for key,value in self.payload.items()}
        fields["signature"] = self.signature
        records = read_heartbeats(FakeRedis([("apoen:telemetry", [("1-0", fields)])]), "apoen:telemetry")
        gc = SomaticGarbageCollector("CLUSTER-OMEGA", GCPolicy(stale_after_seconds=100, minimum_age_seconds=500, maximum_interactions=2))
        results = evaluate_heartbeats(gc, records, self.secret, now=1000)
        self.assertEqual(results[0]["evaluation"]["decision"], "CANDIDATE")
        self.assertFalse(results[0]["destructive_action_performed"])

    def test_altered_signed_telemetry_is_retained(self):
        fields = {key:str(value) for key,value in self.payload.items()}
        fields["interaction_count"] = "0"
        fields["signature"] = self.signature
        records = read_heartbeats(FakeRedis([("apoen:telemetry", [("1-0", fields)])]), "apoen:telemetry")
        gc = SomaticGarbageCollector("CLUSTER-OMEGA", GCPolicy(stale_after_seconds=100, minimum_age_seconds=500, maximum_interactions=2))
        results = evaluate_heartbeats(gc, records, self.secret, now=1000)
        self.assertEqual(results[0]["evaluation"]["reason"], "heartbeat_binding_mismatch")
        self.assertFalse(results[0]["evaluation"]["eligible"])

if __name__ == "__main__":
    unittest.main()
