from datetime import datetime
import uuid
import copy

from fastapi import FastAPI

from models import (
    Attribute,
    BrazeUser,
    UserDeleteRequest,
    UserDeleteResponse,
    UserExportRequest,
    UserExportResponse,
    UserMergeRequest,
    UserMergeResponse,
    UserRemoveRequest,
    UserRemoveResponse,
    UserRenamePayload,
    UserRenameResponse,
    UserTrackRequest,
    UserTrackSuccessResponse,
)
from utils import user_merge, update_attributes

app = FastAPI()

DB = {}


def create_braze_user(
    user: Attribute, existing_user: Attribute, merge_objects: bool
) -> BrazeUser:
    user_dict = user.dict()
    user_dict.pop("merge_objects")

    if user_dict and existing_user:
        existing_user = existing_user.dict()
        user_dict = update_attributes(existing_user, user_dict, merge_objects)

    return BrazeUser(
        created_at=datetime.utcnow(),
        external_id=user_dict.pop("external_id", None),
        braze_id=str(uuid.uuid4()),
        first_name=user_dict.pop("first_name", None),
        last_name=user_dict.pop("last_name", None),
        email=user_dict.pop("email", None),
        dob=user_dict.pop("dob", None),
        home_city=user_dict.pop("home_city", None),
        country=user_dict.pop("country", None),
        custom_attributes=user_dict,
    )


@app.post("/users/track")
def user_track_route(payload: UserTrackRequest) -> UserTrackSuccessResponse:
    for attribute in payload.attributes:
        existing_user = DB.get(attribute.external_id)
        DB[attribute.external_id] = create_braze_user(
            attribute, existing_user, attribute.merge_objects
        )

    for event in payload.events:
        # TODO: Handle events
        pass

    return UserTrackSuccessResponse(
        attributes_processed=len(payload.attributes),
        events_processed=len(payload.events),
        purchases_processed=len(payload.purchases),
    )


@app.post("/users/export/ids")
def user_export_route(payload: UserExportRequest) -> UserExportResponse:
    return UserExportResponse(
        users=[
            DB[external_id] for external_id in payload.external_ids if external_id in DB
        ]
    )


@app.post("/users/delete")
def user_delete_route(payload: UserDeleteRequest) -> UserDeleteResponse:
    for external_id in payload.external_ids:
        DB.pop(external_id, None)

    return UserDeleteResponse(deleted=len(payload.external_ids))


@app.post("/users/external_ids/rename")
def user_rename_route(payload: UserRenamePayload) -> UserRenameResponse:
    for rename in payload.external_id_renames:
        current_user = DB.get(rename.current_external_id)
        if current_user:
            new_user = copy.deepcopy(current_user)
            new_user.external_id = rename.new_external_id
            DB[rename.new_external_id] = new_user

    return UserRenameResponse(
        external_ids=[
            rename.current_external_id for rename in payload.external_id_renames
        ]
    )


@app.post("/users/external_ids/remove", status_code=201)
def user_remove_route(payload: UserRemoveRequest) -> UserRemoveResponse:
    for external_id in payload.external_ids:
        DB.pop(external_id, None)

    return UserRemoveResponse(removed_ids=payload.external_ids)


@app.post("/users/merge", status_code=202)
def user_merge_route(payload: UserMergeRequest) -> UserMergeResponse:
    for merge in payload.merge_updates:
        keep_user = DB.get(merge.identifier_to_keep.external_id)
        merge_user = DB.get(merge.identifier_to_merge.external_id)

        if keep_user and merge_user:
            DB.pop(merge.identifier_to_merge.external_id)
            new_user_dict = user_merge(keep_user.dict(), merge_user.dict())
            DB[merge.identifier_to_keep.external_id] = BrazeUser(**new_user_dict)

    return UserMergeResponse()
