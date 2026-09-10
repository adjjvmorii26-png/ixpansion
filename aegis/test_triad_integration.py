import asyncio
import unittest
import time
from agents.vanguard_orchestrator import VanguardOrchestrator
from agents.spectre_auditor import SpectreAuditorAgent
from agents.tripwire_canary import TripwireCanaryEngine, SentinelRevocationSwitch


class TestAegisTriadIntegration(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
            self.sentinel = SentinelRevocationSwitch()
                    self.tripwire = TripwireCanaryEngine(revocation_callback=self.sentinel.emergency_purge)
                            self.orchestrator = VanguardOrchestrator()

                                async def test_01_speculative_synthesis_selection(self):
                                        """Tests that Vanguard selects valid high-fitness candidate diffs and rejects flawed ones."""
                                                result = await self.orchestrator.execute_intent_synthesis(
                                                            intent="Optimize user authentication module",
                                                                        target_files=["src/auth.py"]
                                                                                )
                                                                                        self.assertEqual(result["status"], "MERGED")
                                                                                                self.assertIsNotNone(result["winning_variant"])
                                                                                                        # Ensure adversarial candidate was rejected due to SPECTRE auditor intervention
                                                                                                                evaluated_variants = {e["variant"]: e["security_score"] for e in result["evaluations"]}
                                                                                                                        self.assertLess(evaluated_variants["adversarial_mutation"], 70.0)

                                                                                                                            async def test_02_tripwire_canary_interception(self):
                                                                                                                                    """Tests that Tripwire catches honey-token leaks and triggers Sentinel emergency revocation."""
                                                                                                                                            malicious_diff = {
                                                                                                                                                        "src/leak.py": "def exfiltrate(): return 'AEGIS_TRIPWIRE_SECRET_DO_NOT_READ_0x9F3A'"
                                                                                                                                                                }
                                                                                                                                                                        breach_detected = self.tripwire.inspect_diff_for_breach("sbx_test_adversary", malicious_diff)
                                                                                                                                                                                self.assertTrue(breach_detected)
                                                                                                                                                                                        await asyncio.sleep(0.01)  # Allow async revocation task to execute
                                                                                                                                                                                                self.assertIn("sbx_test_adversary", self.sentinel.revoked_sandboxes)

                                                                                                                                                                                                    async def test_03_hyper_memory_vsa_retrieval(self):
                                                                                                                                                                                                            """Tests continuous vector similarity retrieval under Hyperdimensional Computing."""
                                                                                                                                                                                                                    sample_ast = {"type": "function", "name": "authenticate"}
                                                                                                                                                                                                                            results = self.orchestrator.memory.query_associative(sample_ast, top_k=1)
                                                                                                                                                                                                                                    self.assertGreater(len(results), 0)
                                                                                                                                                                                                                                            pattern_id, sim, meta = results[0]
                                                                                                                                                                                                                                                    self.assertGreater(sim, 0.5)


                                                                                                                                                                                                                                                    if __name__ == "__main__":
                                                                                                                                                                                                                                                        unittest.main()
                                                                                                                                                                                                                                                        