# -*- coding: utf-8 -*-

"""Set up timers.

Lists all timers when triggered. Additional arguments in the form of "[[hours:]minutes:]seconds
[name]" let you set triggers. Empty field resolve to 0, e.g. "96::" starts a 96 hours timer.
Fields exceeding the maximum amount of the time interval are automatically refactorized, e.g.
"9:120:3600" resolves to 12 hours.

Synopsis: <trigger> [[[hours]:][minutes]:]seconds [name]"""

try:
    from albert import warning, Item, FuncAction
except ImportError:
    print("albert functions not available")

from threading import Timer
from time import strftime, time, localtime
import dbus
import os
from datetime import timedelta
import subprocess

__title__ = "Timer"
__version__ = "0.4.3"
__triggers__ = "timer "
__authors__ = ["manuelschneid3r", "googol42", "math2001"]
__py_deps__ = ["dbus"]

iconPath = os.path.dirname(__file__)+"/time.svg"
soundPath = os.path.dirname(__file__)+"/bing.wav"
timers = []

bus_name = "org.freedesktop.Notifications"
object_path = "/org/freedesktop/Notifications"
interface = bus_name

class AlbertTimer(Timer):

    def __init__(self, interval, name):

        def timeout():
            subprocess.Popen(["aplay", soundPath])
            global timers
            timers.remove(self)
            title = 'Timer "%s"' % self.name if self.name else 'Timer'
            text = "Timed out at %s" % strftime("%X", localtime(self.end))
            notify = dbus.Interface(dbus.SessionBus().get_object(bus_name, object_path), interface)
            notify.Notify(__title__, 0, iconPath, title, text, [], {"urgency":2}, 0)

        super().__init__(interval=interval, function=timeout)
        self.interval = interval
        self.name = name
        self.begin = int(time())
        self.end = self.begin + interval
        self.start()


def startTimer(interval, name):
    global timers
    timers.append(AlbertTimer(interval, name))


def deleteTimer(timer):
    global timers
    timers.remove(timer)
    timer.cancel()

def parse_single_timedelta(string):
    if len(string) == 0:
        return timedelta(seconds=0), 0

    i = 0
    while i < len(string) and string[i] in "0123456789:":
        i += 1

    if i == 0:
        raise ValueError("expect number or colon, not {}".format(string[0]))

    values = string[:i].split(':')
    if len(values) > 3:
        raise ValueError("too many parts")
    if len(values) == 1:
        nums = [0, 0]
    elif len(values) == 2:
        nums = [0]
    else:
        nums = []

    for v in values:
        if v == '':
            v = '0'
        try:
            n = int(v)
        except ValueError:
            raise
        nums.append(n)

    return timedelta(
        hours=nums[0],
        minutes=nums[1],
        seconds=nums[2],
    ), i


def parse_timedelta(string):
    """ returns a timedelta. Supports adding and subtracting.
        Raises a ValueError is the duration is negative
    """
    i = 0

    s = timedelta(seconds=0)
    op = '+'

    while True:
        try:
            delta, n = parse_single_timedelta(string[i:])
        except ValueError as e:
            raise ValueError("after {!r}: {}".format(string[:i], e))

        i += n
        if op == '+':
            s += delta
        elif op == '-':
            s -= delta
        else:
            assert False, "invalid operator: {}".format(op)

        if i == len(string) or string[i] == ' ':
            break
        elif string[i] in '-+':
            op = string[i]
            i += 1
        else:
            raise ValueError("invalid character {!r} after {!r}".format(string[i], string[:i]))

    if s.total_seconds() < 0:
        raise ValueError("duration is negative: {}".format(s))

    return s, i

def parse_query(string):
    delta, i = parse_timedelta(string)
    if i == len(string):
        return delta, ""

    assert string[i] == ' '
    return delta, string[i+1:].strip()

def add_timer(text):
    try:
        delta, name = parse_query(text)
    except ValueError as e:
        return Item(
            id=__title__,
            text="Invalid input: {}".format(e),
            subtext="Enter a query in the form of '%s[[hours:]minutes:]seconds [name]'" % __triggers__,
            icon=iconPath
        )

    seconds = delta.total_seconds()

    return Item(
        id=__title__,
        text=str(delta),
        subtext='Set a timer with name "%s"' % name if name else 'Set a timer',
        icon=iconPath,
        actions=[FuncAction("Set timer", lambda: startTimer(seconds, name))]
    )

def list_timers():
    # List timers
    items = []
    for timer in timers:

        m, s = divmod(timer.interval, 60)
        h, m = divmod(m, 60)
        identifier = "%d:%02d:%02d" % (h, m, s)

        timer_name_with_quotes = '"%s"' % timer.name if timer.name else ''
        items.append(Item(
            id=__title__,
            text='Delete timer <i>%s [%s]</i>' % (timer_name_with_quotes, identifier),
            subtext="Times out %s (in ~%s)" % (strftime("%X", localtime(timer.end)), str(timedelta(seconds=timer.end - int(time())))),
            icon=iconPath,
            actions=[FuncAction("Delete timer", lambda timer=timer: deleteTimer(timer))]
        ))
    if items:
        return items
    # Display hint item
    return Item(
        id=__title__,
        text="Add timer",
        subtext="Enter a query in the form of '%s[[hours:]minutes:]seconds [name]'" % __triggers__,
        icon=iconPath
    )

def handleQuery(query):
    if query.isTriggered:
        text = query.string.strip()
        if text:
            return add_timer(text)
        else:
            return list_timers()
