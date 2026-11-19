"""Contract and invariant tests for the 78-card Tarot engine and verifier."""

import pytest

from archetype_symbolic.core.tarot import TAROT_DECK_78, draw_tarot, parse_cards
from archetype_symbolic.eval.verifiers import verify_tarot_spread


def test_deck_has_78_unique_cards() -> None:
    assert len(TAROT_DECK_78) == 78
    assert len({c["title"] for c in TAROT_DECK_78}) == 78


def test_jumper_does_not_shift_position_and_reversed_is_preserved() -> None:
    cards = parse_cards("rơi: 9 pent; 4 wands rev, 5 cups, queen cups ngược")
    assert [c["position"] for c in cards] == [0, 1, 2, 3]
    assert [c["reversed"] for c in cards] == [False, True, False, True]
    assert cards[0]["jumper"] and cards[-1]["title"] == "Queen of Cups"
    assert parse_cards("The World")[0]["suit"] == "Major"
    assert verify_tarot_spread(cards).status == "PASS"


def test_invalid_or_duplicate_entries_rejected() -> None:
    for text in ("4 pent, unknown", "4 pent, 4 pent rev", ",".join(["world"] * 13)):
        with pytest.raises(ValueError):
            parse_cards(text)
    assert parse_cards("") == []


def test_seeded_draw_and_verifier_catch_corruption() -> None:
    s1 = draw_tarot(count=3, seed=7)
    s2 = draw_tarot(count=3, seed=7)
    assert s1 == s2
    assert len(s1) == 3
    assert verify_tarot_spread(s1).status == "PASS"

    # Duplicate card must fail verification
    dup = [s1[0], s1[0]]
    assert verify_tarot_spread(dup).status == "FAIL"
    # Invented card must fail verification
    fake = [{"title": "The Dragon", "position": 1, "jumper": False, "reversed": False}]
    assert verify_tarot_spread(fake).status == "FAIL"
