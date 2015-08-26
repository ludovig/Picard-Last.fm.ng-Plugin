# -*- coding: utf-8 -*-
import os

from picard.const import USER_DIR

from . import settings
from .helpers.tags import apply_tag_weight


class DebugMixin(object):
    def print_toplist(self, merged):
        def p(score):
            return int(float(score) / float(topscore) * 100.0)

        try:
            topscore = merged[0][1]
            toplist = ["{0}: {1} ({2}%)".format(n, s, p(s)) for n, s in
                       merged[:10]]
            self.log.info("{0}".format(", ".join(toplist)))
        except:
            self.log.info("None")

    def print_toptag_stats(self, scope, name, correction=1):
        toptags = self.toptags[name]
        weight = settings.CONFIG[scope]['weight'][name]
        self.log.info(
            "got {0} {1} tags (x{2}):".format(len(toptags), name, weight))
        merged = apply_tag_weight((toptags, correction))[:10]
        self.print_toplist(merged)


class CollectUnusedMixin(object):
    def collect_unused(self):
        """
        This collects toptags not used to tag files.
        It is a way to find new genres/groupings in the tags used on last.fm.
        """
        self.log.debug(u"collecting unused toptags...")
        all_tags = apply_tag_weight(
            (self.toptags['album'], 1),
            (self.toptags['track'], 1),
            (self.toptags['artist'], 1),
            (self.toptags['all_track'], 1),
            (self.toptags['all_artist'], 1)
        )

        searchlists = [opt['searchlist'] for cat, opt in
                       settings.CATEGORIES.items()]
        unknown_toptags = []

        for toptag in all_tags:
            tag, score = toptag
            for searchlist in searchlists:
                if tag in searchlist:
                    toptag = None
                    break
            if toptag is not None:
                unknown_toptags.append(toptag)

        dbfile = os.path.join(USER_DIR, 'lastfmng', 'toptags.db')
        self.log.debug(u"opening database: %s", dbfile)

        import sqlite3

        conn = sqlite3.connect(dbfile)
        c = conn.cursor()

        try:
            c.execute("""
                CREATE TABLE toptags (tag TEXT PRIMARY KEY, score INTEGER)
                """)
        except:
            pass

        for tag, score in unknown_toptags:
            c.execute("""
                REPLACE INTO toptags (tag, score)
                VALUES (?,
                coalesce((SELECT score FROM toptags WHERE tag = ?),0)+?)
                """, (tag, tag, score))

        conn.commit()
        c.close()