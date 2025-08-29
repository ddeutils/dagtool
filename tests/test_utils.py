from dagtool.utils import parse_version


def test_compare_version():
    assert not [0, 0, 1] >= [0, 0, 2]
    assert [2, 9, 3] >= [2, 1, 10]
    assert not [2, 9, 3] >= [3, 1, 10]


def test_parse_version():
    assert parse_version("3.1.5") == [3, 1, 5]
