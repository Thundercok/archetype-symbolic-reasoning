"""Minimal zero-dependency MCP (Model Context Protocol) stdio server.

Exposes deterministic archetypal symbolic tools over newline-delimited JSON-RPC 2.0
on stdin/stdout so external agents (RAT, Claude Code, Cursor, Antigravity) can invoke
grounded Tarot, I Ching, and Lenormand computations directly.
"""

from __future__ import annotations

import json
import sys
from collections.abc import Callable, Iterable
from typing import Any, TextIO

from archetype_symbolic import __version__
from archetype_symbolic.core.iching import analyze_hexagram, cast_iching
from archetype_symbolic.core.lenormand import draw_lenormand
from archetype_symbolic.core.tarot import draw_tarot, parse_cards
from archetype_symbolic.eval.verifiers import verify_iching_state, verify_tarot_spread

SUPPORTED_PROTOCOL_VERSIONS = ("2025-03-26", "2024-11-05")
SERVER_INFO = {"name": "archetype-symbolic-reasoning", "version": __version__}


def _tool_parse_tarot(args: dict[str, Any]) -> dict[str, Any]:
    cards = parse_cards(str(args["text"]))
    verification = verify_tarot_spread(cards).to_dict() if cards else None
    return {
        "cards": cards,
        "origin": "supplied_cards_not_random_draw",
        "verification": verification,
    }


def _tool_draw_tarot(args: dict[str, Any]) -> dict[str, Any]:
    count = int(args.get("count", 3))
    allow_reversed = bool(args.get("allow_reversed", True))
    seed = args.get("seed")
    cards = draw_tarot(
        count=count,
        allow_reversed=allow_reversed,
        seed=int(seed) if seed is not None else None,
    )
    return {
        "cards": cards,
        "origin": "seeded_draw" if seed is not None else "random_draw",
        "verification": verify_tarot_spread(cards).to_dict(),
    }


def _tool_verify_tarot(args: dict[str, Any]) -> dict[str, Any]:
    return verify_tarot_spread(args.get("cards")).to_dict()


def _tool_cast_iching(args: dict[str, Any]) -> dict[str, Any]:
    question = str(args.get("question", ""))
    seed = args.get("seed")
    return cast_iching(question=question, seed=int(seed) if seed is not None else None)


def _tool_analyze_iching(args: dict[str, Any]) -> dict[str, Any]:
    lines = list(args["lines"])
    changing = list(args.get("changing_lines") or [])
    question = str(args.get("question", ""))
    return analyze_hexagram(lines=lines, changing_lines=changing, question=question)


def _tool_verify_iching(args: dict[str, Any]) -> dict[str, Any]:
    return verify_iching_state(args.get("state") or {}).to_dict()


def _tool_draw_lenormand(args: dict[str, Any]) -> dict[str, Any]:
    question = str(args.get("question", ""))
    count = int(args.get("count", 3))
    seed = args.get("seed")
    return draw_lenormand(
        question=question,
        count=count,
        seed=int(seed) if seed is not None else None,
    )


TOOL_SPECS: list[dict[str, Any]] = [
    {
        "name": "parse_tarot_spread",
        "description": (
            "Parse exact user-supplied Tarot cards (preserving order, reversals, and jumpers) "
            "and verify uniqueness/deck membership. Never invents cards."
        ),
        "inputSchema": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "text": {"type": "string", "maxLength": 2000},
            },
            "required": ["text"],
        },
    },
    {
        "name": "draw_tarot_spread",
        "description": "Draw 1..12 distinct Tarot cards from the canonical 78-card deck.",
        "inputSchema": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "count": {"type": "integer", "minimum": 1, "maximum": 12},
                "allow_reversed": {"type": "boolean"},
                "seed": {"type": "integer"},
            },
        },
    },
    {
        "name": "verify_tarot_spread",
        "description": "Deterministically verify card titles, uniqueness, positions, and jumpers.",
        "inputSchema": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "cards": {"type": "array"},
            },
            "required": ["cards"],
        },
    },
    {
        "name": "cast_iching",
        "description": (
            "Cast an I Ching (Kinh Dịch) hexagram using the 3-coin method and compute "
            "primary, transformed (Biến), nuclear (Hỗ), opposite (Thác), and inverted states."
        ),
        "inputSchema": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "question": {"type": "string", "maxLength": 2000},
                "seed": {"type": "integer"},
            },
        },
    },
    {
        "name": "analyze_iching_hexagram",
        "description": (
            "Deterministically resolve a 6-bit bottom-to-top I Ching vector and optional "
            "1-indexed changing lines into exact King Wen, trigram, Wu Xing, and derived states."
        ),
        "inputSchema": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "lines": {
                    "type": "array",
                    "minItems": 6,
                    "maxItems": 6,
                    "items": {"type": "integer", "enum": [0, 1]},
                },
                "changing_lines": {
                    "type": "array",
                    "items": {"type": "integer", "minimum": 1, "maximum": 6},
                },
                "question": {"type": "string", "maxLength": 2000},
            },
            "required": ["lines"],
        },
    },
    {
        "name": "verify_iching_state",
        "description": (
            "Verify a claimed I Ching state dictionary against the deterministic oracle."
        ),
        "inputSchema": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "state": {"type": "object"},
            },
            "required": ["state"],
        },
    },
    {
        "name": "draw_lenormand",
        "description": "Draw 1..5 distinct cards from the traditional 36-card Lenormand deck.",
        "inputSchema": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "question": {"type": "string", "maxLength": 2000},
                "count": {"type": "integer", "minimum": 1, "maximum": 5},
                "seed": {"type": "integer"},
            },
        },
    },
]

TOOL_HANDLERS: dict[str, Callable[[dict[str, Any]], dict[str, Any]]] = {
    "parse_tarot_spread": _tool_parse_tarot,
    "draw_tarot_spread": _tool_draw_tarot,
    "verify_tarot_spread": _tool_verify_tarot,
    "cast_iching": _tool_cast_iching,
    "analyze_iching_hexagram": _tool_analyze_iching,
    "verify_iching_state": _tool_verify_iching,
    "draw_lenormand": _tool_draw_lenormand,
}


def _jsonrpc_result(req_id: Any, result: dict[str, Any]) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": req_id, "result": result}


def _jsonrpc_error(req_id: Any, code: int, message: str) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": req_id, "error": {"code": code, "message": message}}


class ArchetypeMCPServer:
    """Stateless JSON-RPC 2.0 MCP server for deterministic archetypal symbolic tools."""

    def handle_message(self, message: dict[str, Any]) -> dict[str, Any] | None:
        if not isinstance(message, dict):
            return _jsonrpc_error(None, -32600, "Invalid JSON-RPC request")

        req_id = message.get("id")
        method = message.get("method")
        params = message.get("params") or {}

        if not isinstance(method, str):
            return _jsonrpc_error(req_id, -32600, "Missing method")

        # Notifications have no id and expect no reply.
        if method.startswith("notifications/"):
            return None

        if method == "initialize":
            client_version = params.get("protocolVersion")
            negotiated = (
                client_version
                if client_version in SUPPORTED_PROTOCOL_VERSIONS
                else SUPPORTED_PROTOCOL_VERSIONS[0]
            )
            return _jsonrpc_result(
                req_id,
                {
                    "protocolVersion": negotiated,
                    "capabilities": {"tools": {"listChanged": False}},
                    "serverInfo": SERVER_INFO,
                },
            )

        if method == "ping":
            return _jsonrpc_result(req_id, {})

        if method == "tools/list":
            return _jsonrpc_result(req_id, {"tools": TOOL_SPECS})

        if method == "tools/call":
            name = params.get("name")
            arguments = params.get("arguments") or {}
            if not isinstance(name, str) or name not in TOOL_HANDLERS:
                return _jsonrpc_error(req_id, -32602, f"Unknown tool: {name!r}")
            if not isinstance(arguments, dict):
                return _jsonrpc_error(req_id, -32602, "Tool arguments must be a JSON object")
            try:
                payload = TOOL_HANDLERS[name](arguments)
                return _jsonrpc_result(
                    req_id,
                    {
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps(payload, ensure_ascii=False),
                            }
                        ],
                        "structuredContent": payload,
                        "isError": False,
                    },
                )
            except (ValueError, KeyError, TypeError) as exc:
                err_payload = {"error": str(exc)}
                return _jsonrpc_result(
                    req_id,
                    {
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps(err_payload, ensure_ascii=False),
                            }
                        ],
                        "structuredContent": err_payload,
                        "isError": True,
                    },
                )

        return _jsonrpc_error(req_id, -32601, f"Method not found: {method}")

    def serve(self, instream: Iterable[str], outstream: TextIO) -> None:
        for raw_line in instream:
            line = raw_line.strip()
            if not line:
                continue
            try:
                msg = json.loads(line)
            except json.JSONDecodeError as exc:
                resp: dict[str, Any] | None = _jsonrpc_error(None, -32700, f"Parse error: {exc}")
            else:
                resp = self.handle_message(msg)
            if resp is not None:
                outstream.write(json.dumps(resp, ensure_ascii=False) + "\n")
                outstream.flush()


def main() -> None:
    server = ArchetypeMCPServer()
    server.serve(sys.stdin, sys.stdout)


if __name__ == "__main__":
    main()
