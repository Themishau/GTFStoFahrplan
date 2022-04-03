# -*- coding: utf-8 -*-
# https://www.protechtraining.com/blog/post/tutorial-the-observer-pattern-in-python-879


class Subscriber(object):
    def __init__(self, name, *args, **kwargs):
        self.name = name
        print("Subscriber name {}".format(self.name))

    def notify_subscriber(self, event, message):
        print("no override")
        print('{}'.format(self.name))

    def print_me(self):
        print(self.name)


class Publisher(object):
    def __init__(self, events, *args, **kwargs):
        # maps event names to subscribers
        # str -> dict
        self.events = {event: dict()
                       for event in events}

    def print_me(self):
        print(self.events)

    def get_subscribers(self, event):
        return self.events[event]

    def register(self, event, who, callback=None):
        if callback is None:
            callback = getattr(who, 'notify_subscriber')
        self.get_subscribers(event)[who] = callback

    def unregister(self, event, who):
        del self.get_subscribers(event)[who]

    def dispatch(self, event, message):
        # print("{} {} dispatch(self, event, message) {} {} ".format(self ,self.get_subscribers(event).items(), event, message))
        for subscriber, callback in self.get_subscribers(event).items():
            callback(event, message)
