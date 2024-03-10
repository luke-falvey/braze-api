from braze.utils import (
    user_merge,
    update_attributes,
    execute_array_object_operation,
    ArrayObjectOperation,
)


def test_user_merge():
    d1 = {"attr1": 1, "nattr": {"attr2": 1}}
    d2 = {
        "attr1": 2,
        "nattr": {"attr2": 2, "attr4": 1},
        "attr3": 2,
    }

    d = user_merge(d1, d2)

    expect = {
        "attr1": 1,
        "nattr": {"attr2": 1, "attr4": 1},
        "attr3": 2,
    }

    assert d == expect


def test_update_attributes_not_merge_objects():
    existing_attributes = {"attr1": 1, "nattr": {"attr2": 1}}
    new_attributes = {
        "attr1": 2,
        "nattr": {"attr2": 2, "attr4": 1},
        "attr3": 2,
    }

    d = update_attributes(existing_attributes, new_attributes, merge_objects=False)

    expect = {
        "attr1": 2,
        "nattr": {"attr2": 2, "attr4": 1},
        "attr3": 2,
    }

    assert d == expect


def test_update_attributes_merge_objects():
    existing_attributes = {"attr1": 1, "nattr": {"attr2": 1, "attr3": 3}}
    new_attributes = {
        "attr1": 2,
        "nattr": {"attr2": 2, "attr4": 1},
        "attr3": 2,
    }

    d = update_attributes(existing_attributes, new_attributes, merge_objects=True)

    expect = {
        "attr1": 2,
        "nattr": {"attr2": 2, "attr4": 1, "attr3": 3},
        "attr3": 2,
    }

    assert d == expect


def test_execute_array_object_operation_add():
    existing_attributes = [{"id": 1}]
    operations = [{"id": 2}]
    array_object_operation = ArrayObjectOperation.ADD
    execute_array_object_operation(
        existing_attributes, operations, array_object_operation, merge_objects=False
    )

    assert existing_attributes == [{"id": 1}, {"id": 2}]


def test_execute_array_object_operation_remove():
    existing_attributes = [{"id": 1}, {"id": 2}]
    operations = [{"$identifier_key": "id", "$identifier_value": 2}]
    array_object_operation = ArrayObjectOperation.REMOVE
    execute_array_object_operation(
        existing_attributes, operations, array_object_operation, merge_objects=False
    )

    assert existing_attributes == [{"id": 1}]


def test_execute_array_object_operation_update_not_merge_objects():
    existing_attributes = [{"id": 1, "attr_1": 1, "attr_2": 1}]
    operations = [
        {
            "$identifier_key": "id",
            "$identifier_value": 1,
            "$new_object": {"id": 1, "attr_1": 2, "attr_3": 2},
        }
    ]
    array_object_operation = ArrayObjectOperation.UPDATE
    execute_array_object_operation(
        existing_attributes, operations, array_object_operation, merge_objects=False
    )

    assert existing_attributes == [{"id": 1, "attr_1": 2, "attr_3": 2}]


def test_execute_array_object_operation_update_merge_objects():
    existing_attributes = [{"id": 1, "attr_1": 1, "attr_2": 1}]
    operations = [
        {
            "$identifier_key": "id",
            "$identifier_value": 1,
            "$new_object": {"id": 1, "attr_1": 2, "attr_3": 2},
        }
    ]
    array_object_operation = ArrayObjectOperation.UPDATE
    execute_array_object_operation(
        existing_attributes, operations, array_object_operation, merge_objects=True
    )

    assert existing_attributes == [{"id": 1, "attr_1": 2, "attr_2": 1, "attr_3": 2}]
