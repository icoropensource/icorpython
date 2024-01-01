# -*- coding: utf-8 -*-
import sys
import os
import time
import uuid

VERBOSE = 1


class StatsManager(object):

    def __init__(self, app):
        self.app = app

    def GetUUID(self, aprefix='', asufix=''):
        return aprefix + uuid.uuid4().hex + asufix
