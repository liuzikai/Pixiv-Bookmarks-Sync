# -*- coding: utf-8 -*-
"""
    This is a module that sync Pixiv bookmarks and images.
"""

import requests
from datetime import datetime
import time
from termcolor import colored
import threading
import subprocess
import pixiv_collection_main as pixiv_collection


class PixivCollectionModule(threading.Thread):
    COMMAND_NAME = "pixiv"
    PROGRAM_NAME = "Pixiv Collection"

    def __init__(self):
        threading.Thread.__init__(self)
        self.last_update_year = 0
        self.last_update_month = 0
        self.last_update_day = 0
        self.last_update_time_stamp = None
        self.should_terminate = False

    def stop(self):
        self.should_terminate = True

    @staticmethod
    def get_log_stamp():
        return "[" + PixivCollectionModule.PROGRAM_NAME + " " + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "]"

    def need_to_sync(self):
        """
        Compare t with last update time, and return True if they are different.
        :param t: the input datetime
        :return: whether t is different from last update time
        """
        t = datetime.now()
        return (t.year != self.last_update_year or
                t.month != self.last_update_month or
                t.day != self.last_update_day)

    def perform_sync(self):
        """
        Perform sync and print result.
        :return: None
        """
        if self._perform_sync():
            print(colored('Done. Waiting for next day...\n', "green"))
        else:
            print(colored(
                'Error! Notification email has been sent. Waiting for next day...\n',
                "red"))

    def _perform_sync(self):
        """
        Actually perform sync. If failed, trigger IFTTT and return False.
        :return: True if success
        """
        t = datetime.now()
        self.last_update_time_stamp = t.strftime('%Y-%m-%d %H:%M')
        self.last_update_year = t.year
        self.last_update_month = t.month
        self.last_update_day = t.day

        print(colored("\n[%s %s]" % (self.PROGRAM_NAME, self.last_update_time_stamp), 'blue'))

        try:

            print(colored("Prepare to sync bookmarks...", "blue"))
            pixiv_collection.sync_bookmarks()
            print(colored("Bookmarks synced.", "green"))
            time.sleep(5)
            print(colored("Prepare to download new images...", "blue"))
            pixiv_collection.sync_images()
            print(colored("All images downloaded.", "green"))

        except (subprocess.TimeoutExpired, AssertionError) as e:
            requests.post("https://maker.ifttt.com/trigger/send_message_through_email/with/key/"
                          "bwcfamvDQpt3jv3zsfaUM6?value1=%s&value2=%s" % (self.PROGRAM_NAME, str(e)))
            return False

        return True

    def run(self):
        print(colored(self.get_log_stamp() + " Start", "green"))
        pixiv_collection.init(False)
        while not self.should_terminate:
            if self.need_to_sync():
                self.perform_sync()
            time.sleep(1)
        print(colored(self.get_log_stamp() + " Quit", "red"))
        pixiv_collection.terminate()

    def process_command(self, p):
        """
        A function to process commands
        :param p: the command string
        :return: True if the command is valid
        """

        if p == 'quit':
            if input(colored('Are you sure to quit %s? (Y/n) ' % self.PROGRAM_NAME, "yellow")) == 'Y':
                self.stop()
        elif p == 'run':
            self.perform_sync()
        elif p == 'help':
            print('pixiv        Pixiv Collection:')
            print('     quit    Quit the program')
            print('     run     Perform the sync manually')
        else:
            return False

        return True


if __name__ == '__main__':

    m = PixivCollectionModule()
    m.start()

    while not m.should_terminate:
        p = input()
        if not m.process_command(p):
            print(colored("Invalid command", "red"))
            m.process_command("help")

    m.join()
