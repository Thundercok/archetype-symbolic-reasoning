"""UI coordinator for the external ReadingDesk plugin hosted inside RAT."""

from __future__ import annotations

import copy
from typing import Any
from uuid import uuid4


class ReadingDeskCoordinator:
    """Manages Tarot/reading desk state inside RAT via the generic plugin action bridge."""

    def __init__(self, controller: Any) -> None:
        self.controller = controller
        self.cards: list[Any] = []
        self.chart: dict[str, Any] | None = None
        self.draft: dict[str, Any] = {}
        self.cot_steps: list[dict[str, Any]] = []
        self.grounds: list[dict[str, Any]] = []
        self.error: str = ""
        self.result_refs: dict[str, dict[str, Any]] = {}

    @property
    def snapshot_data(self) -> dict[str, Any]:
        smart_note = getattr(self.controller, "_smart_note_coordinator", None)
        return {
            "cards": list(self.cards),
            "chart": self.chart,
            "draft": dict(self.draft),
            "cotSteps": list(self.cot_steps),
            "grounds": list(self.grounds),
            "error": self.error,
            "resultRefs": dict(self.result_refs),
            "activeNote": (
                dict(smart_note.active_note)
                if smart_note and smart_note.active_note
                else None
            ),
            "activeNoteId": smart_note.active_note_id if smart_note else None,
            "activeNoteRevision": smart_note.active_note_revision if smart_note else 0,
        }

    def on_view_opened(self) -> None:
        ctrl = self.controller
        if hasattr(ctrl, "assistant_runtime") and ctrl.assistant_runtime:
            ctrl.assistant_runtime.load_tool_pack("divination")
        ctrl._status = "Bàn xem · bài và biểu tượng"

    def invoke_action(self, action: str, payload: dict[str, Any]) -> Any:
        if action == "set_cards":
            return self.set_cards(str(payload.get("text", "")))
        if action == "import_profile":
            return self.import_profile(str(payload.get("path", "")))
        if action == "synthesize_draft":
            return self.synthesize_draft(str(payload.get("query", "")))
        if action == "save_draft":
            return self.save_draft(str(payload.get("text", "")))
        if action == "synthesize_from_current_draft":
            return self.synthesize_from_current_draft(
                domain=str(payload.get("domain", "decision")),
                title=str(payload.get("title", "")),
            )
        raise ValueError(f"Unknown divination plugin action: {action!r}")

    def execute_reading_tool(
        self,
        name: str,
        args: dict[str, Any],
        *,
        selected_path: str | None = None,
    ) -> Any:
        from rat.engine.execution import ExecutionRequest
        from rat.engine.execution_service import AgentExecutionService

        ctrl = self.controller
        if hasattr(ctrl, "assistant_runtime") and ctrl.assistant_runtime:
            ctrl.assistant_runtime.load_tool_pack("divination")

        ctx = {
            "selected_document_path": selected_path,
            "reading_cards": list(self.cards),
            "reading_chart": copy.deepcopy(self.chart) if self.chart else None,
            "context_notes": str(
                self.draft.get("draft_markdown", "") if isinstance(self.draft, dict) else ""
            ),
        }
        req = ExecutionRequest(
            f"Thực thi {name}",
            execution_id="reading-" + uuid4().hex,
            origin="ui_action",
            requested_action={"name": name, "args": args},
            context=ctx,
        )
        resp = AgentExecutionService(ctrl.assistant_runtime).execute(req)
        if resp.error or not resp.artifacts:
            raise ValueError(resp.error or "Chưa chuẩn bị được dữ liệu phiên xem.")
        artifact = resp.artifacts[0]
        self.result_refs[name] = {"artifact_id": artifact.id, "revision": artifact.revision}
        return artifact.payload

    def set_cards(self, text: str) -> bool:
        ctrl = self.controller
        if ctrl._closed:
            return False
        try:
            result = self.execute_reading_tool("prepare_reading_spread", {"text": text})
        except ValueError as exc:
            self.error = str(exc)
            ctrl.changed.emit()
            return False
        self.cards = result["cards"]
        self.error = ""
        ctrl.changed.emit()
        return True

    def import_profile(self, path: str) -> bool:
        ctrl = self.controller
        if ctrl._closed:
            return False
        local = path.removeprefix("file://")
        try:
            result = self.execute_reading_tool(
                "load_reading_profile", {"file_path": local}, selected_path=local
            )
            self.chart = {k: v for k, v in result.items() if k != "chart"}
        except (ValueError, KeyError, TypeError, OSError) as exc:
            self.error = "Không mở được hồ sơ: " + str(exc)
            ctrl.changed.emit()
            return False
        self.error = ""
        ctrl.changed.emit()
        return True

    def synthesize_draft(self, query: str = "") -> bool:
        ctrl = self.controller
        if ctrl._closed or ctrl.snapshot["busy"]:
            return False
        if not self.cards:
            self.error = "Hãy đặt bài lên bàn trước khi soạn bản luận."
            ctrl.changed.emit()
            return False
        self.error = ""
        q = query.strip() or "Soạn bản luận cho trải bài hiện tại"
        try:
            result = self.execute_reading_tool("synthesize_reading_draft", {"query": q})
            self.draft = result
            self.cot_steps = result.get("cot_steps", [])
            self.grounds = result.get("grounds", [])
            self.error = ""
            ctrl._status = "Đã soạn bản luận có cấu trúc"
            ctrl._events.append(f"Đã soạn bản luận CoT: {result.get('title', '')}")
            ctrl.changed.emit()
            return True
        except Exception as exc:
            self.error = f"Lỗi soạn bản luận: {exc}"
            ctrl.changed.emit()
            return False

    def save_draft(self, text: str) -> bool:
        ctrl = self.controller
        if ctrl._closed or not self.draft:
            return False
        self.draft["draft_markdown"] = text
        self.draft["user_edited"] = True
        ctrl._events.append("Người dùng đã chỉnh sửa và lưu bản luận nháp")
        ctrl.changed.emit()
        return True

    def synthesize_from_current_draft(self, domain: str = "decision", title: str = "") -> str:
        ctrl = self.controller
        smart_note = getattr(ctrl, "_smart_note_coordinator", None)
        if ctrl._closed or smart_note is None:
            return ""
        if self.draft and self.draft.get("draft_markdown"):
            content = self.draft["draft_markdown"]
            note_title = title or self.draft.get("title", "Ghi chú Bàn xem")
        elif self.cards:
            parts = [
                f"{c.get('title', '')} ({'ngược' if c.get('reversed') else 'xuôi'})"
                for c in self.cards
            ]
            content = f"Dữ kiện trải bài gồm các lá: {', '.join(parts)}."
            note_title = title or "Ghi chú Trải bài"
        else:
            self.error = "Chưa có nội dung bản luận hoặc trải bài để tổng hợp ghi chú."
            ctrl.changed.emit()
            return ""
        return smart_note.synthesize_smart_note(
            raw_content=content,
            domain=domain,
            title=note_title,
            extra_context={"reading_cards": list(self.cards)},
        )
