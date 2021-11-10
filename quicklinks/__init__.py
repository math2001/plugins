# -*- coding: utf-8 -*-
"""
open links quickly
"""

import albert
import json

FILE = '/home/math2001/.quicklinks.json'

__title__ = "Quick Links"
__version__ = "0.1.0"
__triggers__ = "q"
__authors__ = "Mathieu Paturel"

def fuzz_match(search, full_text):
    full_text = full_text.lower()
    start = -1
    for char in search.lower():
        start = full_text.find(char, start+1)
        if start == -1:
            return False
    return True


def handleQuery(query):
    if not query.isTriggered:
        return []

    try:
        with open(FILE, 'r') as fp:
            links = json.load(fp)
    except FileNotFoundError as e:
        albert.warning("File {!r} not found: {}".format(FILE, e))
        return []
    except ValueError as e:
        albert.warning("Couldn't load JSON: {}".format(e))
        return []

    items = []
    for name, url in links.items():
        if not fuzz_match(query.string, name):
            continue

        items.append(albert.Item(
            text=name,
            subtext="Open {}".format(url),
            actions=[
                albert.UrlAction(text='what does this text do?',
                                 url=url)
            ]
        ))

    return items

if __name__ == "__main__":
    assert fuzz_match("foo", "foobar")
    assert fuzz_match("foo", "f blah o basdf o")
    assert not fuzz_match("foo", "oof")
