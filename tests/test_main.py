from braze.utils import user_merge, update_attributes


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
