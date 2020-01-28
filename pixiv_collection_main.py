# -*- coding: utf-8 -*-
from pixivpy3 import *
from pixiv_collection_db import *
from termcolor import colored
import os
from time import sleep

_CURR_DICT = os.path.dirname(os.path.abspath(__file__))  # directory of this file
_DBFILE = "%s/pixiv_bookmarks.db" % _CURR_DICT  # database filename
_ILLUSTDICT = "%s/illusts" % _CURR_DICT  # illustrations download directory

_SYNCINTERVAL = 3  # interval between requesting pages of bookmark [s]
_DOWNLOADINTERVAL = 15  # interval between downloading illustrations [s]
_TRIALCOUNT = 5  # times of retry if download fails
_RETRYINTERVAL = 45  # interval between retries [s]

# Although login is not required to view public bookmarks, Pixiv APIs do require login
_USERNAME = "userbay"
_PASSWORD = "userpay"

_USESNI = True  # Bypassing GFW, see [upbit/pixivpy: Pixiv API for Python](https://github.com/upbit/pixivpy)
_USERID = 15315919  # user to monitor

pixiv_api = None
db = None


def sync_bookmarks():
    """
    Sync user bookmarks with database. Database entry and illustration(s) of a deleted bookmark won't be deleted.
    We assume that all new bookmarks are before recorded bookmarks.
    :return: None
    """
    global pixiv_api, db
    max_bookmark_id = None
    count = 0

    pixiv_api.login(_USERNAME, _PASSWORD)

    while True:
        result = pixiv_api.user_bookmarks_illust(_USERID, max_bookmark_id=max_bookmark_id)
        for illust in result["illusts"]:
            if db.image_exists(illust["id"]):
                return  # encounter a image that already recorded (new bookmarks are at the front)
            db.add_image(illust)
            print(u"[%d] %d %s (%s)" % (count, illust["id"], illust["title"], illust["user"]["name"]))
            count += 1

        if result["next_url"]:
            for arg in result["next_url"].split("?")[-1].split("&"):
                p = arg.split("=")
                if p[0] == "max_bookmark_id":
                    max_bookmark_id = int(p[1])
                    break
        else:
            return  # no more bookmark

        sleep(_SYNCINTERVAL)


def sync_images():
    global pixiv_api, db
    images = db.get_undownloaded_images()
    if len(images) == 0:
        return
    else:
        print(colored("%d images to download" % len(images), "yellow"))
        if not os.path.exists(_ILLUSTDICT):
            os.makedirs(_ILLUSTDICT)
        for idx, (id, name, meta) in enumerate(images):
            urls = meta.split(",")
            for idx2, url in enumerate(urls):

                trial_count = 0
                while trial_count < _TRIALCOUNT:
                    trial_count += 1
                    try:
                        print(u"(%d/%d) [%d] %s (%d/%d)..." % (idx, len(images), id, name, idx2 + 1, len(urls)),
                              end="", flush=True)
                        pixiv_api.download(url, path=_ILLUSTDICT, name=None)
                        print("Done")
                        break
                    except Exception as e:
                        print("Failed, retry in %ds..." % _RETRYINTERVAL)
                        sleep(_RETRYINTERVAL)

                if trial_count >= _TRIALCOUNT:
                    print(colored("Failed for %d times! Terminate." % _TRIALCOUNT, "red"))
                    return

                sleep(_DOWNLOADINTERVAL)

            db.set_image_downloaded(id)


def init(use_sni):

    global db, pixiv_api

    db = PixivCollectionDB(_DBFILE, _USERID)

    if use_sni:
        pixiv_api = ByPassSniApi()  # Same as AppPixivAPI, but bypass the GFW
        pixiv_api.require_appapi_hosts()
    else:
        pixiv_api = AppPixivAPI()
    pixiv_api.set_accept_language('en-us')


def terminate():

    global db, pixiv_api

    del db
    db = None

    del pixiv_api
    pixiv_api = None


if __name__ == '__main__':

    init(use_sni=_USESNI)

    print(colored("Prepare to sync bookmarks...", "blue"))
    sync_bookmarks()
    print(colored("Bookmarks synced.", "green"))
    sleep(5)
    print(colored("Prepare to download new images...", "blue"))
    sync_images()
    print(colored("All images downloaded.", "green"))

    terminate()

