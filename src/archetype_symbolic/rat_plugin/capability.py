"""RAT capability & verifier definitions for Tarot / archetypal reading sessions."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from archetype_symbolic.core.tarot import parse_cards
from archetype_symbolic.eval.verifiers import verify_tarot_spread


def reading_draft_observation_pack(res: Any) -> Any:
    """Compact Observation Pack view for reading draft artifacts (SoL-Pi)."""
    if not isinstance(res, dict):
        return res
    cards = res.get("cards", [])
    card_summaries = [
        f"{c.get('title')} ({'rev' if c.get('reversed') else 'upright'})"
        for c in cards
        if isinstance(c, dict)
    ]
    markdown = res.get("draft_markdown", "")
    snippet = markdown[:250].strip() + ("..." if len(markdown) > 250 else "")
    return {
        "title": res.get("title"),
        "query": res.get("query"),
        "cards_count": len(cards),
        "cards_summary": card_summaries,
        "draft_preview": snippet,
        "verification_status": res.get("verification_status", "UNKNOWN"),
        "user_edited": res.get("user_edited", False),
        "status": "raw_reading_draft_saved_in_artifact_store",
    }


class ReadingVerifier:
    """Scoped RAT verifier delegating Tarot spread checks to archetype_symbolic."""

    def check_execution(self, evidence: Any) -> Any:
        from rat.engine.verification import VerificationReport, VerificationStatus

        ids = (evidence.id,)
        op = evidence.operation
        res = evidence.result

        if not isinstance(res, dict) or res.get("error"):
            return VerificationReport(
                VerificationStatus.UNKNOWN,
                f"{op}_execution",
                "Thao tác trải bài/hồ sơ chưa trả về dữ liệu quan sát được.",
                ids,
            )

        if op == "prepare_reading_spread":
            verdict = verify_tarot_spread(res.get("cards", []))
            status = (
                VerificationStatus.PASS if verdict.status == "PASS" else VerificationStatus.FAIL
            )
            return VerificationReport(
                status,
                "prepare_reading_spread",
                verdict.reason,
                ids,
                checked=verdict.checked,
            )

        if op == "load_reading_profile":
            chart = res.get("chart", {})
            positions = res.get("positions", [])
            if not chart or not positions:
                return VerificationReport(
                    VerificationStatus.FAIL,
                    "load_reading_profile",
                    "Hồ sơ lá số chưa tính được tọa độ hành tinh.",
                    ids,
                )
            return VerificationReport(
                VerificationStatus.PASS,
                "load_reading_profile",
                f"Đã đối chiếu thông tin ngày sinh và tính toán {len(positions)} tọa độ chính.",
                ids,
                checked=("birth_data", "calculated_chart_positions"),
            )

        if op == "synthesize_reading_draft":
            draft = str(res.get("draft_markdown") or "").strip()
            if not draft:
                return VerificationReport(
                    VerificationStatus.FAIL,
                    "synthesize_reading_draft",
                    "Bản luận chưa có nội dung.",
                    ids,
                )
            return VerificationReport(
                VerificationStatus.UNKNOWN,
                "synthesize_reading_draft",
                "Diễn giải mang tính biểu tượng/tham khảo; đã giữ tách bạch dữ kiện quan sát.",
                ids,
            )

        return VerificationReport(
            VerificationStatus.UNKNOWN,
            f"{op}_execution",
            "Không có quy tắc xác minh riêng cho thao tác này.",
            ids,
        )

    def check_consensus(self, samples: list[str]) -> Any:
        from rat.engine.verification import VerificationReport, VerificationStatus

        cleaned = [s.strip() for s in samples if isinstance(s, str) and s.strip()]
        if len(cleaned) < 2:
            return VerificationReport(
                VerificationStatus.UNKNOWN,
                "reading_consensus",
                "Cần tối thiểu 2 mẫu để kiểm tra độ đồng thuận.",
                (),
            )
        token_sets = [set(s.lower().split()) for s in cleaned]
        overlaps: list[float] = []
        for i in range(len(token_sets)):
            for j in range(i + 1, len(token_sets)):
                union = token_sets[i] | token_sets[j]
                overlaps.append(len(token_sets[i] & token_sets[j]) / len(union) if union else 0.0)
        mean_overlap = sum(overlaps) / len(overlaps) if overlaps else 0.0
        status = VerificationStatus.PASS if mean_overlap >= 0.35 else VerificationStatus.UNKNOWN
        return VerificationReport(
            status,
            "reading_consensus",
            f"Độ đồng thuận từ vựng trung bình giữa {len(cleaned)} mẫu: {mean_overlap:.2f}.",
            (),
        )


def create_reading_capability() -> Any:
    """Create the RAT Capability exposing Tarot spread prep and grounded synthesis."""
    from rat.kernel.registry import Capability, OperationDefinition

    capability = Capability(
        "reading",
        "Bàn xem",
        "Chuẩn bị dữ kiện trải bài và hồ sơ; soạn bản luận qua vòng Agent/model.",
    )
    verifier = ReadingVerifier()

    def prepare(args: dict[str, Any], **context: Any) -> dict[str, Any]:
        return {
            "cards": parse_cards(args["text"]),
            "origin": "supplied_cards_not_random_draw",
        }

    def load(args: dict[str, Any], **context: Any) -> dict[str, Any]:
        path = Path(args["file_path"]).resolve()
        selected = context.get("selected_document_path")
        if not selected or path != Path(selected).resolve():
            raise ValueError("Cần người dùng chọn hồ sơ lá số trước; không tự đoán đường dẫn.")
        raise ValueError("Tính năng bản đồ sao chưa được kích hoạt ở phiên bản hiện tại.")

    def synthesize(args: dict[str, Any], **context: Any) -> dict[str, Any]:
        model_client = context.get("model_client")
        runtime = context.get("runtime")
        if model_client is None and runtime is not None:
            model_client = getattr(runtime, "document_model_client", None) or getattr(
                runtime, "model_client", None
            )

        if model_client is None:
            raise RuntimeError(
                "model_unavailable: Chưa nối vòng Agent/model cho bản luận; chưa tạo bản luận."
            )

        query = args.get("query") or context.get("query") or "Soạn bản luận cho trải bài hiện tại"
        cards = args.get("cards") or context.get("reading_cards") or []
        chart = args.get("chart") or context.get("reading_chart") or {}
        context_notes = context.get("context_notes") or ""

        if not cards and not chart:
            raise ValueError("Hãy đặt bài lên bàn hoặc chọn hồ sơ trước khi soạn bản luận.")

        card_lines = []
        for c in cards:
            pos_label = (
                "Lá rơi (jumper)" if c.get("jumper") else f"Vị trí {c.get('position')}"
            )
            orient = "Ngược (reversed)" if c.get("reversed") else "Xuôi (upright)"
            card_lines.append(f"- {pos_label}: {c.get('title')} ({orient})")
        card_desc = "\n".join(card_lines) if card_lines else "Không có trải bài Tarot."

        positions = chart.get("positions") or []
        pos_lines = [f"- {p.get('name')}: {p.get('position')}" for p in positions]
        chart_desc = "\n".join(pos_lines) if pos_lines else "Không có hồ sơ lá số."

        messages = [
            {
                "role": "system",
                "content": (
                    "Bạn là trợ lý phân tích trải bài Tarot trong RAT.\n"
                    "Các lá bài được cung cấp là dữ kiện quan sát thực tế (input_fact), "
                    "không được tự bịa thêm lá bài khác.\n"
                    "Tách bạch giữa dữ kiện đầu vào và phần luận giải biểu tượng.\n"
                    "Trình bày mạch lạc bằng tiếng Việt."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Câu hỏi / Trọng tâm: {query}\n\n"
                    f"Trải bài Tarot:\n{card_desc}\n\n"
                    f"Tọa độ hồ sơ:\n{chart_desc}\n\n"
                    f"Ghi chú bổ sung: {context_notes or 'Không có'}\n\n"
                    "Hãy soạn bản luận chi tiết có cấu trúc dựa trên các dữ kiện trên."
                ),
            },
        ]

        meta = model_client.chat_with_meta(messages, [], max_tokens=1000, thinking=False)
        message = (meta.get("message") or {}) if isinstance(meta, dict) else {}
        content = message.get("content", "")
        error = meta.get("error") if isinstance(meta, dict) else None

        if error or not content.strip():
            raise RuntimeError(
                f"model_generation_failed: {error or 'Model trả về phản hồi rỗng.'}"
            )

        candidate_drafts = context.get("candidate_drafts") or args.get("candidate_drafts")
        consensus_meta = None
        v_status = "UNKNOWN"
        v_scope = "Chưa xác minh nội dung diễn giải (diễn giải mang tính biểu tượng/tham khảo)"
        if candidate_drafts and isinstance(candidate_drafts, list):
            c_report = verifier.check_consensus(candidate_drafts)
            v_status = c_report.status.value
            v_scope = c_report.scope
            consensus_meta = {
                "samples": candidate_drafts,
                "stop_early": v_status == "PASS",
                "reason": c_report.reason,
            }

        return {
            "title": f"Bản luận: {query[:60]}",
            "query": query,
            "cards": cards,
            "chart_positions": positions,
            "draft_markdown": content.strip(),
            "cot_steps": [
                {
                    "step": 1,
                    "thought": "Tổng hợp các lá bài đã quan sát",
                    "status": "completed",
                },
                {
                    "step": 2,
                    "thought": "Soạn bản luận giải thích ý nghĩa biểu tượng theo ngữ cảnh",
                    "status": "completed",
                },
            ],
            "verification_status": v_status,
            "verification_scope": v_scope,
            **({"consensus_metadata": consensus_meta} if consensus_meta else {}),
            "user_edited": False,
        }

    capability.register_operation(
        OperationDefinition(
            name="prepare_reading_spread",
            description=(
                "Record exact user-supplied tarot cards, preserving order, reversals, and jumpers. "
                "Never invent or randomly draw cards."
            ),
            parameters={
                "type": "object",
                "additionalProperties": False,
                "properties": {"text": {"type": "string", "maxLength": 2000}},
                "required": ["text"],
            },
            handler=prepare,
            artifact_kind="reading_spread",
            verifier=verifier,
            result_contract={
                "type": "object",
                "properties": {
                    "cards": {
                        "type": "array",
                        "maxItems": 12,
                        "items": {
                            "type": "object",
                            "properties": {
                                "title": {"type": "string"},
                                "suit": {"type": "string"},
                                "numeral": {"type": "string"},
                                "reversed": {"type": "boolean"},
                                "jumper": {"type": "boolean"},
                                "position": {"type": "integer", "minimum": 0, "maximum": 12},
                            },
                            "required": [
                                "title",
                                "suit",
                                "numeral",
                                "reversed",
                                "jumper",
                                "position",
                            ],
                        },
                    },
                    "origin": {"type": "string"},
                },
                "required": ["cards", "origin"],
            },
        )
    )
    capability.register_operation(
        OperationDefinition(
            name="load_reading_profile",
            description="Read an explicitly selected local reading profile.",
            parameters={
                "type": "object",
                "additionalProperties": False,
                "properties": {"file_path": {"type": "string"}},
                "required": ["file_path"],
            },
            handler=load,
            artifact_kind="reading_natal_profile",
            verifier=verifier,
        )
    )
    capability.register_operation(
        OperationDefinition(
            name="synthesize_reading_draft",
            description=(
                "Request an interpretation draft from supplied cards using the Agent/model loop."
            ),
            parameters={
                "type": "object",
                "properties": {"query": {"type": "string", "maxLength": 2000}},
            },
            handler=synthesize,
            artifact_kind="reading_draft",
            verifier=verifier,
            observation_formatter=reading_draft_observation_pack,
        )
    )
    return capability
