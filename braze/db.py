from sqlite3 import connect, Connection
from typing import Mapping, Optional
from datetime import datetime
import json
import os
import copy

SETUP_SCRIPT_PATH = "sql/setup.sql"
TEARDOWN_SCRIPT_PATH = "sql/teardown.sql"


def dict_factory(cursor, row):
    fields = [column[0] for column in cursor.description]
    return {key: value for key, value in zip(fields, row)}


def setup(databse: str = ":memory:") -> Connection:
    conn = connect(databse)
    conn.execute("""
        create table user (
            created_at datetime not null,
            external_id text primary key,
            braze_id text not null,
            first_name text,
            last_name text,
            email text,
            dob text,
            home_city text,
            country text,
            custom_attributes json
        );
    """)
    return conn


def teardown(conn: Connection, database: Optional[str] = ":memory:"):
    conn.execute("drop table user;")

    if database and database != ":memory:":
        os.remove(TEARDOWN_SCRIPT_PATH)


def get_user(conn: Connection, external_id: str) -> Mapping:
    cursor = conn.execute("select * from user where external_id = ?", (external_id,))
    cursor.row_factory = dict_factory
    row = cursor.fetchone()
    row["created_at"] = datetime.fromisoformat(row["created_at"])
    row["custom_attributes"] = json.loads(row["custom_attributes"])
    return row


def upsert_user(conn: Connection, user: Mapping):
    stored_user = copy.deepcopy(user)
    stored_user["custom_attributes"] = json.dumps(stored_user["custom_attributes"])
    conn.execute(
        """
        insert into user(
            created_at,
            external_id,
            braze_id,
            first_name,
            last_name,
            email,
            dob,
            home_city,
            country,
            custom_attributes
        )
        values (
            :created_at,
            :external_id,
            :braze_id,
            :first_name,
            :last_name,
            :email,
            :dob,
            :home_city,
            :country,
            json(:custom_attributes)
        )
        on conflict(external_id)
        do update set 
            created_at=:created_at,
            external_id=:external_id,
            braze_id=:braze_id,
            first_name=:first_name,
            last_name=:last_name,
            email=:email,
            dob=:dob,
            home_city=:home_city,
            country=:country,
            custom_attributes=json(:custom_attributes);
        """,
        stored_user,
    )
