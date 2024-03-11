from datetime import datetime
import uuid

from braze.db import setup, teardown, upsert_user, get_user


def test_integration():
    user = {
        "created_at": datetime.utcnow(),
        "external_id": "1",
        "braze_id": str(uuid.uuid4()),
        "first_name": None,
        "last_name": None,
        "email": None,
        "dob": None,
        "home_city": None,
        "country": None,
        "custom_attributes": {"sum_insured": 2},
    }
    conn = setup(":memory:")

    upsert_user(conn, user)

    stored_user = get_user(conn, user["external_id"])

    assert user == stored_user

    teardown(conn)
