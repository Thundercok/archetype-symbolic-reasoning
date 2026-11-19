"""Invariant tests for the 36-card Lenormand engine."""

from archetype_symbolic.core.lenormand import LENORMAND_36, draw_lenormand


def test_lenormand_deck_cardinality() -> None:
    assert len(LENORMAND_36) == 36
    assert [c["num"] for c in LENORMAND_36] == [str(i) for i in range(1, 37)]


def test_draw_lenormand_seeded_and_clamped() -> None:
    r1 = draw_lenormand("Hỏi dự án", count=3, seed=123)
    r2 = draw_lenormand("Hỏi dự án", count=3, seed=123)
    assert r1 == r2
    assert r1["visual_type"] == "lenormand"
    assert len(r1["cards"]) == 3
    assert len({c["number"] for c in r1["cards"]}) == 3
    assert len(draw_lenormand(count=99, seed=1)["cards"]) == 5
    assert len(draw_lenormand(count=0, seed=1)["cards"]) == 1
