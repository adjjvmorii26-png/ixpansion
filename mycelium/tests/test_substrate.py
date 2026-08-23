import pytest

from mycelium.nucleus.substrate import ResourceSite, Substrate


class TestSubstrate:
    def test_gradient_prefers_close_rich_sites(self):
        substrate = Substrate()
        substrate.add_site(ResourceSite("near", (0.1, 0), nutrient=6))
        substrate.add_site(ResourceSite("far", (4, 0), nutrient=12))
        gradient = substrate.gradient((0, 0))
        assert gradient["near"] > gradient["far"]

    def test_withdrawal_never_crosses_protected_reserve(self):
        substrate = Substrate()
        substrate.add_site(ResourceSite("site", (0, 0), nutrient=10, reserve=3))
        granted = substrate.withdraw("site", 99)
        assert granted == 7
        assert substrate.sites["site"].nutrient == 3

    def test_duplicate_site_and_invalid_geometry_are_rejected(self):
        substrate = Substrate()
        site = ResourceSite("same", (0, 0))
        substrate.add_site(site)
        with pytest.raises(ValueError):
            substrate.add_site(ResourceSite("same", (1, 1)))
        with pytest.raises(ValueError):
            ResourceSite("bad", (1, 2, 3))

    def test_signal_accumulates_without_changing_nutrients(self):
        substrate = Substrate()
        substrate.add_site(ResourceSite("site", (0, 0), nutrient=5))
        assert substrate.deposit_signal("site", 1.5) == 1.5
        assert substrate.deposit_signal("site", 0.5) == 2.0
        assert substrate.total_nutrient == 5
