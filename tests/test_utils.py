import pytest

from braze.utils import (
    user_merge,
    update_attributes,
    execute_array_object_operation,
    ArrayObjectOperation,
)


@pytest.fixture(name="attributes")
def INITIAL_STATE():
    return {
        "external_id": "1",
        "attr_1": 1,
        "nested_attr": {"attr_2": 1, "dnested_attr": {"attr_3": 1}},
        "array_attr": [{"id": 1, "attr_4": 1}],
    }


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


def test_update_attributes_update_attr_1(attributes):
    new_attributes = {"external_id": "1", "attr_1": 2}
    update_attributes(attributes, new_attributes, merge_objects=False)

    assert attributes["attr_1"] == 2


def test_update_attributes_update_attr_2_merge_objects(attributes):
    new_attributes = {"external_id": "1", "nested_attr": {"attr_2": 2}}
    update_attributes(attributes, new_attributes, merge_objects=True)

    assert attributes["nested_attr"]["attr_2"] == 2
    assert attributes["nested_attr"]["dnested_attr"]["attr_3"] == 1


def test_update_attributes_update_attr_2_no_merge_objects(attributes):
    new_attributes = {"external_id": "1", "nested_attr": {"attr_2": 2}}
    update_attributes(attributes, new_attributes, merge_objects=False)

    assert attributes["nested_attr"]["attr_2"] == 2
    assert "dnested_attr" not in attributes["nested_attr"]


def test_update_attributes_update_attr_3_no_merge_objects(attributes):
    new_attributes = {
        "external_id": "1",
        "nested_attr": {"dnested_attr": {"attr_3": 2}},
    }
    update_attributes(attributes, new_attributes, merge_objects=False)

    assert attributes["nested_attr"]["dnested_attr"]["attr_3"] == 2
    assert "attr_2" not in attributes["nested_attr"]


def test_update_attributes_update_attr_3_merge_objects(attributes):
    new_attributes = {
        "external_id": "1",
        "nested_attr": {"dnested_attr": {"attr_3": 2}},
    }
    update_attributes(attributes, new_attributes, merge_objects=True)

    assert attributes["nested_attr"]["dnested_attr"]["attr_3"] == 2
    assert attributes["nested_attr"]["attr_2"] == 1


def test_update_attributes_update_array_attr_add_object(attributes):
    new_attributes = {
        "external_id": "1",
        "array_attr": {"$add": [{"id": 2, "attr_5": "1"}]},
    }
    update_attributes(attributes, new_attributes, merge_objects=True)

    assert len(attributes["array_attr"]) == 2
    assert attributes["array_attr"][1] == {"id": 2, "attr_5": "1"}


def test_update_attributes_update_array_attr_update_object(attributes):
    new_attributes = {
        "external_id": "1",
        "array_attr": {
            "$update": [
                {
                    "$identifier_key": "id",
                    "$identifier_value": 1,
                    "$new_object": {"id": 1, "attr_4": "2"},
                }
            ]
        },
    }
    update_attributes(attributes, new_attributes, merge_objects=True)

    assert len(attributes["array_attr"]) == 1
    assert attributes["array_attr"][0] == {"id": 1, "attr_4": "2"}


def test_update_attributes_update_array_attr_remove_object(attributes):
    new_attributes = {
        "external_id": "1",
        "array_attr": {
            "$remove": [
                {
                    "$identifier_key": "id",
                    "$identifier_value": 1,
                }
            ]
        },
    }
    update_attributes(attributes, new_attributes, merge_objects=True)

    assert len(attributes["array_attr"]) == 0


def test_update_attributes_remove_operation_on_new_user():
    attributes = {}
    new_attributes = {
        "external_id": "1",
        "array_attr": {
            "$remove": [
                {
                    "$identifier_key": "id",
                    "$identifier_value": 1,
                }
            ]
        },
    }
    update_attributes(attributes, new_attributes, merge_objects=True)

    assert "array_attr" not in attributes
    assert attributes == {"external_id": "1"}


def test_update_attributes_add_operation_on_new_user():
    attributes = {}
    new_attributes = {
        "external_id": "1",
        "array_attr": {"$add": [{"id": 1, "attr_4": "1"}]},
    }
    update_attributes(attributes, new_attributes, merge_objects=True)

    assert attributes == {"external_id": "1"}
