import uuid
from langgraph.types import Command
from app.agents.graph import review_graph
from app.db.repositories.contract_repo import ContractRepository
from app.db.repositories.clause_repo import ClauseRepository


def test_agent_graph_interrupt_and_resume(db_session, test_user):
    contract_repo = ContractRepository(db_session)
    clause_repo = ClauseRepository(db_session)

    # Setup contract and version
    contract = contract_repo.create_contract(
        user_id=test_user.id,
        title="Consulting Master Services Agreement",
        contract_type="freelance",
        party_role="freelancer",
    )
    version = contract_repo.create_version(
        contract_id=contract.id,
        version=1,
        filename="contract.pdf",
    )

    # Insert risky clause (unlimited liability)
    clause_repo.add_clause(
        version_id=version.id,
        clause_no="8.1",
        heading="Indemnification",
        text="Contractor shall indemnify Client with unlimited liability for any damages.",
        page_start=1,
        page_end=1,
    )

    thread_id = f"test_thread_{uuid.uuid4().hex[:8]}"
    config = {"configurable": {"thread_id": thread_id}}

    # 1. Start agent execution
    initial_state = {
        "version_id": version.id,
        "contract_id": contract.id,
        "party_role": "freelancer",
        "contract_type": "freelance",
    }
    review_graph.invoke(initial_state, config=config)

    # Check paused at human_review interrupt
    snapshot = review_graph.get_state(config)
    assert snapshot.next, "Agent should pause at interrupt for human review"
    assert "suggestions" in snapshot.values
    suggestions = snapshot.values["suggestions"]
    assert len(suggestions) > 0

    # 2. Simulate human decision (Approve the first suggestion)
    sug_id = suggestions[0]["id"]
    decisions = {
        sug_id: {
            "status": "approved",
            "final_text": "Both parties agree to a mutual liability cap limited to total contract fees.",
        }
    }

    # Resume graph execution with decisions
    review_graph.invoke(Command(resume=decisions), config=config)

    # Check finished execution
    final_snapshot = review_graph.get_state(config)
    assert not final_snapshot.next, "Agent should complete export after decisions submitted"
    assert final_snapshot.values.get("status") == "completed"
    assert len(final_snapshot.values.get("export_ids", [])) > 0
