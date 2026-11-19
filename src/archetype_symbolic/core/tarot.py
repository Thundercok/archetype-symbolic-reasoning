"""Deterministic 78-card Tarot deck, spread parser, and spread invariants."""

from __future__ import annotations

import random
import re
import unicodedata
from typing import Any

MAJORS: tuple[str, ...] = (
    "fool",
    "magician",
    "high priestess",
    "empress",
    "emperor",
    "hierophant",
    "lovers",
    "chariot",
    "strength",
    "hermit",
    "wheel of fortune",
    "justice",
    "hanged man",
    "death",
    "temperance",
    "devil",
    "tower",
    "star",
    "moon",
    "sun",
    "judgement",
    "world",
)

SUITS: dict[str, str] = {
    "pent": "Pentacles",
    "pentacles": "Pentacles",
    "pentacle": "Pentacles",
    "cups": "Cups",
    "cup": "Cups",
    "wands": "Wands",
    "wand": "Wands",
    "swords": "Swords",
    "sword": "Swords",
}

CANONICAL_SUITS: tuple[str, ...] = ("Wands", "Cups", "Swords", "Pentacles")

SUIT_ELEMENTS: dict[str, str] = {
    "Wands": "Fire",
    "Cups": "Water",
    "Swords": "Air",
    "Pentacles": "Earth",
    "Major": "Archetype",
}

RANKS: dict[str, str] = {
    **{str(i): str(i) for i in range(2, 11)},
    "1": "Ace",
    "a": "Ace",
    "ace": "Ace",
    "page": "Page",
    "knight": "Knight",
    "queen": "Queen",
    "king": "King",
}

CANONICAL_RANKS: tuple[str, ...] = (
    "Ace",
    "2",
    "3",
    "4",
    "5",
    "6",
    "7",
    "8",
    "9",
    "10",
    "Page",
    "Knight",
    "Queen",
    "King",
)


def _build_deck() -> tuple[dict[str, str], ...]:
    deck: list[dict[str, str]] = []
    for idx, major in enumerate(MAJORS):
        deck.append(
            {
                "title": major.title(),
                "suit": "Major",
                "numeral": str(idx),
                "element": SUIT_ELEMENTS["Major"],
            }
        )
    for suit in CANONICAL_SUITS:
        for rank in CANONICAL_RANKS:
            deck.append(
                {
                    "title": f"{rank} of {suit}",
                    "suit": suit,
                    "numeral": rank,
                    "element": SUIT_ELEMENTS[suit],
                }
            )
    return tuple(deck)


TAROT_DECK_78: tuple[dict[str, str], ...] = _build_deck()
VALID_TITLES: frozenset[str] = frozenset(card["title"] for card in TAROT_DECK_78)


def normalize_key(text: str) -> str:
    """Fold case, strip Vietnamese diacritics (including đ -> d), and normalize spaces."""
    value = unicodedata.normalize("NFD", text.casefold()).replace("đ", "d")
    return " ".join("".join(c for c in value if not unicodedata.combining(c)).split())


def parse_cards(text: str) -> list[dict[str, Any]]:
    """Parse user-supplied Tarot cards atomically, preserving order, reversals, and jumpers."""
    if len(text) > 2000:
        raise ValueError("Nhập tối đa 2.000 ký tự và 12 lá mỗi lần.")
    entries = [s.strip() for s in re.split(r"[,;\n]+", text) if s.strip()]
    if len(entries) > 12:
        raise ValueError("Bàn xem hiện hỗ trợ tối đa 12 lá.")

    result: list[dict[str, Any]] = []
    seen: set[str] = set()
    position = 0

    for raw in entries:
        value = normalize_key(raw)
        jumper = bool(re.match(r"^(?:roi|la roi|jumper)\s*:\s*", value))
        value = re.sub(r"^(?:roi|la roi|jumper)\s*:\s*", "", value)
        reversed_card = bool(re.search(r"\s+(?:rev|reversed|nguoc)$", value))
        value = re.sub(r"\s+(?:rev|reversed|nguoc|upright|xuoi)$", "", value)
        value = re.sub(r"^the\s+", "", value)
        if value == "judgment":
            value = "judgement"

        if value in MAJORS:
            title, suit = value.title(), "Major"
            numeral = str(MAJORS.index(value))
        else:
            parts = value.replace(" of ", " ").split()
            if len(parts) != 2 or parts[0] not in RANKS or parts[1] not in SUITS:
                raise ValueError(f"Chưa nhận ra “{raw}”. Ví dụ: 4 pent, 8 cups, devil rev.")
            numeral, suit = RANKS[parts[0]], SUITS[parts[1]]
            title = f"{numeral} of {suit}"

        if title in seen:
            raise ValueError(f"“{title}” đang lặp. Kiểm tra lại các lá đã nhập.")
        seen.add(title)

        if not jumper:
            position += 1
        result.append(
            {
                "title": title,
                "suit": suit,
                "numeral": numeral,
                "reversed": reversed_card,
                "jumper": jumper,
                "position": 0 if jumper else position,
            }
        )
    return result


def draw_tarot(
    count: int = 3,
    *,
    allow_reversed: bool = True,
    seed: int | None = None,
) -> list[dict[str, Any]]:
    """Draw a deterministic (when seeded) spread of distinct cards from the 78-card Tarot deck."""
    if not 1 <= count <= 12:
        raise ValueError("Spread count must be between 1 and 12.")
    rng = random.Random(seed) if seed is not None else random.SystemRandom()
    chosen = rng.sample(TAROT_DECK_78, count)
    return [
        {
            "title": card["title"],
            "suit": card["suit"],
            "numeral": card["numeral"],
            "reversed": bool(allow_reversed and rng.choice((False, True))),
            "jumper": False,
            "position": idx,
        }
        for idx, card in enumerate(chosen, start=1)
    ]
