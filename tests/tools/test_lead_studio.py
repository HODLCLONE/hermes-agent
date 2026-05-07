from __future__ import annotations

import json
from pathlib import Path

import pytest

from tools.lead_studio import (
    ApprovalDispatchError,
    CustomerOutreachDispatcher,
    CustomerOutreachError,
    LeadRejectedError,
    LeadStudioStore,
    LeadStudioWorkflow,
    OwnershipConflictError,
    StageOrderError,
    TelegramApprovalDispatcher,
    build_sample_lead_payloads,
)


class RecordingDispatcher:
    def __init__(self) -> None:
        self.calls: list[dict] = []

    def request_approval(self, snapshot):
        payload = {
            "target": "telegram:-100123:77",
            "message": f"Approval for {snapshot.lead_id}",
            "result": {"success": True, "message_id": 42},
        }
        self.calls.append(payload)
        return payload


class RecordingOutreachDispatcher:
    def __init__(self) -> None:
        self.calls: list[dict] = []

    def send_outreach(self, snapshot, payload):
        rendered = {
            "channel": payload.get("channel", "email"),
            "recipient": payload.get("recipient") or payload.get("to"),
            "cc": payload.get("cc") or ["hodlceo.eth@gmail.com"],
            "subject": payload.get("subject", "Test subject"),
            "message": payload.get("message") or payload.get("pitch_text") or "Pitch body",
            "result": {"success": True, "provider_message_id": "email-123"},
        }
        self.calls.append(rendered)
        return rendered


@pytest.fixture()
def sample_payloads() -> dict[str, dict]:
    return build_sample_lead_payloads()


@pytest.fixture()
def workflow(tmp_path: Path) -> LeadStudioWorkflow:
    store = LeadStudioStore(root=tmp_path / "lead-studio")
    dispatcher = RecordingDispatcher()
    return LeadStudioWorkflow(store=store, dispatcher=dispatcher)


def test_full_state_flow_reaches_approval_gate(workflow: LeadStudioWorkflow, sample_payloads: dict[str, dict]):
    lead_id = "greenpoint-dental-studio"

    snap = workflow.scout_lead(lead_id, "scout-agent", sample_payloads["scouted"])
    assert snap.current_state == "scouted"

    snap = workflow.diagnose_lead(lead_id, "diagnoser-agent", sample_payloads["diagnosed"])
    assert snap.current_state == "diagnosed"

    snap = workflow.build_lead(lead_id, "builder-agent", sample_payloads["built"])
    assert snap.current_state == "built"

    snap = workflow.film_lead(lead_id, "filmer-agent", sample_payloads["filmed"])
    assert snap.current_state == "filmed"

    snap = workflow.pitch_lead(lead_id, "pitcher-agent", sample_payloads["pitched"])
    assert snap.current_state == "pitched"

    snap = workflow.check_lead(lead_id, "checker-agent", sample_payloads["checked"])
    assert snap.current_state == "approval_requested"
    assert snap.completed_stages == ["scouted", "diagnosed", "built", "filmed", "pitched", "checked"]
    assert snap.approval_requested is True
    assert snap.stage_payloads["approval_requested"]["target"].startswith("telegram")

    artifacts = sorted((workflow.store.artifacts_dir(lead_id)).glob("*.json"))
    assert len(artifacts) == 7
    assert all(path.is_file() for path in artifacts)


def test_stage_order_is_enforced(workflow: LeadStudioWorkflow, sample_payloads: dict[str, dict]):
    with pytest.raises(StageOrderError):
        workflow.diagnose_lead("skip-scout", "diagnoser-agent", sample_payloads["diagnosed"])


def test_second_agent_cannot_mutate_owned_lead(tmp_path: Path, sample_payloads: dict[str, dict]):
    store = LeadStudioStore(root=tmp_path / "lead-studio")
    workflow = LeadStudioWorkflow(store=store, dispatcher=RecordingDispatcher())
    lead_id = "owned-lead"

    workflow.scout_lead(lead_id, "scout-agent", sample_payloads["scouted"])

    with store.claim(lead_id, "diagnoser-agent", "diagnoser"):
        with pytest.raises(OwnershipConflictError):
            workflow.diagnose_lead(lead_id, "builder-agent", sample_payloads["diagnosed"])

    snap = workflow.diagnose_lead(lead_id, "diagnoser-agent", sample_payloads["diagnosed"])
    assert snap.current_state == "diagnosed"


def test_rejected_diagnosis_stops_before_approval(workflow: LeadStudioWorkflow, sample_payloads: dict[str, dict]):
    lead_id = "directory-false-positive"
    rejected = dict(sample_payloads["diagnosed"])
    rejected.update({
        "decision": "rejected",
        "rejection_reason": "Business is a directory listing, not an operating NYC-local business.",
    })

    workflow.scout_lead(lead_id, "scout-agent", sample_payloads["scouted"])
    snap = workflow.diagnose_lead(lead_id, "diagnoser-agent", rejected)

    assert snap.current_state == "diagnosed"
    assert snap.rejected_at == "diagnosed"
    assert snap.approval_requested is False

    with pytest.raises(LeadRejectedError):
        workflow.build_lead(lead_id, "builder-agent", sample_payloads["built"])


def test_checked_rejection_is_terminal(tmp_path: Path, sample_payloads: dict[str, dict]):
    store = LeadStudioStore(root=tmp_path / "lead-studio")
    workflow = LeadStudioWorkflow(store=store, dispatcher=RecordingDispatcher())
    lead_id = "checker-rejected"
    checked_rejected = dict(sample_payloads["checked"])
    checked_rejected.update({
        "decision": "rejected",
        "checker_note": "Prospective build is too speculative for outreach.",
    })

    workflow.scout_lead(lead_id, "scout-agent", sample_payloads["scouted"])
    workflow.diagnose_lead(lead_id, "diagnoser-agent", sample_payloads["diagnosed"])
    workflow.build_lead(lead_id, "builder-agent", sample_payloads["built"])
    workflow.film_lead(lead_id, "filmer-agent", sample_payloads["filmed"])
    workflow.pitch_lead(lead_id, "pitcher-agent", sample_payloads["pitched"])

    snap = workflow.check_lead(lead_id, "checker-agent", checked_rejected)
    assert snap.current_state == "checked"
    assert snap.rejected_at == "checked"
    assert snap.approval_requested is False

    with pytest.raises(LeadRejectedError):
        workflow.check_lead(lead_id, "checker-agent", checked_rejected)


def test_checker_is_only_stage_that_dispatches_approval(tmp_path: Path, sample_payloads: dict[str, dict]):
    store = LeadStudioStore(root=tmp_path / "lead-studio")
    dispatcher = RecordingDispatcher()
    workflow = LeadStudioWorkflow(store=store, dispatcher=dispatcher)
    lead_id = "checker-gate"

    workflow.scout_lead(lead_id, "scout-agent", sample_payloads["scouted"])
    workflow.diagnose_lead(lead_id, "diagnoser-agent", sample_payloads["diagnosed"])
    workflow.build_lead(lead_id, "builder-agent", sample_payloads["built"])
    workflow.film_lead(lead_id, "filmer-agent", sample_payloads["filmed"])
    workflow.pitch_lead(lead_id, "pitcher-agent", sample_payloads["pitched"])

    assert dispatcher.calls == []

    workflow.check_lead(lead_id, "checker-agent", sample_payloads["checked"])
    assert len(dispatcher.calls) == 1


def test_telegram_dispatcher_uses_send_message_tool(tmp_path: Path, sample_payloads: dict[str, dict]):
    sent_args = {}

    def fake_send_tool(args):
        sent_args.update(args)
        return json.dumps({"success": True, "message_id": 99})

    store = LeadStudioStore(root=tmp_path / "lead-studio")
    workflow = LeadStudioWorkflow(
        store=store,
        dispatcher=TelegramApprovalDispatcher(target="telegram:-100555:17", send_tool=fake_send_tool),
    )
    lead_id = "telegram-path"

    workflow.scout_lead(lead_id, "scout-agent", sample_payloads["scouted"])
    workflow.diagnose_lead(lead_id, "diagnoser-agent", sample_payloads["diagnosed"])
    workflow.build_lead(lead_id, "builder-agent", sample_payloads["built"])
    workflow.film_lead(lead_id, "filmer-agent", sample_payloads["filmed"])
    workflow.pitch_lead(lead_id, "pitcher-agent", sample_payloads["pitched"])
    snap = workflow.check_lead(lead_id, "checker-agent", sample_payloads["checked"])

    assert sent_args["action"] == "send"
    assert sent_args["target"] == "telegram:-100555:17"
    assert "APPROVE / REJECT / REVISE" in sent_args["message"]
    assert "Opportunity:" in sent_args["message"]
    assert snap.current_state == "approval_requested"


def test_dispatch_errors_bubble_as_approval_dispatch_error(tmp_path: Path, sample_payloads: dict[str, dict]):
    attempts = []

    def failing_send_tool(args):
        attempts.append(args)
        return {"error": "telegram unavailable"}

    store = LeadStudioStore(root=tmp_path / "lead-studio")
    workflow = LeadStudioWorkflow(
        store=store,
        dispatcher=TelegramApprovalDispatcher(target="telegram", send_tool=failing_send_tool),
    )
    lead_id = "dispatch-failure"

    workflow.scout_lead(lead_id, "scout-agent", sample_payloads["scouted"])
    workflow.diagnose_lead(lead_id, "diagnoser-agent", sample_payloads["diagnosed"])
    workflow.build_lead(lead_id, "builder-agent", sample_payloads["built"])
    workflow.film_lead(lead_id, "filmer-agent", sample_payloads["filmed"])
    workflow.pitch_lead(lead_id, "pitcher-agent", sample_payloads["pitched"])

    with pytest.raises(ApprovalDispatchError):
        workflow.check_lead(lead_id, "checker-agent", sample_payloads["checked"])

    snap = workflow.store.load_snapshot(lead_id)
    assert snap.current_state == "checked"
    assert snap.approval_requested is False
    assert len(attempts) == 1

    retried = {}

    def succeeding_send_tool(args):
        retried.update(args)
        return json.dumps({"success": True, "message_id": 100})

    workflow.dispatcher = TelegramApprovalDispatcher(target="telegram", send_tool=succeeding_send_tool)
    retried_snapshot = workflow.check_lead(lead_id, "checker-agent", sample_payloads["checked"])
    assert retried_snapshot.current_state == "approval_requested"
    assert retried["target"] == "telegram"


def test_non_json_dispatch_response_is_treated_as_error(tmp_path: Path, sample_payloads: dict[str, dict]):
    def bad_send_tool(args):
        return "not-json"

    store = LeadStudioStore(root=tmp_path / "lead-studio")
    workflow = LeadStudioWorkflow(
        store=store,
        dispatcher=TelegramApprovalDispatcher(target="telegram", send_tool=bad_send_tool),
    )
    lead_id = "dispatch-bad-json"

    workflow.scout_lead(lead_id, "scout-agent", sample_payloads["scouted"])
    workflow.diagnose_lead(lead_id, "diagnoser-agent", sample_payloads["diagnosed"])
    workflow.build_lead(lead_id, "builder-agent", sample_payloads["built"])
    workflow.film_lead(lead_id, "filmer-agent", sample_payloads["filmed"])
    workflow.pitch_lead(lead_id, "pitcher-agent", sample_payloads["pitched"])

    with pytest.raises(ApprovalDispatchError):
        workflow.check_lead(lead_id, "checker-agent", sample_payloads["checked"])


def test_stale_owner_lock_is_recovered(tmp_path: Path, sample_payloads: dict[str, dict]):
    store = LeadStudioStore(root=tmp_path / "lead-studio", lock_timeout_seconds=1)
    workflow = LeadStudioWorkflow(store=store, dispatcher=RecordingDispatcher())
    lead_id = "stale-lock-lead"

    workflow.scout_lead(lead_id, "scout-agent", sample_payloads["scouted"])
    lock_path = store.lock_path(lead_id)
    lock_path.write_text(
        json.dumps(
            {
                "lead_id": lead_id,
                "owner_id": "stalled-agent",
                "owner_role": "diagnoser",
                "claimed_at": "2000-01-01T00:00:00+00:00",
            }
        ),
        encoding="utf-8",
    )

    snap = workflow.diagnose_lead(lead_id, "diagnoser-agent", sample_payloads["diagnosed"])
    assert snap.current_state == "diagnosed"


def _run_to_approval(workflow: LeadStudioWorkflow, lead_id: str, sample_payloads: dict[str, dict]):
    workflow.scout_lead(lead_id, "scout-agent", sample_payloads["scouted"])
    workflow.diagnose_lead(lead_id, "diagnoser-agent", sample_payloads["diagnosed"])
    workflow.build_lead(lead_id, "builder-agent", sample_payloads["built"])
    workflow.film_lead(lead_id, "filmer-agent", sample_payloads["filmed"])
    workflow.pitch_lead(lead_id, "pitcher-agent", sample_payloads["pitched"])
    return workflow.check_lead(lead_id, "checker-agent", sample_payloads["checked"])


def test_customer_outreach_records_durable_sent_state_with_email_cc(tmp_path: Path, sample_payloads: dict[str, dict]):
    store = LeadStudioStore(root=tmp_path / "lead-studio")
    outreach = RecordingOutreachDispatcher()
    workflow = LeadStudioWorkflow(
        store=store,
        dispatcher=RecordingDispatcher(),
        outreach_dispatcher=outreach,
    )
    lead_id = "customer-send"
    _run_to_approval(workflow, lead_id, sample_payloads)
    approved = workflow.record_operator_decision(lead_id, "operator-telegram", "approve", {"source": "telegram"})
    assert approved.current_state == "operator_approved"

    snap = workflow.send_customer_outreach(
        lead_id,
        "outreach-agent",
        {
            "channel": "email",
            "recipient": "owner@example.com",
            "pitch_text": "Here is the approved pitch/build.",
        },
    )

    assert snap.current_state == "customer_sent"
    assert snap.customer_sent is True
    sent = snap.stage_payloads["customer_sent"]
    assert sent["recipient"] == "owner@example.com"
    assert sent["cc"] == ["hodlceo.eth@gmail.com"]
    assert sent["message"] == "Here is the approved pitch/build."
    assert sent["result"]["success"] is True
    assert "sent_at" in sent
    assert len(list(store.artifacts_dir(lead_id).glob("*__customer_sent.json"))) == 1


def test_customer_outreach_blocked_is_durable_when_no_contact(tmp_path: Path, sample_payloads: dict[str, dict]):
    store = LeadStudioStore(root=tmp_path / "lead-studio")
    workflow = LeadStudioWorkflow(store=store, dispatcher=RecordingDispatcher())
    lead_id = "customer-blocked"
    _run_to_approval(workflow, lead_id, sample_payloads)
    approved = workflow.record_operator_decision(lead_id, "operator-telegram", "approve", {"source": "telegram"})
    assert approved.current_state == "operator_approved"

    snap = workflow.block_customer_outreach(
        lead_id,
        "outreach-agent",
        {
            "channel": "email",
            "blocked_reason": "No public customer email or working contact form found.",
            "searched_urls": ["https://example.com/contact"],
        },
    )

    assert snap.current_state == "outreach_blocked"
    assert snap.outreach_blocked is True
    blocked = snap.stage_payloads["outreach_blocked"]
    assert blocked["blocked_reason"].startswith("No public customer email")
    assert "blocked_at" in blocked


def test_customer_outreach_requires_human_approval_first(workflow: LeadStudioWorkflow, sample_payloads: dict[str, dict]):
    lead_id = "no-approval-yet"
    workflow.scout_lead(lead_id, "scout-agent", sample_payloads["scouted"])

    with pytest.raises(StageOrderError):
        workflow.send_customer_outreach(
            lead_id,
            "outreach-agent",
            {"channel": "email", "recipient": "owner@example.com"},
        )


def test_operator_decision_is_durable_gate_before_customer_send(tmp_path: Path, sample_payloads: dict[str, dict]):
    store = LeadStudioStore(root=tmp_path / "lead-studio")
    workflow = LeadStudioWorkflow(store=store, dispatcher=RecordingDispatcher())
    lead_id = "operator-approval"
    _run_to_approval(workflow, lead_id, sample_payloads)

    snap = workflow.record_operator_decision(
        lead_id,
        "operator-telegram",
        "approve",
        {"source": "telegram", "source_message": "Approve"},
    )

    assert snap.current_state == "operator_approved"
    assert snap.operator_approved is True
    approved = snap.stage_payloads["operator_approved"]
    assert approved["source"] == "telegram"
    assert approved["source_message"] == "Approve"
    assert "decided_at" in approved


def test_email_outreach_dispatcher_ccs_hodl_email_by_default(tmp_path: Path, sample_payloads: dict[str, dict]):
    sent_args = {}

    def fake_smtp(args):
        sent_args.update(args)
        return {"success": True, "provider_message_id": "smtp-1"}

    store = LeadStudioStore(root=tmp_path / "lead-studio")
    workflow = LeadStudioWorkflow(
        store=store,
        dispatcher=RecordingDispatcher(),
        outreach_dispatcher=CustomerOutreachDispatcher(smtp_send_fn=fake_smtp),
    )
    lead_id = "default-cc"
    _run_to_approval(workflow, lead_id, sample_payloads)
    approved = workflow.record_operator_decision(lead_id, "operator-telegram", "approve", {"source": "telegram"})
    assert approved.current_state == "operator_approved"

    snap = workflow.send_customer_outreach(
        lead_id,
        "outreach-agent",
        {"channel": "email", "recipient": "owner@example.com"},
    )

    assert sent_args["cc"] == ["hodlceo.eth@gmail.com"]
    assert sent_args["to"] == "owner@example.com"
    assert "Build opportunity:" in sent_args["message"]
    assert snap.stage_payloads["customer_sent"]["cc"] == ["hodlceo.eth@gmail.com"]


def test_email_outreach_dispatch_errors_are_not_marked_sent(tmp_path: Path, sample_payloads: dict[str, dict]):
    def failing_smtp(args):
        return {"error": "smtp unavailable"}

    store = LeadStudioStore(root=tmp_path / "lead-studio")
    workflow = LeadStudioWorkflow(
        store=store,
        dispatcher=RecordingDispatcher(),
        outreach_dispatcher=CustomerOutreachDispatcher(smtp_send_fn=failing_smtp),
    )
    lead_id = "customer-send-failure"
    _run_to_approval(workflow, lead_id, sample_payloads)
    approved = workflow.record_operator_decision(lead_id, "operator-telegram", "approve", {"source": "telegram"})
    assert approved.current_state == "operator_approved"

    with pytest.raises(CustomerOutreachError):
        workflow.send_customer_outreach(
            lead_id,
            "outreach-agent",
            {"channel": "email", "recipient": "owner@example.com"},
        )

    snap = store.load_snapshot(lead_id)
    assert snap.current_state == "operator_approved"
    assert snap.customer_sent is False
