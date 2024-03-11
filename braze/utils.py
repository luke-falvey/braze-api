from typing import Mapping, Optional, List
from enum import Enum


ARRAY_OPERATIONS = set(["$add", "$update", "$remove"])


class ArrayObjectOperation(Enum):
    ADD = "$add"
    UPDATE = "$update"
    REMOVE = "$remove"


def user_merge(keep_user: Mapping, merge_user: Mapping):
    for k, v in merge_user.items():
        if k not in keep_user and not isinstance(v, (dict)):
            keep_user[k] = v
        elif isinstance(v, dict):
            keep_user[k] = user_merge(keep_user[k], v)
    return keep_user


def get_array_object_operation(value) -> Optional[ArrayObjectOperation]:
    if (
        isinstance(value, dict)
        and len(value) == 1
        and any(k in ARRAY_OPERATIONS for k in value)
    ):
        operation = list(value)[0]
        if operation == ArrayObjectOperation.ADD.value:
            return ArrayObjectOperation.ADD
        elif operation == ArrayObjectOperation.UPDATE.value:
            return ArrayObjectOperation.UPDATE
        elif operation == ArrayObjectOperation.REMOVE.value:
            return ArrayObjectOperation.REMOVE


def execute_remove_array_objects(
    existing_attributes: List[Mapping], remove_operations: List[Mapping]
) -> List[Mapping]:
    for attribute in existing_attributes:
        if any(
            attribute.get(remove_operation.get("$identifier_key"))
            == remove_operation.get("$identifier_value")
            for remove_operation in remove_operations
        ):
            existing_attributes.remove(attribute)


def execute_update_array_objects(
    existing_attributes, update_operations, merge_objects
) -> List[Mapping]:
    for i, existing_attribute in enumerate(existing_attributes):
        for remove_operation in update_operations:
            identifier_key = remove_operation.get("$identifier_key")
            identifier_value = remove_operation.get("$identifier_value")
            new_object = remove_operation.get("$new_object")
            if (
                identifier_key
                and identifier_value
                and identifier_key in existing_attribute
                and identifier_value == existing_attribute.get(identifier_key)
            ):
                if merge_objects:
                    existing_attributes[i] = {**existing_attribute, **new_object}
                else:
                    existing_attributes[i] = new_object


def execute_add_array_objects(existing_attributes, add_operations) -> List[Mapping]:
    existing_attributes.extend(add_operations)
    return existing_attributes


def execute_array_object_operation(
    existing_attributes: List[Mapping],
    operations: Mapping,
    array_object_operation: ArrayObjectOperation,
    merge_objects: bool,
) -> List[Mapping]:
    if not isinstance(existing_attributes, list):
        return

    if array_object_operation == ArrayObjectOperation.ADD:
        return execute_add_array_objects(existing_attributes, operations)
    elif array_object_operation == ArrayObjectOperation.UPDATE:
        return execute_update_array_objects(
            existing_attributes, operations, merge_objects
        )
    elif array_object_operation == ArrayObjectOperation.REMOVE:
        return execute_remove_array_objects(existing_attributes, operations)


def update_attributes(
    existing_attributes: Mapping, new_attributes: Mapping, merge_objects: bool
):
    for k, v in new_attributes.items():
        array_object_operation = get_array_object_operation(v)
        if array_object_operation:
            operations = v[array_object_operation.value]
            execute_array_object_operation(
                existing_attributes.get(k, []),
                operations,
                array_object_operation,
                merge_objects,
            )
        elif isinstance(v, dict) and not merge_objects:
            existing_attributes[k] = v
        elif isinstance(v, dict) and merge_objects:
            existing_attributes[k] = update_attributes(
                existing_attributes[k] if k in existing_attributes else {},
                new_attributes[k],
                merge_objects,
            )
        else:
            existing_attributes[k] = v

    return existing_attributes
