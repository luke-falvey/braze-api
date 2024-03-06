from datetime import datetime
from typing import Mapping, List, Optional

from pydantic import BaseModel, Field, Extra, conlist


MAX_ATTRIBUTES = 75


class BrazeUser(BaseModel):
    # https://www.braze.com/docs/api/endpoints/export/user_data/post_users_identifier/#sample-user-export-file-output
    created_at: datetime
    external_id: str
    braze_id: str
    first_name: Optional[str]
    last_name: Optional[str]
    email: Optional[str]
    dob: Optional[str]
    home_city: Optional[str]
    country: Optional[str]
    custom_attributes: Mapping


class Attribute(BaseModel, extra=Extra.allow):
    external_id: str
    merge_objects: bool = Field(alias="_merge_objects", default=False)


class Event(BaseModel):
    pass


class Purchase(BaseModel):
    pass


class UserTrackRequest(BaseModel):
    attributes: Optional[conlist(Attribute, max_items=MAX_ATTRIBUTES)] = []  # type: ignore
    events: Optional[conlist(Event, max_items=MAX_ATTRIBUTES)] = []  # type: ignore
    purchases: Optional[conlist(Purchase, max_items=MAX_ATTRIBUTES)] = []  # type: ignore


class UserTrackSuccessResponse(BaseModel):
    message: str = "success"
    attributes_processed: int
    events_processed: int
    purchases_processed: int


class UserExportRequest(BaseModel):
    external_ids: conlist(str, max_items=MAX_ATTRIBUTES)  # type: ignore


class UserExportResponse(BaseModel):
    users: List[BrazeUser]  # type: ignore


class UserDeleteRequest(BaseModel):
    external_ids: conlist(str, max_items=MAX_ATTRIBUTES)  # type: ignore


class UserDeleteResponse(BaseModel):
    message: str = "success"
    deleted: int


class UserRemoveRequest(BaseModel):
    external_ids: List[str]


class UserRemoveResponse(BaseModel):
    message: str = "success"
    removed_ids: List[str]
    removal_errors: List[str] = []


class UserRename(BaseModel):
    current_external_id: str
    new_external_id: str


class UserRenamePayload(BaseModel):
    external_id_renames: List[UserRename]


class UserRenameResponse(BaseModel):
    message: str = "success"
    external_ids: List[str]
    rename_errors: Optional[List[str]]


class MergeIdentifier(BaseModel):
    external_id: str


class MergeUpdate(BaseModel):
    identifier_to_keep: MergeIdentifier
    identifier_to_merge: MergeIdentifier


class UserMergeRequest(BaseModel):
    merge_updates: List[MergeUpdate]


class UserMergeResponse(BaseModel):
    message: str = "success"


