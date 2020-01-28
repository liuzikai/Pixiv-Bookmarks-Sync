# -*- coding: utf-8 -*-
import sqlite3


class PixivCollectionDB:
    def __init__(self, db_file, user):
        self.db_file = db_file
        self.user = user

        self.conn = sqlite3.connect(self.db_file)

        self.conn.execute(u"""CREATE TABLE IF NOT EXISTS images_%d
            (
            id INTEGER UNIQUE,
            title TEXT,
            type TEXT,
            user_id INTEGER,
            user_name TEXT,
            user_account TEXT,
            tags TEXT,
            create_date TEXT,
            page_count INTEGER,
            width INTEGER,
            height INTEGER,
            sanity_level INTEGER,
            x_restrict INTEGER,
            meta TEXT,
            downloaded INTEGER
            )""" % self.user)

        self.conn.execute(u"""CREATE TABLE IF NOT EXISTS tags
            (
            name TEXT UNIQUE,
            translated_name TEXT,
            alias TEXT
            )""")

    def __del__(self):
        self.conn.commit()
        self.conn.close()

    def image_exists(self, id):
        return self.conn.execute(
            "SELECT EXISTS (SELECT 1 FROM images_%d WHERE id=? LIMIT 1)" % self.user, (id,)).fetchone()[0] == 1

    def add_image(self, d):
        """
        Add one image entry.
        :param d: directory of parsed json.
        :return: None
        """

        tags = []
        for tag in d["tags"]:
            self.conn.execute(u"INSERT OR REPLACE INTO tags (name, translated_name, alias) VALUES (?, ?, ?)",
                              (tag["name"], tag["translated_name"], ""))
            tags.append(tag["name"])

        if d["page_count"] == 1:
            meta = [d["meta_single_page"]["original_image_url"]]
        else:
            meta = []
            for page in d["meta_pages"]:
                meta.append(page["image_urls"]["original"])

        self.conn.execute(u"""INSERT INTO images_%d (id, title, type, user_id, user_name, user_account, tags, 
                          create_date, page_count, width, height, sanity_level, x_restrict, meta, downloaded)
                          VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""" % self.user,
                          (d["id"],
                           d["title"],
                           d["type"],
                           d["user"]["id"],
                           d["user"]["name"],
                           d["user"]["account"],
                           ",".join(tags),
                           d["create_date"],
                           d["page_count"],
                           d["width"],
                           d["height"],
                           d["sanity_level"],
                           d["x_restrict"],
                           ",".join(meta),
                           0))

        self.conn.commit()

    def get_undownloaded_images(self):
        """
        Get undownloaded images in [(id, meta, image)] where meta is comma-split urls of original images.
        :return: [(id, meta, image)] of undownloaded images
        """
        ts = self.conn.execute(u"SELECT id, title, meta FROM images_%d WHERE downloaded=0" % self.user).fetchall()
        return ts

    def set_image_downloaded(self, id, downloaded=1):
        self.conn.execute(u"UPDATE images_%d SET downloaded=? WHERE id=?" % self.user, (downloaded, id))
        self.conn.commit()
