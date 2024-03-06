from typing import Mapping


def user_merge(keep_user: Mapping, merge_user: Mapping):
    for k, v in merge_user.items():
        if k not in keep_user and not isinstance(v, (dict)):
            keep_user[k] = v
        elif isinstance(v, dict):
            keep_user[k] = user_merge(keep_user[k], v)
    return keep_user


def update_attributes(
    existing_attributes: Mapping, new_attributes: Mapping, merge_objects: bool
):
    for k, v in new_attributes.items():
        if isinstance(v, dict) and not merge_objects:
            existing_attributes[k] = v
        if isinstance(v, dict) and merge_objects:
            existing_attributes[k] = update_attributes(
                existing_attributes[k] if k in existing_attributes else {},
                new_attributes[k],
                merge_objects,
            )
        else:
            existing_attributes[k] = v

    return existing_attributes
