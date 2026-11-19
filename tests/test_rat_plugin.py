"""Tests for the external RAT plugin entry point and instant handlers."""

from pathlib import Path

from archetype_symbolic.rat_plugin import DivinationToolPack
from archetype_symbolic.rat_plugin.pack import _handle_instant_query


def test_plugin_exposes_qml_assets_and_commands() -> None:
    pack = DivinationToolPack()
    cards = pack.get_ui_cards()
    assert len(cards) == 2
    for card in cards:
        assert Path(card["qml"]).is_file(), f"Missing QML asset: {card['qml']}"
    assert pack.get_slash_commands() == {"/reading": "reading_desk"}
    assert "tarot" in pack.get_routing_keywords()


def test_instant_query_handlers_iching_and_lenormand() -> None:
    iching_res = _handle_instant_query("gieo quẻ kinh dịch hôm nay")
    assert iching_res is not None
    card, text = iching_res
    assert card["visual_type"] == "iching"
    assert "Kinh Dịch" in text

    leno_res = _handle_instant_query("rút 3 lá bài lenormand")
    assert leno_res is not None
    l_card, l_text = leno_res
    assert l_card["visual_type"] == "lenormand"
    assert "Lenormand" in l_text

    assert _handle_instant_query("thời khóa biểu thứ hai") is None
