"""One synchronous judgment after an explicit mutation; no Actor consultation."""
from dataclasses import asdict
import time
from . import providers
from .contracts import MATERIAL_MAX_CHARS, SessionRef, ToolCompleted, ToolFault
from .evidence import build_packet, verify_evidence
from .prompting import load_system_prompt
from .provider_contract import parse_feedback
from .runtime import RuntimeSettings, PROVIDER_TIMEOUT_SEC
from .storage import Journal


class NudgeCore:
    def __init__(self, settings: RuntimeSettings, *, dispatch=None, log_error=None):
        self.settings = settings
        self.dispatch = dispatch or providers.call_codex_result
        self.log_error = log_error or (lambda message: None)
        self.journal = Journal(settings.paths.data_dir)

    def start_round(self, session: SessionRef, request: str, goal: str = ""):
        self.journal.start_round(session, request, goal)

    def process_batch(self, session: SessionRef, events: tuple[ToolCompleted, ...]):
        payload = [asdict(event) for event in events]
        self.journal.record_batch(session, payload)
        judgment_payload = self.journal.events_for_judgment(
            session, payload, has_modification=any(event.modification is not None for event in events))
        if judgment_payload is None:
            return None
        events = tuple(ToolCompleted(**event) for event in judgment_payload)
        reserved = self.journal.begin(session)
        if reserved is None:
            return None
        attempt, task = reserved
        detail = {}
        try:
            if self.settings.configuration_error or self.settings.provider not in ("openai", "codex"):
                raise ToolFault("configuration", self.settings.configuration_error or "僅支援 OpenAI／Codex")
            packet = build_packet(session, task, events)
            detail["packet"] = packet.render()
            started = time.monotonic()
            run = self.dispatch(
                system_prompt=load_system_prompt(prompt_file=self.settings.paths.runtime_dir / "buddy-prompt.txt"),
                nudge_input=detail["packet"], model=self.settings.model,
                schema_path=self.settings.paths.runtime_dir / "nudge-schema.json",
                timeout_sec=PROVIDER_TIMEOUT_SEC, workspace_root=packet.workspace,
                remaining_chars=MATERIAL_MAX_CHARS - packet.material_chars,
                log_error=self.log_error,
            )
            detail.update(raw_output=run.raw_output, usage=run.usage, trace=run.trace,
                          materials=[asdict(line) for line in run.materials],
                          elapsed_seconds=time.monotonic() - started)
            feedback = parse_feedback(run.raw_output)
            if feedback is not None:
                verify_evidence(feedback, (*packet.lines, *run.materials))
            current = self.journal.finish(session, attempt, "feedback" if feedback else "silence", detail)
            if current and feedback:
                return attempt, feedback
            return None
        except Exception as exc:
            fault = exc if isinstance(exc, ToolFault) else ToolFault("internal", str(exc))
            detail["fault"] = {"kind": fault.kind, "detail": fault.detail}
            detail.update(fault.evidence)
            self.journal.finish(session, attempt, "fault", detail)
            raise fault
