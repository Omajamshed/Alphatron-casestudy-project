import uuid
from app.db.models.user import User
from app.core.security import get_password_hash
from app.db.repositories.contract_repo import ContractRepository


def test_user_data_isolation(db_session, test_user):
    contract_repo = ContractRepository(db_session)

    # Create User B
    user_b = User(
        id=str(uuid.uuid4()),
        email="user_b@example.com",
        password_hash=get_password_hash("password123"),
    )
    db_session.add(user_b)
    db_session.commit()
    db_session.refresh(user_b)

    # User B creates a private contract
    contract_b = contract_repo.create_contract(
        user_id=user_b.id,
        title="User B Confidential Contract",
        contract_type="employment",
    )

    # Test User A (test_user) attempts to read User B's contract
    queried_by_a = contract_repo.get_contract(contract_id=contract_b.id, user_id=test_user.id)
    assert queried_by_a is None, "User A must not be able to access User B's contract"

    # Verify User A's contract list does NOT contain User B's contract
    list_for_a = contract_repo.list_contracts(user_id=test_user.id)
    contract_ids_a = [c.id for c in list_for_a]
    assert contract_b.id not in contract_ids_a

    # User B can access their own contract
    queried_by_b = contract_repo.get_contract(contract_id=contract_b.id, user_id=user_b.id)
    assert queried_by_b is not None
    assert queried_by_b.id == contract_b.id
