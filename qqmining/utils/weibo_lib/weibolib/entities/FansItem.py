#coding=utf-8
#!/usr/bin/env python
# Created by Tina on 2017/5/4

class FansItem(Item):
    """ 粉丝列表 """
    def __init__(self):
        self._id = ''  # 用户ID
        self.fans = ''  # 粉丝