# -*- encoding: utf-8 -*-
# !/usr/bin/python3
# @Time   : 2019/7/4 15:56
# @File   : weixinpy.py
from api import *


class WeiXin:
    def __init__(self, uin):
        self.uin = uin

    def get_history_articles(self, biz, key):
        return get_history_api(biz=biz, uin=self.uin, key=key, offset=0)

    def get_article_comment(self, biz, comment_id, key):
        return get_article_comments_api(biz=biz, comment_id=comment_id, uin=self.uin, key=key)

    def get_article_detail(self, biz, key, comment_id, **kwargs):
        return get_article_read_like_api(uin=self.uin, biz=biz, key=key, comment_id=comment_id, **kwargs)

    def auto(self, biz, key):
        histories = self.get_history_articles(biz, key)
        for article_item in histories["results"]["article_infos"]:
            article_url = article_item["article_content_url"]
            comment_id = get_article_comment_id_api(article_url)
            print(comment_id, article_url)
            print(self.get_article_comment(biz, comment_id, key))
            print(self.get_article_detail(biz, key, comment_id, **split_article_url2mis(article_url)))


if __name__ == '__main__':
    test_key = "034516426b2066d0be790fd633c25bd2556e6c86e3e9b9ffc82a6fd06fbb8daccd281a0e027b63aa98eb47c944234cc2af2e41d4eddaabadfb3d4e1ce6ab76a8ad8d32eb9750148f08f20b30257910b9"
    weixin = WeiXin("MTE3MzE2NjAxOA==")
    weixin.auto("MzI1NTg3NzgwMw==", test_key)
