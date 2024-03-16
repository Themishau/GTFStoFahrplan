# -*- coding: utf-8 -*-
# https://www.protechtraining.com/blog/post/tutorial-the-observer-pattern-in-python-879
import logging
from .Base.GTFSEnums import *
import asyncio

logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s %(levelname)s %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S")


class Subscriber(object):
    def __init__(self, name, *args, **kwargs):
        self.name = name
        logging.debug("Subscriber name {}".format(self.name))

    # def notify_subscriber(self, event, message):
    #     logging.debug("no override")
    #     logging.debug('{}'.format(self.name))

    def trigger_action(self, event, message):
        logging.debug("trigger_action")
        logging.debug(f'message{message}')

    def update_gui(self, event, message):
        logging.debug("update_gui")
        logging.debug(f'message {message}')

    def print_me(self):
        logging.debug(self.name)


class Publisher(object):
    def __init__(self, events, *args, **kwargs):
        # maps event names to subscribers
        # str -> dict
        self.events = {event: dict()
                       for event in events}

    def print_me(self):
        logging.debug(self.events)

    def get_subscribers(self, event):
        return self.events[event]

    def register(self, event, who, callback=None):
        if callback is None:
            callback = getattr(who, 'notify_subscriber')
        else:
            callback = getattr(who, callback)
        logging.debug(
            f" \n register CALLBACK {self} \n REGISTER EVENT: {event} \n WITH OBJECT: {who} \n to EVENTS: {self.events} \n")
        self.get_subscribers(event)[who] = callback

    def register_self_trigger_action(self, event, who):
        callback = getattr(who, SubscriberTypes.trigger_action.value)
        logging.debug(
            f" \n register_self_trigger_action CALLBACK {self} \n REGISTER EVENT: {event} \n WITH OBJECT: {who} \n to EVENTS: {self.events} \n")
        self.get_subscribers(event)[who] = callback

    def register_self_update_gui(self, event, who):
        callback = getattr(who, SubscriberTypes.update_gui.value)
        logging.debug(
            f" \n register_self_update_gui CALLBACK {self} \n REGISTER EVENT: {event} \n WITH OBJECT {who} \n to EVENTS {self.events} \n")
        self.get_subscribers(event)[who] = callback

    def unregister(self, event, who):
        del self.get_subscribers(event)[who]

    def dispatch(self, event, message):
        try:
            logging.debug(
                f"dispatch: {self} {self.get_subscribers(event).items()},  dispatch(self, event, message): {event} {message} ")
            for subscriber, callback in self.get_subscribers(event).items():
                callback(event, message)
        except KeyError:
            logging.debug(f"these are the events listed {self.events} {event} is mmissing ")

    async def dispatchAsync(self, event, message):
        try:
            logging.debug(
                f"dispatch: {self} {self.get_subscribers(event).items()}, dispatch(self, event, message): {event} {message} ")
            for subscriber, callback in self.get_subscribers(event).items():
                asyncio.create_task(callback(event, message))  # Schedule callback execution as a task
        except KeyError:
            logging.debug(f"these are the events listed {self.events} {event} is missing ")
