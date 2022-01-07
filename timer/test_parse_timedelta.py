"""
To run the tests:

    modules/timer $ python test_parse_timedelta.py
"""

from __init__ import parse_query
from datetime import timedelta


def test_parse_query():
    table = (
        (":", timedelta(seconds=0), ""),
        (":: now", timedelta(seconds=0), "now"),
        ("2: yo", timedelta(minutes=2), "yo"),
        ("1:2:3 hello world", timedelta(hours=1, minutes=2, seconds=3), "hello world"),
        ("1:2: ok", timedelta(hours=1, minutes=2), "ok"),
        (":3 what?", timedelta(seconds=3), "what?"),
        ("2:3 what's up", timedelta(minutes=2, seconds=3), "what's up"),
        ("3  works", timedelta(seconds=3), "works"),
        ("3+2 five  ", timedelta(seconds=5), "five"),
        ("1:2+3:4 lorem\t", timedelta(minutes=1 + 3, seconds=2 + 4), "lorem"),
        ("1:2+3: tricked", timedelta(minutes=1 + 3, seconds=2 + 0), "tricked"),
        ("1:2+3 b b ro", timedelta(minutes=1, seconds=2 + 3), "b b ro"),
        ("1:2-3", timedelta(minutes=1, seconds=-1), ""),
        ("3:4-1:2", timedelta(minutes=3 - 1, seconds=4 - 2), ""),
        ("3:4-1:8 bar", timedelta(minutes=3 - 1, seconds=4 - 8), "bar"),
        ("1:2-3:4 bar", ValueError, ''),
        ("1:24:32-5: foo", timedelta(hours=1, minutes=24 - 5, seconds=32), 'foo'),
        ("1:2-", timedelta(minutes=1, seconds=2), ''),
    )

    for string, want_delta, want_message in table:
        if want_delta == ValueError:
            # manual assert raises
            err = None
            try:
                parse_query(string)
            except Exception as e:
                err = e
            assert isinstance(
                err, ValueError
            ), "string={} should raised ValueError, got {}".format(string, err)
        else:
            assert parse_query(string) == (
                want_delta,
                want_message,
            ), "string={} got={} want={}".format(
                string, parse_query(string), (want_delta, want_message)
            )


if __name__ == "__main__":
    test_parse_query()
    print("[ ok ] Tests passed")
