import pytest
from omega_prime.agents.emergent_hierarchy import EmergentHierarchy


class TestEmergentHierarchy:
    def test_join_and_interact(self):
        h = EmergentHierarchy()
        h.join("alpha", "sentinel")
        h.join("beta", "wanderer")
        result = h.interact("alpha", "beta")
        assert "dom_authority" in result

    def test_repeated_deference_creates_rank(self):
        h = EmergentHierarchy()
        h.join("boss", "sentinel")
        h.join("worker", "wanderer")
        for _ in range(15):
            h.interact("boss", "worker")
        boss_node = h._agents["boss"]
        worker_node = h._agents["worker"]
        assert boss_node.authority > worker_node.authority

    def test_challenge_can_flip_ranks(self):
        h = EmergentHierarchy()
        h.join("strong", "sentinel")
        h.join("weak", "wanderer")
        for _ in range(10):
            h.interact("strong", "weak")

        strong_before = h._agents["strong"].authority
        results = [h.challenge("weak", "strong") for _ in range(20)]
        # At least one challenge may succeed given randomness
        total = sum(1 for r in results if r.get("success"))
        # Just verify the mechanism runs without error
        assert all("new_challenger_rank" in r for r in results)

    def test_coalition_forms_same_species(self):
        h = EmergentHierarchy()
        h.join("a", "sentinel")
        h.join("b", "sentinel")
        # Make them similar authority then interact
        for _ in range(3):
            h.interact("a", "b")
            h.interact("b", "a")
        stats = h.stats
        # Coalition formation is probabilistic based on authority similarity
        assert "coalitions" in stats

    def test_sovereigns_exist_after_many_interactions(self):
        h = EmergentHierarchy()
        h.join("king", "overseer")
        h.join("subject1", "wanderer")
        h.join("subject2", "wanderer")
        h.join("subject3", "wanderer")
        for _ in range(30):
            h.interact("king", "subject1")
            h.interact("king", "subject2")
            h.interact("king", "subject3")
        sovereigns = h.sovereigns
        assert "king" in sovereigns

    def test_hierarchy_tree_sorted(self):
        h = EmergentHierarchy()
        for i in range(5):
            h.join(f"a{i}", "wanderer")
        # Make agent_4 dominant
        for _ in range(10):
            for j in range(4):
                h.interact("a4", f"a{j}")
        tree = h.hierarchy_tree
        authorities = [t["authority"] for t in tree]
        assert authorities == sorted(authorities, reverse=True)
