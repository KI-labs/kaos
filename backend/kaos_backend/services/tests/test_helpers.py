from kaos_backend.util.helpers import product_dict


def test_product_dict():
    result = list(product_dict(**{"a": [1, 2, 3], "b": ["foo", "bar"]}))
    reference = [{"a": 1, "b": "foo"},
                 {"a": 2, "b": "foo"},
                 {"a": 3, "b": "foo"},
                 {"a": 1, "b": "bar"},
                 {"a": 2, "b": "bar"},
                 {"a": 3, "b": "bar"}]

    assert len(result) == len(reference)
    for r in result:
        assert r in reference


def test_product_dict_empty():
    result = list(product_dict(**{}))
    assert list(result) == [{}]


def test_product_dict_one_key():
    result = product_dict(**{"a": [1, 2, 3]})
    assert list(result) == [{"a": 1}, {"a": 2}, {"a": 3}]
