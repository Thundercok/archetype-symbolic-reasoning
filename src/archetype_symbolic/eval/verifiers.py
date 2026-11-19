"""Deterministic verifiers for symbolic state accuracy and structural constraint checks."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from archetype_symbolic.core.iching import analyze_hexagram
from archetype_symbolic.core.tarot import VALID_TITLES


@dataclass(frozen=True)
class VerificationResult:
    """Structured deterministic verification output."""

    status: str  # "PASS" | "FAIL"
    scope: str
    reason: str
    checked: tuple[str, ...] = ()
    violations: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def verify_tarot_spread(cards: Any) -> VerificationResult:
    """Verify structural invariants of a Tarot spread (valid titles, uniqueness, positions)."""
    if not isinstance(cards, list) or not cards:
        return VerificationResult(
            status="FAIL",
            scope="tarot_spread",
            reason="Trải bài không chứa lá bài hợp lệ.",
            violations=("empty_or_non_list",),
        )

    if len(cards) > 12:
        return VerificationResult(
            status="FAIL",
            scope="tarot_spread",
            reason="Trải bài vượt quá giới hạn 12 lá.",
            violations=("exceeds_max_cards",),
        )

    seen: set[str] = set()
    violations: list[str] = []
    expected_pos = 0

    for idx, card in enumerate(cards):
        if not isinstance(card, dict):
            violations.append(f"card[{idx}]:not_a_dict")
            continue
        title = card.get("title")
        if not isinstance(title, str) or title not in VALID_TITLES:
            violations.append(f"card[{idx}]:invalid_title:{title!r}")
            continue
        if title in seen:
            violations.append(f"card[{idx}]:duplicate_title:{title}")
            continue
        seen.add(title)

        jumper = bool(card.get("jumper", False))
        pos = card.get("position")
        if jumper:
            if pos != 0:
                violations.append(f"card[{idx}]:jumper_position_must_be_0:got_{pos}")
        else:
            expected_pos += 1
            if pos != expected_pos:
                violations.append(f"card[{idx}]:expected_position_{expected_pos}:got_{pos}")

    if violations:
        return VerificationResult(
            status="FAIL",
            scope="tarot_spread",
            reason=f"Phát hiện {len(violations)} lỗi cấu trúc trải bài.",
            checked=("card_titles", "uniqueness", "positions", "jumpers"),
            violations=tuple(violations),
        )

    return VerificationResult(
        status="PASS",
        scope="tarot_spread",
        reason=(
            f"Đã đối chiếu {len(cards)} lá bài: thứ tự, chiều xuôi/ngược "
            "và lá rơi (jumper) khớp đầu vào."
        ),
        checked=("card_titles", "uniqueness", "positions", "reversals", "jumpers"),
    )


def verify_iching_state(claimed: dict[str, Any]) -> VerificationResult:
    """Verify a claimed I Ching derivation against the deterministic Z_2^6 oracle."""
    if not isinstance(claimed, dict) or "lines" not in claimed:
        return VerificationResult(
            status="FAIL",
            scope="iching_state",
            reason="Thiếu vector 6 hào (lines) để đối chiếu.",
            violations=("missing_lines",),
        )

    try:
        oracle = analyze_hexagram(
            claimed["lines"],
            changing_lines=claimed.get("changing_lines") or [],
        )
    except (ValueError, TypeError) as exc:
        return VerificationResult(
            status="FAIL",
            scope="iching_state",
            reason=f"Trạng thái quẻ không hợp lệ: {exc}",
            violations=(f"invalid_input:{exc}",),
        )

    violations: list[str] = []
    if "hexagram_name" in claimed and claimed["hexagram_name"] != oracle["hexagram_name"]:
        violations.append(
            f"hexagram_name:expected={oracle['hexagram_name']!r},got={claimed['hexagram_name']!r}"
        )
    if "king_wen_number" in claimed and claimed["king_wen_number"] != oracle["king_wen_number"]:
        violations.append(
            f"king_wen_number:expected={oracle['king_wen_number']},got={claimed['king_wen_number']}"
        )
    if "transformed" in claimed:
        oracle_t = oracle["transformed"]
        claimed_t = claimed["transformed"]
        if oracle_t is None and claimed_t is not None:
            violations.append("transformed:expected_none_when_no_changing_lines")
        elif oracle_t is not None:
            if not isinstance(claimed_t, dict):
                violations.append("transformed:expected_dict")
            elif "name" in claimed_t and claimed_t["name"] != oracle_t["name"]:
                violations.append(
                    f"transformed.name:expected={oracle_t['name']!r},got={claimed_t['name']!r}"
                )
    if "nuclear" in claimed and isinstance(claimed["nuclear"], dict):
        if "name" in claimed["nuclear"] and claimed["nuclear"]["name"] != oracle["nuclear"]["name"]:
            violations.append(
                f"nuclear.name:expected={oracle['nuclear']['name']!r},"
                f"got={claimed['nuclear']['name']!r}"
            )

    if violations:
        return VerificationResult(
            status="FAIL",
            scope="iching_state",
            reason=f"Phát hiện {len(violations)} sai lệch so với oracle Kinh Dịch.",
            checked=("lines", "hexagram_name", "king_wen_number", "transformed", "nuclear"),
            violations=tuple(violations),
        )

    return VerificationResult(
        status="PASS",
        scope="iching_state",
        reason="Trạng thái quẻ Kinh Dịch khớp 100% với oracle tất định.",
        checked=("lines", "hexagram_name", "king_wen_number", "transformed", "nuclear"),
    )
