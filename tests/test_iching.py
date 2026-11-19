"""Algebraic and canonical invariant tests for the I Ching Z_2^6 symbolic engine."""

import pytest

from archetype_symbolic.core.iching import (
    HEXAGRAMS_64,
    KING_WEN_INDEX,
    TRIGRAM_OBJECTS,
    analyze_hexagram,
    cast_iching,
    element_relation,
    hexagram_from_bits,
    inverted_bits,
    opposite_bits,
    transform_bits,
)
from archetype_symbolic.eval.verifiers import verify_iching_state


def test_trigram_bottom_to_top_classical_encodings() -> None:
    """Verify every trigram against classical bottom-to-top mnemonics."""
    assert len(TRIGRAM_OBJECTS) == 8
    assert TRIGRAM_OBJECTS[(1, 1, 1)].name == "Càn"   # ☰ tam liên
    assert TRIGRAM_OBJECTS[(1, 1, 0)].name == "Đoài"  # ☱ thượng khuyết (broken on top)
    assert TRIGRAM_OBJECTS[(1, 0, 1)].name == "Ly"    # ☲ trung hư (broken in middle)
    assert TRIGRAM_OBJECTS[(1, 0, 0)].name == "Chấn"  # ☳ ngưỡng bồn (solid at bottom)
    assert TRIGRAM_OBJECTS[(0, 1, 1)].name == "Tốn"   # ☴ hạ đoạn (broken at bottom)
    assert TRIGRAM_OBJECTS[(0, 1, 0)].name == "Khảm"  # ☵ trung mãn (solid in middle)
    assert TRIGRAM_OBJECTS[(0, 0, 1)].name == "Cấn"   # ☶ phúc uyển (solid on top)
    assert TRIGRAM_OBJECTS[(0, 0, 0)].name == "Khôn"  # ☷ lục đoạn


def test_hexagrams_bijection_over_z2_6() -> None:
    """Every 6-bit vector maps uniquely to one of 64 King Wen hexagrams (1..64)."""
    assert len(HEXAGRAMS_64) == 64
    assert sorted(KING_WEN_INDEX.values()) == list(range(1, 65))

    seen_numbers: set[int] = set()
    for n in range(64):
        bits = tuple((n >> i) & 1 for i in range(6))
        h = hexagram_from_bits(bits)
        seen_numbers.add(h["king_wen_number"])
        # Opposite and inverted must be involutions: f(f(x)) == x
        assert opposite_bits(opposite_bits(bits)) == bits
        assert inverted_bits(inverted_bits(bits)) == bits
    assert len(seen_numbers) == 64


def test_known_canonical_hexagrams_and_transformations() -> None:
    # Hexagram 11: Địa Thiên Thái (Upper Khôn 000, Lower Càn 111) -> bits [1,1,1,0,0,0]
    thai = analyze_hexagram([1, 1, 1, 0, 0, 0], changing_lines=[1, 6])
    assert thai["king_wen_number"] == 11
    assert thai["hexagram_name"] == "Địa Thiên Thái"
    # Nuclear of [1,1,1,0,0,0]: lower=[1,1,0] (Đoài), upper=[1,0,0] (Chấn) -> Quy Muội (#54)
    assert thai["nuclear"]["king_wen_number"] == 54
    assert thai["nuclear"]["name"] == "Lôi Trạch Quy Muội"
    # Opposite and inverted of Thái (#11) are both Thiên Địa Bĩ (#12)
    assert thai["opposite"]["king_wen_number"] == 12
    assert thai["inverted"]["king_wen_number"] == 12
    # Flip lines 1 & 6 -> [0,1,1,0,0,1] (Lower Tốn, Upper Cấn -> Sơn Phong Cổ #18)
    assert thai["transformed"] is not None
    assert thai["transformed"]["king_wen_number"] == 18
    assert thai["transformed"]["name"] == "Sơn Phong Cổ"


def test_wu_xing_element_relations() -> None:
    assert element_relation("Kim", "Thủy").startswith("Tương Sinh")
    assert element_relation("Thủy", "Kim").startswith("Được Sinh")
    assert element_relation("Kim", "Mộc").startswith("Tương Khắc")
    assert element_relation("Mộc", "Kim").startswith("Bị Khắc")
    assert element_relation("Hỏa", "Hỏa").startswith("Tỷ Hòa")


def test_seeded_cast_is_reproducible_and_verified() -> None:
    a = cast_iching("Hỏi công việc", seed=42)
    b = cast_iching("Hỏi công việc", seed=42)
    assert a == b
    assert a["visual_type"] == "iching"
    assert verify_iching_state(a).status == "PASS"

    # Mutating hexagram_name must trigger FAIL in verifier
    corrupted = dict(a, hexagram_name="Quẻ Bịa Đặt")
    res = verify_iching_state(corrupted)
    assert res.status == "FAIL"
    assert any("hexagram_name" in v for v in res.violations)


def test_invalid_inputs_rejected() -> None:
    with pytest.raises(ValueError):
        hexagram_from_bits([1, 0, 1])
    with pytest.raises(ValueError):
        transform_bits([1, 1, 1, 1, 1, 1], [7])
    with pytest.raises(ValueError):
        transform_bits([1, 1, 1, 1, 1, 1], [2, 2])
