import pytest
from pendulum import DateTime, parse, timezone
from pendulum.parsing.exceptions import ParserError

from dagtool.utils import DotDict, parse_version


def test_compare_version():
    assert not [0, 0, 1] >= [0, 0, 2]
    assert [2, 9, 3] >= [2, 1, 10]
    assert not [2, 9, 3] >= [3, 1, 10]


def test_parse_version():
    assert parse_version("3.1.5") == [3, 1, 5]


def test_parse_datetime():
    dt = parse("2025-01-01")
    assert isinstance(dt, DateTime)

    with pytest.raises(ParserError):
        data = "{{ vars('start_date') }}"
        parse(data).in_tz(timezone("Asia/Bangkok"))


def test_dotdict():
    data = DotDict({"foo": {"bar": {"baz": 1}}})

    assert data.get("foo.bar.baz") == 1
    assert data["foo.bar.baz"] == 1
    assert data.get("foo?.bar.missing", 42) == 42
    assert data.get("foo?.bar.missing") is None

    with pytest.raises(KeyError):
        assert data["foo?.bar.missing"]

    with pytest.raises(KeyError):
        assert data["foo.bar.missing"]

    assert data.get("foo.bar.missing", 42) == 42

    data.set("foo.bar.baz", 99)
    assert data["foo"]["bar"]["baz"] == 99
    assert data.get("foo.bar.baz") == 99

    # NOTE: strict set -> KeyError if path doesn't exist
    try:
        data.set("foo.buz.qux", 10)
    except KeyError as e:
        print(e)

    # NOTE: safe set -> creates missing path
    data.set("foo?.buz.qux", 10)
    assert data.get("foo.buz.qux") == 10
