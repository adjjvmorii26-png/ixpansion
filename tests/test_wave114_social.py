"""Wave 114 tests — Social & Ecosystem Layer (7 modules)."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def test_gossip_network_start():
    from api.gossip_network import GossipNetwork
    gn = GossipNetwork()
    result = gn.start_rumor("whisperer", "the system is evolving")
    assert result["rumor"]["origin"] == "whisperer"


def test_gossip_network_retell():
    from api.gossip_network import GossipNetwork
    gn = GossipNetwork()
    rumor = gn.start_rumor("a", "something interesting")
    result = gn.retell_rumor(rumor["rumor"]["id"], "b")
    assert result["hop"]["reteller"] == "b"


def test_faction_system_found():
    from api.faction_system import FactionSystem
    fs = FactionSystem()
    result = fs.found_faction("Innovators", "progress", "founder_1")
    assert result["faction"]["name"] == "Innovators"


def test_faction_system_recruit():
    from api.faction_system import FactionSystem
    fs = FactionSystem()
    f = fs.found_faction("Guardians", "protection", "a")
    result = fs.recruit(f["faction"]["id"], "b")
    assert result["agent"] == "b"


def test_talent_auction_list():
    from api.talent_auction import TalentAuction
    ta = TalentAuction()
    result = ta.list_auction("expert", "quantum_physics", 50.0)
    assert result["listed"]["skill"] == "quantum_physics"


def test_talent_auction_bid():
    from api.talent_auction import TalentAuction
    ta = TalentAuction()
    auction = ta.list_auction("s", "ml", 20.0)
    result = ta.place_bid(auction["listed"]["id"], "buyer", 30.0)
    assert result["accepted"] is True


def test_story_forge_create():
    from api.story_forge import StoryForge
    sf = StoryForge()
    result = sf.create_story("The Last Algorithm", "cyberpunk")
    assert result["story"]["title"] == "The Last Algorithm"


def test_story_forge_contribute():
    from api.story_forge import StoryForge
    sf = StoryForge()
    story = sf.create_story("Test Story")
    result = sf.contribute(story["story"]["id"], "author_1", "character", "The Architect")
    assert result["type"] == "character"


def test_territory_map_claim():
    from api.territory_map import TerritoryMap
    tm = TerritoryMap(3, 3)
    result = tm.claim("region_0_0", "settler")
    assert result["new_owner"] == "settler"


def test_territory_map_improve():
    from api.territory_map import TerritoryMap
    tm = TerritoryMap(3, 3)
    tm.claim("region_1_1", "builder")
    result = tm.improve("region_1_1", "farm")
    assert result["improvement"] == "farm"


def test_attention_economy_register():
    from api.attention_economy import AttentionEconomy
    ae = AttentionEconomy()
    result = ae.register("content_creator")
    assert result["registered"]["current"] == 50.0


def test_attention_economy_earn_and_spend():
    from api.attention_economy import AttentionEconomy
    ae = AttentionEconomy()
    ae.register("a")
    ae.earn_attention("a", 20.0, "viral_post")
    assert ae.agents["a"].current == 70.0
    result = ae.spend_attention("a", 10.0, "ad")
    assert ae.agents["a"].current == 60.0


def test_attention_economy_tick():
    from api.attention_economy import AttentionEconomy
    ae = AttentionEconomy()
    ae.register("a")
    ae.register("b")
    result = ae.tick()
    assert result["tick"] == 1


def test_skill_tree_define():
    from api.skill_tree import SkillTree
    st = SkillTree()
    result = st.define_skill("coding", 0)
    assert result["defined"]["tier"] == 0


def test_skill_tree_unlock():
    from api.skill_tree import SkillTree
    st = SkillTree()
    st.define_skill("basics", 0)
    st.define_skill("advanced", 1, ["basics"])
    result = st.unlock("agent_1", "basics")
    assert result["unlocked"] == "basics"


def test_skill_tree_unlock_requires_prereq():
    from api.skill_tree import SkillTree
    st = SkillTree()
    st.define_skill("a", 0)
    st.define_skill("b", 1, ["a"])
    result = st.unlock("agent_1", "b")
    assert "error" in result


def test_skill_tree_teach():
    from api.skill_tree import SkillTree
    st = SkillTree()
    st.define_skill("wisdom", 0)
    st.unlock("teacher", "wisdom")
    result = st.teach("teacher", "student", "wisdom")
    assert result["teacher"] == "teacher"
