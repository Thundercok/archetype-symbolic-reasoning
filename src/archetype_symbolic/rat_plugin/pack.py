"""RAT ToolPack entry point contributed by `archetype-symbolic-reasoning`."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from archetype_symbolic.core.iching import cast_iching
from archetype_symbolic.core.lenormand import draw_lenormand

_QML_DIR = Path(__file__).resolve().parent / "qml"

_ICHING_KEYWORDS = (
    "kinh dịch",
    "kinh dich",
    "gieo quẻ",
    "gieo que",
    "bói quẻ",
    "boi que",
    "bói dịch",
    "boi dich",
    "quẻ dịch",
    "que dich",
    "lên quẻ",
    "len que",
)

_LENORMAND_KEYWORDS = (
    "lenormand",
    "rút bài",
    "rut bai",
    "bói bài",
    "boi bai",
    "bói lenormand",
    "boi lenormand",
    "rút 3 lá",
    "rut 3 la",
)


def _handle_instant_query(query: str) -> tuple[dict[str, Any], str] | None:
    q_low = (query or "").strip().lower()
    if any(k in q_low for k in _ICHING_KEYWORDS):
        res_card = cast_iching(query)
        ch = res_card.get("changing_lines") or []
        ch_str = f" (Hào {', '.join(str(x) for x in ch)} động)" if ch else ""
        ans_text = (
            f"🔮 Quẻ Kinh Dịch #{res_card['king_wen_number']}: "
            f"{res_card['hexagram_name']}{ch_str}\n"
            f"• Thượng: {res_card['upper_trigram']} · Hạ: {res_card['lower_trigram']} "
            f"({res_card['element_relation']})\n"
            f"• Ý nghĩa: {res_card['meaning']}\n"
            f"• Lời khuyên: {res_card['advice']}"
        )
        if res_card.get("transformed"):
            t = res_card["transformed"]
            ans_text += (
                f"\n\n🔄 Quẻ Biến #{t['king_wen_number']}: {t['name']} "
                f"({t['upper']} trên {t['lower']})\n• {t['meaning']}"
            )
        return res_card, ans_text

    if any(k in q_low for k in _LENORMAND_KEYWORDS):
        res_card = draw_lenormand(query, count=3)
        lines = [
            f"{i + 1}. {c['slot']}: [{c['number']}] {c['icon']} {c['name']} — {c['meaning']}"
            for i, c in enumerate(res_card["cards"])
        ]
        ans_text = (
            "🃏 Rút 3 lá bài Lenormand:\n\n"
            + "\n".join(lines)
            + f"\n\n✨ Thông điệp: {res_card['summary']}"
        )
        return res_card, ans_text

    return None


def _make_pack_class() -> type:
    """Build DivinationToolPack inheriting from RAT's ToolPack when RAT is present."""
    try:
        from rat.plugins.manifest import ToolPack, ToolPackManifest

        base: type = ToolPack
        manifest = ToolPackManifest(
            id="divination",
            name="Bàn xem Tarot & Chiêm đoán (Archetype)",
            description=(
                "Plugin từ archetype-symbolic-reasoning: Tarot 78 lá, "
                "Kinh Dịch Z_2^6, Lenormand 36 lá và bản luận có xác minh."
            ),
            version="0.1.0",
            category="vertical",
            author="Thundercok",
            enabled_by_default=False,
            tags=["divination", "tarot", "iching", "lenormand", "neuro-symbolic"],
        )
    except ImportError:
        base = object
        manifest = None

    class _DivinationToolPack(base):  # type: ignore[valid-type, misc]
        """External RAT plugin pack supplied by archetype-symbolic-reasoning."""

        pass

    _DivinationToolPack.manifest = manifest

    def create_capabilities(self: Any, context: dict[str, Any] | None = None) -> list[Any]:
        from archetype_symbolic.rat_plugin.capability import create_reading_capability

        return [create_reading_capability()]

    def get_ui_cards(self: Any) -> list[dict[str, Any]]:
        return [
            {
                "id": "reading_desk",
                "name": "🔮 Gói mở rộng: Bàn xem Tarot...",
                "kind": "view",
                "qml": str(_QML_DIR / "ReadingDesk.qml"),
                "shortcut": "Ctrl+Shift+R",
            },
            {
                "id": "archetype_artifact_card",
                "name": "Archetype Artifact Card",
                "kind": "artifact_card",
                "qml": str(_QML_DIR / "ArchetypeArtifactCard.qml"),
                "visual_types": ["iching", "lenormand"],
            },
        ]

    def get_routing_keywords(self: Any) -> tuple[str, ...]:
        return (
            "tarot",
            "lenormand",
            "rút bài",
            "rut bai",
            "rút 3 lá",
            "rut 3 la",
            "trải bài",
            "kinh dịch",
            "kinh dich",
            "gieo quẻ",
            "gieo que",
            "lá bài",
        )

    def get_slash_commands(self: Any) -> dict[str, str]:
        return {"/reading": "reading_desk"}

    def get_instant_handlers(self: Any) -> list[Any]:
        return [_handle_instant_query]

    def create_ui_coordinator(self: Any, controller: Any) -> Any:
        from archetype_symbolic.rat_plugin.coordinator import ReadingDeskCoordinator

        return ReadingDeskCoordinator(controller)

    _DivinationToolPack.create_capabilities = create_capabilities
    _DivinationToolPack.get_ui_cards = get_ui_cards
    _DivinationToolPack.get_routing_keywords = get_routing_keywords
    _DivinationToolPack.get_slash_commands = get_slash_commands
    _DivinationToolPack.get_instant_handlers = get_instant_handlers
    _DivinationToolPack.create_ui_coordinator = create_ui_coordinator
    _DivinationToolPack.__name__ = "DivinationToolPack"
    _DivinationToolPack.__qualname__ = "DivinationToolPack"
    return _DivinationToolPack


def DivinationToolPack() -> Any:
    """Factory entry point for ``rat.plugins``."""
    return _make_pack_class()()
