"""End-to-end JSON-RPC 2.0 tests for the MCP stdio server."""

import io
import json

from archetype_symbolic.mcp_server import ArchetypeMCPServer


def _roundtrip(messages: list[dict]) -> list[dict]:
    server = ArchetypeMCPServer()
    instream = io.StringIO("\n".join(json.dumps(m) for m in messages) + "\n")
    outstream = io.StringIO()
    server.serve(instream, outstream)
    return [json.loads(line) for line in outstream.getvalue().splitlines() if line.strip()]


def test_mcp_initialize_list_and_tool_calls() -> None:
    responses = _roundtrip(
        [
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {"protocolVersion": "2025-03-26"},
            },
            {"jsonrpc": "2.0", "method": "notifications/initialized"},
            {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
            {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {
                    "name": "parse_tarot_spread",
                    "arguments": {"text": "rơi: 9 pent; world rev"},
                },
            },
            {
                "jsonrpc": "2.0",
                "id": 4,
                "method": "tools/call",
                "params": {
                    "name": "analyze_iching_hexagram",
                    "arguments": {"lines": [1, 1, 1, 0, 0, 0], "changing_lines": [1, 6]},
                },
            },
            {
                "jsonrpc": "2.0",
                "id": 5,
                "method": "tools/call",
                "params": {"name": "draw_lenormand", "arguments": {"count": 3, "seed": 9}},
            },
        ]
    )

    assert len(responses) == 5  # notification produces no response
    assert responses[0]["result"]["serverInfo"]["name"] == "archetype-symbolic-reasoning"

    tool_names = {t["name"] for t in responses[1]["result"]["tools"]}
    assert {
        "parse_tarot_spread",
        "draw_tarot_spread",
        "verify_tarot_spread",
        "cast_iching",
        "analyze_iching_hexagram",
        "verify_iching_state",
        "draw_lenormand",
    }.issubset(tool_names)

    tarot_payload = responses[2]["result"]["structuredContent"]
    assert responses[2]["result"]["isError"] is False
    assert tarot_payload["cards"][0]["jumper"] is True
    assert tarot_payload["cards"][1]["title"] == "World"
    assert tarot_payload["cards"][1]["reversed"] is True
    assert tarot_payload["verification"]["status"] == "PASS"

    iching_payload = responses[3]["result"]["structuredContent"]
    assert iching_payload["king_wen_number"] == 11
    assert iching_payload["transformed"]["king_wen_number"] == 18

    lenormand_payload = responses[4]["result"]["structuredContent"]
    assert len(lenormand_payload["cards"]) == 3


def test_mcp_tool_validation_error_returns_structured_is_error() -> None:
    responses = _roundtrip(
        [
            {
                "jsonrpc": "2.0",
                "id": 10,
                "method": "tools/call",
                "params": {
                    "name": "parse_tarot_spread",
                    "arguments": {"text": "4 pent, 4 pent rev"},
                },
            }
        ]
    )
    assert responses[0]["result"]["isError"] is True
    assert "lặp" in responses[0]["result"]["structuredContent"]["error"]
