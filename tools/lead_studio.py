from __future__ import annotations

import json
import os
import smtplib
import ssl
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from email.mime.text import MIMEText
from email.utils import formatdate
from pathlib import Path
from typing import Any, Callable, Iterator, Optional

from hermes_constants import get_hermes_dir


STAGE_SEQUENCE = (
    "scouted",
    "diagnosed",
    "built",
    "filmed",
    "pitched",
    "checked",
    "approval_requested",
    "operator_approved",
    "approval_rejected",
    "revision_requested",
    "demo_built",
    "demo_checked",
    "customer_sent",
    "outreach_blocked",
)

STAGE_OWNER_ROLES = {
    "scouted": "scout",
    "diagnosed": "diagnoser",
    "built": "builder",
    "filmed": "filmer",
    "pitched": "pitcher",
    "checked": "checker",
}

_ALLOWED_PREVIOUS_STATE = {
    "scouted": None,
    "diagnosed": "scouted",
    "built": "diagnosed",
    "filmed": "built",
    "pitched": "filmed",
    "checked": "pitched",
    "approval_requested": "checked",
}

_REJECTABLE_STAGES = {"diagnosed", "checked"}


class LeadStudioError(RuntimeError):
    """Base workflow error."""


class StageOrderError(LeadStudioError):
    """Raised when a stage transition violates the fixed workflow order."""


class OwnershipConflictError(LeadStudioError):
    """Raised when another agent currently owns the lead lock."""


class LeadRejectedError(LeadStudioError):
    """Raised when a rejected lead is asked to continue."""


class ApprovalDispatchError(LeadStudioError):
    """Raised when the Telegram approval request fails to send."""

class CustomerOutreachError(LeadStudioError):
    """Raised when approved customer outreach fails to send."""


@dataclass(frozen=True)
class LeadSnapshot:
    lead_id: str
    current_state: Optional[str]
    rejected_at: Optional[str]
    rejection_reason: Optional[str]
    approval_requested: bool
    operator_approved: bool
    approval_rejected: bool
    revision_requested: bool
    demo_built: bool
    demo_checked: bool
    customer_sent: bool
    outreach_blocked: bool
    events: list[dict[str, Any]]
    stage_payloads: dict[str, dict[str, Any]]

    @property
    def completed_stages(self) -> list[str]:
        return [event["state"] for event in self.events if event.get("kind") == "stage_completed"]

    @property
    def is_rejected(self) -> bool:
        return self.rejected_at is not None


class TelegramApprovalDispatcher:
    """Send the final approval request through Hermes' existing send_message path."""

    def __init__(
        self,
        target: str = "telegram",
        send_tool: Optional[Callable[[dict[str, Any]], Any]] = None,
    ) -> None:
        self.target = target
        self._send_tool = send_tool or self._default_send_tool

    @staticmethod
    def _default_send_tool(args: dict[str, Any]) -> Any:
        from tools.send_message_tool import send_message_tool

        return send_message_tool(args)

    def build_message(self, snapshot: LeadSnapshot) -> str:
        scouted = snapshot.stage_payloads.get("scouted", {})
        diagnosed = snapshot.stage_payloads.get("diagnosed", {})
        built = snapshot.stage_payloads.get("built", {})
        filmed = snapshot.stage_payloads.get("filmed", {})
        pitched = snapshot.stage_payloads.get("pitched", {})
        checked = snapshot.stage_payloads.get("checked", {})

        business_name = scouted.get("business_name", snapshot.lead_id)
        category = scouted.get("category", "unknown category")
        neighborhood = diagnosed.get("neighborhood") or diagnosed.get("borough") or "NYC"
        opportunity = built.get("opportunity_summary", "Opportunity summary unavailable.")
        why_now = built.get("why_it_matters", "Value rationale unavailable.")
        evidence = filmed.get("evidence", [])
        evidence_line = ", ".join(evidence[:3]) if evidence else "no evidence listed"
        pitch = pitched.get("pitch_text", "Pitch draft unavailable.")
        checker_note = checked.get("checker_note", "Ready for review.")

        return (
            "Lead Studio approval request\n\n"
            f"Lead: {business_name} ({category})\n"
            f"Location: {neighborhood}\n"
            f"Lead ID: {snapshot.lead_id}\n\n"
            f"Opportunity: {opportunity}\n"
            f"Why it is worth doing: {why_now}\n"
            f"Evidence: {evidence_line}\n\n"
            f"Pitch:\n{pitch}\n\n"
            f"Checker note: {checker_note}\n\n"
            "Reply with one of: APPROVE / REJECT / REVISE"
        )

    def request_approval(self, snapshot: LeadSnapshot) -> dict[str, Any]:
        message = self.build_message(snapshot)
        result = self._send_tool(
            {
                "action": "send",
                "target": self.target,
                "message": message,
            }
        )
        if isinstance(result, str):
            try:
                result = json.loads(result)
            except json.JSONDecodeError as exc:
                raise ApprovalDispatchError(
                    "send_message returned a non-JSON response for Telegram approval dispatch"
                ) from exc
        if isinstance(result, dict) and result.get("success") is False:
            raise ApprovalDispatchError(result.get("error") or "send_message reported success=false")
        if isinstance(result, dict) and result.get("error"):
            raise ApprovalDispatchError(result["error"])
        if not isinstance(result, dict):
            raise ApprovalDispatchError(
                f"Unexpected send_message result type: {type(result).__name__}"
            )
        return {
            "target": self.target,
            "message": message,
            "result": result,
        }


class CustomerOutreachDispatcher:
    """Send approved customer pitch/build outreach and return a durable receipt payload."""

    def __init__(
        self,
        default_cc: Optional[list[str]] = None,
        smtp_send_fn: Optional[Callable[[dict[str, Any]], dict[str, Any]]] = None,
    ) -> None:
        self.default_cc = list(default_cc or ["hodlceo.eth@gmail.com"])
        self._smtp_send_fn = smtp_send_fn or self._send_email

    def build_email_body(self, snapshot: LeadSnapshot, payload: dict[str, Any]) -> str:
        scouted = snapshot.stage_payloads.get("scouted", {})
        built = snapshot.stage_payloads.get("built", {})
        pitched = snapshot.stage_payloads.get("pitched", {})
        filmed = snapshot.stage_payloads.get("filmed", {})
        business_name = scouted.get("business_name", snapshot.lead_id)
        pitch_text = payload.get("pitch_text") or pitched.get("pitch_text") or ""
        demo_url = self._demo_url(snapshot, payload)
        build_summary = payload.get("build_summary") or built.get("opportunity_summary") or ""
        work_scope = payload.get("work_scope") or built.get("work_scope") or []
        evidence = payload.get("evidence") or filmed.get("evidence") or []

        if isinstance(work_scope, list):
            scope_text = "\n".join(f"- {item}" for item in work_scope[:8])
        else:
            scope_text = str(work_scope)
        evidence_lines = []
        if isinstance(evidence, list):
            for item in evidence[:5]:
                if isinstance(item, dict):
                    evidence_lines.append(item.get("summary") or item.get("evidence") or item.get("implication") or json.dumps(item, sort_keys=True))
                else:
                    evidence_lines.append(str(item))
        elif evidence:
            evidence_lines.append(str(evidence))
        evidence_text = "\n".join(f"- {line}" for line in evidence_lines)

        parts = [
            f"Hi {business_name} team,",
            "",
            pitch_text,
            "",
            "Build opportunity:",
            build_summary,
        ]
        if scope_text:
            parts.extend(["", "Suggested scope:", scope_text])
        if evidence_text:
            parts.extend(["", "Why this is grounded:", evidence_text])
        if demo_url:
            parts.extend(["", "Preview link:", demo_url])
        parts.extend([
            "",
            "If helpful, we'd be glad to walk through the tighter homepage / conversion-path concept.",
            "",
            "- HODLHQ",
        ])
        return "\n".join(parts).strip() + "\n"

    def _demo_url(self, snapshot: LeadSnapshot, payload: dict[str, Any]) -> str:
        candidate = (
            payload.get("demo_url")
            or payload.get("demo_link")
            or payload.get("build_url")
            or snapshot.stage_payloads.get("demo_checked", {}).get("demo_url")
            or snapshot.stage_payloads.get("demo_built", {}).get("demo_url")
        )
        return str(candidate or "").strip()

    def send_outreach(self, snapshot: LeadSnapshot, payload: dict[str, Any]) -> dict[str, Any]:
        demo_url = self._demo_url(snapshot, payload)
        if not demo_url:
            raise CustomerOutreachError("Customer outreach requires a reviewable demo_url/build_url")
        channel = str(payload.get("channel") or "email").lower()
        if channel != "email":
            result = payload.get("delivery_result") or {"success": True, "platform": channel, "mode": "record_only"}
            return {
                "channel": channel,
                "recipient": payload.get("recipient") or payload.get("contact"),
                "cc": payload.get("cc") or [],
                "subject": payload.get("subject"),
                "message": payload.get("message") or payload.get("pitch_text"),
                "demo_url": demo_url,
                "result": result,
            }

        recipient = str(payload.get("recipient") or payload.get("to") or "").strip()
        if not recipient:
            raise CustomerOutreachError("Email outreach requires a recipient/to address")
        cc = list(payload.get("cc") or self.default_cc)
        subject = payload.get("subject") or f"Website clarity idea for {snapshot.stage_payloads.get('scouted', {}).get('business_name', snapshot.lead_id)}"
        message = payload.get("message") or self.build_email_body(snapshot, payload)
        result = self._smtp_send_fn({"to": recipient, "cc": cc, "subject": subject, "message": message})
        if isinstance(result, dict) and result.get("success") is False:
            raise CustomerOutreachError(result.get("error") or "email outreach reported success=false")
        if isinstance(result, dict) and result.get("error"):
            raise CustomerOutreachError(result["error"])
        if not isinstance(result, dict):
            raise CustomerOutreachError(f"Unexpected email outreach result type: {type(result).__name__}")
        return {
            "channel": "email",
            "recipient": recipient,
            "cc": cc,
            "subject": subject,
            "message": message,
            "demo_url": demo_url,
            "result": result,
        }

    @staticmethod
    def _send_email(args: dict[str, Any]) -> dict[str, Any]:
        address = os.getenv("EMAIL_ADDRESS", "")
        password = os.getenv("EMAIL_PASSWORD", "")
        smtp_host = os.getenv("EMAIL_SMTP_HOST", "")
        try:
            from gateway.config import Platform, load_gateway_config

            pconfig = load_gateway_config().platforms.get(Platform.EMAIL)
            if pconfig and pconfig.enabled:
                address = address or pconfig.extra.get("address", "")
                smtp_host = smtp_host or pconfig.extra.get("smtp_host", "")
        except Exception:
            pass
        smtp_port = int(os.getenv("EMAIL_SMTP_PORT", "587") or "587")
        if not all([address, password, smtp_host]):
            return {"error": "Email not configured (EMAIL_ADDRESS, EMAIL_PASSWORD, EMAIL_SMTP_HOST required)"}

        to_addr = args["to"]
        cc_addrs = list(args.get("cc") or [])
        msg = MIMEText(args["message"], "plain", "utf-8")
        msg["From"] = address
        msg["To"] = to_addr
        if cc_addrs:
            msg["Cc"] = ", ".join(cc_addrs)
        msg["Subject"] = args["subject"]
        msg["Date"] = formatdate(localtime=True)

        recipients = [to_addr, *cc_addrs]
        try:
            with smtplib.SMTP(smtp_host, smtp_port) as server:
                server.starttls(context=ssl.create_default_context())
                server.login(address, password)
                server.send_message(msg, from_addr=address, to_addrs=recipients)
            return {"success": True, "platform": "email", "to": to_addr, "cc": cc_addrs}
        except Exception as exc:
            return {"error": f"Email outreach failed: {exc}"}


class LeadStudioStore:
    """Append-only lead workflow store under HERMES_HOME."""

    def __init__(
        self,
        root: Optional[Path] = None,
        now_fn: Optional[Callable[[], datetime]] = None,
        lock_timeout_seconds: int = 900,
    ) -> None:
        self.root = Path(root) if root is not None else get_hermes_dir("workflows/lead_studio", "lead_studio")
        self._now_fn = now_fn or (lambda: datetime.now(timezone.utc))
        self.lock_timeout_seconds = max(int(lock_timeout_seconds), 0)
        self.root.mkdir(parents=True, exist_ok=True)
        (self.root / "leads").mkdir(parents=True, exist_ok=True)

    def _parse_iso_datetime(self, value: str) -> Optional[datetime]:
        if not value:
            return None
        try:
            parsed = datetime.fromisoformat(value)
        except ValueError:
            return None
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed

    def _lock_is_stale(self, existing: dict[str, Any]) -> bool:
        if self.lock_timeout_seconds <= 0:
            return False
        claimed_at = self._parse_iso_datetime(str(existing.get("claimed_at") or ""))
        if claimed_at is None:
            return False
        age_seconds = (self._now() - claimed_at).total_seconds()
        return age_seconds > self.lock_timeout_seconds

    def lead_dir(self, lead_id: str) -> Path:
        return self.root / "leads" / lead_id

    def artifacts_dir(self, lead_id: str) -> Path:
        return self.lead_dir(lead_id) / "artifacts"

    def events_path(self, lead_id: str) -> Path:
        return self.lead_dir(lead_id) / "events.jsonl"

    def lock_path(self, lead_id: str) -> Path:
        return self.lead_dir(lead_id) / ".owner.lock"

    def _now(self) -> datetime:
        return self._now_fn()

    def _timestamp(self) -> str:
        return self._now().strftime("%Y%m%dT%H%M%S%fZ")

    def _ensure_lead_dirs(self, lead_id: str) -> None:
        self.artifacts_dir(lead_id).mkdir(parents=True, exist_ok=True)

    def _load_events(self, lead_id: str) -> list[dict[str, Any]]:
        path = self.events_path(lead_id)
        if not path.exists():
            return []
        events: list[dict[str, Any]] = []
        for raw_line in path.read_text(encoding="utf-8").splitlines():
            if not raw_line.strip():
                continue
            events.append(json.loads(raw_line))
        return events

    def _append_event(self, lead_id: str, event: dict[str, Any]) -> None:
        self._ensure_lead_dirs(lead_id)
        with self.events_path(lead_id).open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(event, sort_keys=True) + "\n")

    def _write_artifact(self, lead_id: str, stage_state: str, payload: dict[str, Any]) -> str:
        self._ensure_lead_dirs(lead_id)
        filename = f"{self._timestamp()}__{stage_state}.json"
        path = self.artifacts_dir(lead_id) / filename
        path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return str(path)

    @contextmanager
    def claim(self, lead_id: str, owner_id: str, owner_role: str) -> Iterator[dict[str, str]]:
        self._ensure_lead_dirs(lead_id)
        lock_path = self.lock_path(lead_id)
        payload = {
            "lead_id": lead_id,
            "owner_id": owner_id,
            "owner_role": owner_role,
            "claimed_at": self._now().isoformat(),
        }
        flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY
        while True:
            try:
                fd = os.open(lock_path, flags)
                break
            except FileExistsError as exc:
                existing = {}
                try:
                    existing = json.loads(lock_path.read_text(encoding="utf-8"))
                except Exception:
                    existing = {"raw": lock_path.read_text(encoding="utf-8", errors="ignore")}
                if self._lock_is_stale(existing):
                    try:
                        lock_path.unlink()
                        continue
                    except FileNotFoundError:
                        continue
                raise OwnershipConflictError(
                    f"Lead {lead_id} is already owned by {existing.get('owner_id', 'unknown')}"
                ) from exc
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as fh:
                json.dump(payload, fh, sort_keys=True)
            yield payload
        finally:
            try:
                lock_path.unlink()
            except FileNotFoundError:
                pass

    def load_snapshot(self, lead_id: str) -> LeadSnapshot:
        events = self._load_events(lead_id)
        current_state: Optional[str] = None
        rejected_at: Optional[str] = None
        rejection_reason: Optional[str] = None
        approval_requested = False
        operator_approved = False
        approval_rejected = False
        revision_requested = False
        demo_built = False
        demo_checked = False
        customer_sent = False
        outreach_blocked = False
        stage_payloads: dict[str, dict[str, Any]] = {}

        for event in events:
            kind = event.get("kind")
            if kind == "stage_completed":
                state = event["state"]
                payload = dict(event.get("payload") or {})
                stage_payloads[state] = payload
                current_state = state
                if payload.get("decision") == "rejected":
                    rejected_at = state
                    rejection_reason = payload.get("rejection_reason") or payload.get("checker_note")
            elif kind == "approval_requested":
                approval_requested = True
                current_state = "approval_requested"
                stage_payloads["approval_requested"] = dict(event.get("payload") or {})
            elif kind == "operator_approved":
                operator_approved = True
                current_state = "operator_approved"
                stage_payloads["operator_approved"] = dict(event.get("payload") or {})
            elif kind == "approval_rejected":
                approval_rejected = True
                current_state = "approval_rejected"
                stage_payloads["approval_rejected"] = dict(event.get("payload") or {})
            elif kind == "revision_requested":
                revision_requested = True
                current_state = "revision_requested"
                stage_payloads["revision_requested"] = dict(event.get("payload") or {})
            elif kind == "demo_built":
                demo_built = True
                current_state = "demo_built"
                stage_payloads["demo_built"] = dict(event.get("payload") or {})
            elif kind == "demo_checked":
                demo_checked = True
                current_state = "demo_checked"
                stage_payloads["demo_checked"] = dict(event.get("payload") or {})
            elif kind == "customer_sent":
                customer_sent = True
                current_state = "customer_sent"
                stage_payloads["customer_sent"] = dict(event.get("payload") or {})
            elif kind == "outreach_blocked":
                outreach_blocked = True
                current_state = "outreach_blocked"
                stage_payloads["outreach_blocked"] = dict(event.get("payload") or {})

        return LeadSnapshot(
            lead_id=lead_id,
            current_state=current_state,
            rejected_at=rejected_at,
            rejection_reason=rejection_reason,
            approval_requested=approval_requested,
            operator_approved=operator_approved,
            approval_rejected=approval_rejected,
            revision_requested=revision_requested,
            demo_built=demo_built,
            demo_checked=demo_checked,
            customer_sent=customer_sent,
            outreach_blocked=outreach_blocked,
            events=events,
            stage_payloads=stage_payloads,
        )

    def _validate_transition(self, snapshot: LeadSnapshot, next_state: str, payload: dict[str, Any]) -> None:
        if snapshot.approval_requested:
            raise StageOrderError(f"Lead {snapshot.lead_id} already reached approval_requested")
        if snapshot.is_rejected:
            raise LeadRejectedError(
                f"Lead {snapshot.lead_id} was rejected at {snapshot.rejected_at}: {snapshot.rejection_reason or 'no reason provided'}"
            )
        expected_previous = _ALLOWED_PREVIOUS_STATE[next_state]
        if snapshot.current_state != expected_previous:
            raise StageOrderError(
                f"Lead {snapshot.lead_id} cannot move to {next_state} from {snapshot.current_state}; expected {expected_previous}"
            )
        if payload.get("decision") == "rejected" and next_state not in _REJECTABLE_STAGES:
            raise StageOrderError(f"Only diagnosed or checked may reject a lead, not {next_state}")

    def record_stage(self, lead_id: str, stage_state: str, owner_id: str, payload: dict[str, Any]) -> LeadSnapshot:
        snapshot = self.load_snapshot(lead_id)
        self._validate_transition(snapshot, stage_state, payload)
        artifact_payload = {
            **payload,
            "lead_id": lead_id,
            "owner_id": owner_id,
            "owner_role": STAGE_OWNER_ROLES[stage_state],
            "recorded_at": self._now().isoformat(),
        }
        artifact_path = self._write_artifact(lead_id, stage_state, artifact_payload)
        self._append_event(
            lead_id,
            {
                "kind": "stage_completed",
                "state": stage_state,
                "owner_id": owner_id,
                "recorded_at": self._now().isoformat(),
                "artifact_path": artifact_path,
                "payload": artifact_payload,
            },
        )
        return self.load_snapshot(lead_id)

    def record_approval_request(self, lead_id: str, owner_id: str, dispatch: dict[str, Any]) -> LeadSnapshot:
        snapshot = self.load_snapshot(lead_id)
        if snapshot.current_state != "checked":
            raise StageOrderError(
                f"Lead {lead_id} cannot request approval from {snapshot.current_state}; expected checked"
            )
        if snapshot.is_rejected:
            raise LeadRejectedError(
                f"Lead {lead_id} was rejected at {snapshot.rejected_at}: {snapshot.rejection_reason or 'no reason provided'}"
            )
        artifact_payload = {
            **dispatch,
            "lead_id": lead_id,
            "owner_id": owner_id,
            "owner_role": "checker",
            "recorded_at": self._now().isoformat(),
        }
        artifact_path = self._write_artifact(lead_id, "approval_requested", artifact_payload)
        self._append_event(
            lead_id,
            {
                "kind": "approval_requested",
                "state": "approval_requested",
                "owner_id": owner_id,
                "recorded_at": self._now().isoformat(),
                "artifact_path": artifact_path,
                "payload": artifact_payload,
            },
        )
        return self.load_snapshot(lead_id)

    def record_dispatch_attempt(self, lead_id: str, owner_id: str, target: str) -> None:
        snapshot = self.load_snapshot(lead_id)
        if snapshot.current_state != "checked":
            raise StageOrderError(
                f"Lead {lead_id} cannot dispatch approval from {snapshot.current_state}; expected checked"
            )
        self._append_event(
            lead_id,
            {
                "kind": "approval_dispatch_attempted",
                "state": "checked",
                "owner_id": owner_id,
                "recorded_at": self._now().isoformat(),
                "payload": {
                    "lead_id": lead_id,
                    "owner_id": owner_id,
                    "owner_role": "checker",
                    "target": target,
                },
            },
        )

    def record_operator_decision(self, lead_id: str, owner_id: str, decision: str, payload: Optional[dict[str, Any]] = None) -> LeadSnapshot:
        snapshot = self.load_snapshot(lead_id)
        if snapshot.current_state != "approval_requested":
            raise StageOrderError(
                f"Lead {lead_id} cannot record operator decision from {snapshot.current_state}; expected approval_requested"
            )
        normalized = decision.strip().lower()
        kind_by_decision = {
            "approve": "operator_approved",
            "approved": "operator_approved",
            "reject": "approval_rejected",
            "rejected": "approval_rejected",
            "revise": "revision_requested",
            "revision_requested": "revision_requested",
        }
        kind = kind_by_decision.get(normalized)
        if kind is None:
            raise StageOrderError(f"Unsupported operator approval decision: {decision}")
        artifact_payload = {
            **(payload or {}),
            "lead_id": lead_id,
            "owner_id": owner_id,
            "owner_role": "operator",
            "decision": kind,
            "decided_at": self._now().isoformat(),
            "recorded_at": self._now().isoformat(),
        }
        artifact_path = self._write_artifact(lead_id, kind, artifact_payload)
        self._append_event(
            lead_id,
            {
                "kind": kind,
                "state": kind,
                "owner_id": owner_id,
                "recorded_at": self._now().isoformat(),
                "artifact_path": artifact_path,
                "payload": artifact_payload,
            },
        )
        return self.load_snapshot(lead_id)


    def record_demo_built(self, lead_id: str, owner_id: str, payload: dict[str, Any]) -> LeadSnapshot:
        snapshot = self.load_snapshot(lead_id)
        if snapshot.current_state not in {"operator_approved", "outreach_blocked"}:
            raise StageOrderError(
                f"Lead {lead_id} cannot record demo_built from {snapshot.current_state}; expected operator_approved or outreach_blocked"
            )
        demo_url = str(payload.get("demo_url") or payload.get("demo_link") or payload.get("build_url") or "").strip()
        if not demo_url:
            raise StageOrderError("demo_built requires a reviewable demo_url/build_url")
        artifact_payload = {
            **payload,
            "demo_url": demo_url,
            "lead_id": lead_id,
            "owner_id": owner_id,
            "owner_role": "demo_builder",
            "built_at": self._now().isoformat(),
            "recorded_at": self._now().isoformat(),
        }
        artifact_path = self._write_artifact(lead_id, "demo_built", artifact_payload)
        self._append_event(
            lead_id,
            {
                "kind": "demo_built",
                "state": "demo_built",
                "owner_id": owner_id,
                "recorded_at": self._now().isoformat(),
                "artifact_path": artifact_path,
                "payload": artifact_payload,
            },
        )
        return self.load_snapshot(lead_id)

    def record_demo_checked(self, lead_id: str, owner_id: str, payload: dict[str, Any]) -> LeadSnapshot:
        snapshot = self.load_snapshot(lead_id)
        if snapshot.current_state != "demo_built":
            raise StageOrderError(
                f"Lead {lead_id} cannot record demo_checked from {snapshot.current_state}; expected demo_built"
            )
        demo_url = str(payload.get("demo_url") or snapshot.stage_payloads.get("demo_built", {}).get("demo_url") or "").strip()
        if not demo_url:
            raise StageOrderError("demo_checked requires a reviewable demo_url/build_url")
        artifact_payload = {
            **payload,
            "demo_url": demo_url,
            "lead_id": lead_id,
            "owner_id": owner_id,
            "owner_role": "demo_checker",
            "checked_at": self._now().isoformat(),
            "recorded_at": self._now().isoformat(),
        }
        artifact_path = self._write_artifact(lead_id, "demo_checked", artifact_payload)
        self._append_event(
            lead_id,
            {
                "kind": "demo_checked",
                "state": "demo_checked",
                "owner_id": owner_id,
                "recorded_at": self._now().isoformat(),
                "artifact_path": artifact_path,
                "payload": artifact_payload,
            },
        )
        return self.load_snapshot(lead_id)

    def record_customer_outreach_attempt(self, lead_id: str, owner_id: str, channel: str, recipient: Optional[str]) -> None:
        snapshot = self.load_snapshot(lead_id)
        if snapshot.current_state not in {"demo_checked", "outreach_blocked"}:
            raise StageOrderError(
                f"Lead {lead_id} cannot send customer outreach from {snapshot.current_state}; expected demo_checked or outreach_blocked"
            )
        self._append_event(
            lead_id,
            {
                "kind": "customer_outreach_attempted",
                "state": snapshot.current_state,
                "owner_id": owner_id,
                "recorded_at": self._now().isoformat(),
                "payload": {
                    "lead_id": lead_id,
                    "owner_id": owner_id,
                    "owner_role": "outreach",
                    "channel": channel,
                    "recipient": recipient,
                },
            },
        )

    def record_customer_sent(self, lead_id: str, owner_id: str, dispatch: dict[str, Any]) -> LeadSnapshot:
        snapshot = self.load_snapshot(lead_id)
        if snapshot.current_state not in {"demo_checked", "outreach_blocked"}:
            raise StageOrderError(
                f"Lead {lead_id} cannot record customer_sent from {snapshot.current_state}; expected demo_checked or outreach_blocked"
            )
        artifact_payload = {
            **dispatch,
            "lead_id": lead_id,
            "owner_id": owner_id,
            "owner_role": "outreach",
            "sent_at": self._now().isoformat(),
            "recorded_at": self._now().isoformat(),
        }
        artifact_path = self._write_artifact(lead_id, "customer_sent", artifact_payload)
        self._append_event(
            lead_id,
            {
                "kind": "customer_sent",
                "state": "customer_sent",
                "owner_id": owner_id,
                "recorded_at": self._now().isoformat(),
                "artifact_path": artifact_path,
                "payload": artifact_payload,
            },
        )
        return self.load_snapshot(lead_id)

    def record_outreach_blocked(self, lead_id: str, owner_id: str, payload: dict[str, Any]) -> LeadSnapshot:
        snapshot = self.load_snapshot(lead_id)
        if snapshot.current_state not in {"operator_approved", "demo_checked"}:
            raise StageOrderError(
                f"Lead {lead_id} cannot record outreach_blocked from {snapshot.current_state}; expected operator_approved or demo_checked"
            )
        artifact_payload = {
            **payload,
            "lead_id": lead_id,
            "owner_id": owner_id,
            "owner_role": "outreach",
            "blocked_at": self._now().isoformat(),
            "recorded_at": self._now().isoformat(),
        }
        artifact_path = self._write_artifact(lead_id, "outreach_blocked", artifact_payload)
        self._append_event(
            lead_id,
            {
                "kind": "outreach_blocked",
                "state": "outreach_blocked",
                "owner_id": owner_id,
                "recorded_at": self._now().isoformat(),
                "artifact_path": artifact_path,
                "payload": artifact_payload,
            },
        )
        return self.load_snapshot(lead_id)


class LeadStudioWorkflow:
    """Sequential autonomous lead studio with durable artifacts and checker-only approvals."""

    def __init__(
        self,
        store: Optional[LeadStudioStore] = None,
        dispatcher: Optional[TelegramApprovalDispatcher] = None,
        outreach_dispatcher: Optional[CustomerOutreachDispatcher] = None,
    ) -> None:
        self.store = store or LeadStudioStore()
        self.dispatcher = dispatcher or TelegramApprovalDispatcher()
        self.outreach_dispatcher = outreach_dispatcher or CustomerOutreachDispatcher()

    def scout_lead(self, lead_id: str, owner_id: str, payload: dict[str, Any]) -> LeadSnapshot:
        with self.store.claim(lead_id, owner_id, "scout"):
            return self.store.record_stage(lead_id, "scouted", owner_id, payload)

    def diagnose_lead(self, lead_id: str, owner_id: str, payload: dict[str, Any]) -> LeadSnapshot:
        with self.store.claim(lead_id, owner_id, "diagnoser"):
            return self.store.record_stage(lead_id, "diagnosed", owner_id, payload)

    def build_lead(self, lead_id: str, owner_id: str, payload: dict[str, Any]) -> LeadSnapshot:
        with self.store.claim(lead_id, owner_id, "builder"):
            return self.store.record_stage(lead_id, "built", owner_id, payload)

    def film_lead(self, lead_id: str, owner_id: str, payload: dict[str, Any]) -> LeadSnapshot:
        with self.store.claim(lead_id, owner_id, "filmer"):
            return self.store.record_stage(lead_id, "filmed", owner_id, payload)

    def pitch_lead(self, lead_id: str, owner_id: str, payload: dict[str, Any]) -> LeadSnapshot:
        with self.store.claim(lead_id, owner_id, "pitcher"):
            return self.store.record_stage(lead_id, "pitched", owner_id, payload)

    def check_lead(self, lead_id: str, owner_id: str, payload: dict[str, Any]) -> LeadSnapshot:
        with self.store.claim(lead_id, owner_id, "checker"):
            current_snapshot = self.store.load_snapshot(lead_id)
            if current_snapshot.is_rejected:
                raise LeadRejectedError(
                    f"Lead {lead_id} was rejected at {current_snapshot.rejected_at}: {current_snapshot.rejection_reason or 'no reason provided'}"
                )
            if current_snapshot.current_state == "pitched":
                checked_snapshot = self.store.record_stage(lead_id, "checked", owner_id, payload)
            elif current_snapshot.current_state == "checked" and not current_snapshot.is_rejected:
                checked_snapshot = current_snapshot
            else:
                raise StageOrderError(
                    f"Lead {lead_id} cannot enter checker dispatch from {current_snapshot.current_state}; expected pitched or checked"
                )
            checked_payload = checked_snapshot.stage_payloads.get("checked", {})
            if checked_payload.get("decision") == "rejected":
                return checked_snapshot
            dispatch_target = getattr(self.dispatcher, "target", "telegram")
            self.store.record_dispatch_attempt(lead_id, owner_id, dispatch_target)
            dispatch = self.dispatcher.request_approval(checked_snapshot)
            return self.store.record_approval_request(lead_id, owner_id, dispatch)

    def record_operator_decision(
        self,
        lead_id: str,
        owner_id: str,
        decision: str,
        payload: Optional[dict[str, Any]] = None,
    ) -> LeadSnapshot:
        """Record human APPROVE / REJECT / REVISE response after approval_requested."""
        with self.store.claim(lead_id, owner_id, "operator"):
            return self.store.record_operator_decision(lead_id, owner_id, decision, payload)

    def record_demo_built(self, lead_id: str, owner_id: str, payload: dict[str, Any]) -> LeadSnapshot:
        """Record a reviewable demo/build URL after operator approval."""
        with self.store.claim(lead_id, owner_id, "demo_builder"):
            return self.store.record_demo_built(lead_id, owner_id, payload)

    def record_demo_checked(self, lead_id: str, owner_id: str, payload: dict[str, Any]) -> LeadSnapshot:
        """Record QA approval for the demo/build URL before customer outreach."""
        with self.store.claim(lead_id, owner_id, "demo_checker"):
            return self.store.record_demo_checked(lead_id, owner_id, payload)

    def send_customer_outreach(self, lead_id: str, owner_id: str, payload: dict[str, Any]) -> LeadSnapshot:
        """Send approved customer outreach and record a durable customer_sent receipt."""
        with self.store.claim(lead_id, owner_id, "outreach"):
            current_snapshot = self.store.load_snapshot(lead_id)
            if current_snapshot.customer_sent:
                raise StageOrderError(f"Lead {lead_id} already reached customer_sent")
            if current_snapshot.current_state not in {"demo_checked", "outreach_blocked"}:
                raise StageOrderError(
                    f"Lead {lead_id} cannot send customer outreach from {current_snapshot.current_state}; expected demo_checked or outreach_blocked"
                )
            channel = str(payload.get("channel") or "email").lower()
            recipient = payload.get("recipient") or payload.get("to") or payload.get("contact")
            self.store.record_customer_outreach_attempt(lead_id, owner_id, channel, recipient)
            dispatch = self.outreach_dispatcher.send_outreach(current_snapshot, payload)
            return self.store.record_customer_sent(lead_id, owner_id, dispatch)

    def block_customer_outreach(self, lead_id: str, owner_id: str, payload: dict[str, Any]) -> LeadSnapshot:
        """Record that approved customer outreach is blocked and why."""
        with self.store.claim(lead_id, owner_id, "outreach"):
            current_snapshot = self.store.load_snapshot(lead_id)
            if current_snapshot.current_state not in {"operator_approved", "demo_checked"}:
                raise StageOrderError(
                    f"Lead {lead_id} cannot block customer outreach from {current_snapshot.current_state}; expected operator_approved or demo_checked"
                )
            return self.store.record_outreach_blocked(lead_id, owner_id, payload)


def build_sample_lead_payloads() -> dict[str, dict[str, Any]]:
    """Sample per-stage payloads for smoke tests and reusable workflow docs."""
    return {
        "scouted": {
            "business_name": "Greenpoint Dental Studio",
            "category": "dentist",
            "source_urls": [
                "https://example.com/greenpoint-dental-studio",
                "https://maps.example.com/greenpoint-dental-studio",
            ],
            "borough": "Brooklyn",
            "initial_confidence": 0.84,
        },
        "diagnosed": {
            "decision": "accepted",
            "website_url": "https://greenpointdentalstudio.example.com",
            "borough": "Brooklyn",
            "neighborhood": "Greenpoint",
            "is_real_business": True,
            "is_nyc_local": True,
            "false_positive_checks": ["not directory", "not wiki", "not association"],
        },
        "built": {
            "opportunity_summary": "Modernize the clinic site with a faster mobile landing page and clear appointment funnel.",
            "why_it_matters": "The current web presence undersells premium services and likely leaks mobile conversions.",
            "work_scope": ["mobile-first redesign", "booking CTA cleanup", "review proof module"],
        },
        "filmed": {
            "before_after_narrative": "Show the current dense homepage, then a streamlined mobile booking-first version.",
            "demo_framing": "90-second teardown with conversion-focused rebuild notes.",
            "evidence": ["slow hero load", "buried booking CTA", "weak testimonials placement"],
        },
        "pitched": {
            "pitch_text": "I found a fast mobile-web upgrade that could help Greenpoint Dental Studio convert more appointment traffic without changing their core brand.",
        },
        "checked": {
            "decision": "approved",
            "checker_note": "All six stages are present, evidence is concrete, and the prospective build is ready for human approval.",
        },
    }
