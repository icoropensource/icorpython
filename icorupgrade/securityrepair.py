# -*- coding: utf-8 -*-
from icorlib.icorinterface import *
import icorlib.icorsecurity as ICORSecurity
import os

import icorexceptions


def SecurityRepair(alog=None):
    if 1:
        ICORSecurity.RepairUsersInUserGroups(alog=alog)
    if 1:
        ICORSecurity.RepairUserGroupsInUsers(alog=alog)
    if 1:
        ICORSecurity.RepairGroupsInUserGroups(alog=alog)
    if 1:
        ICORSecurity.RepairUserGroupsInGroups(alog=alog)
    if 1:
        ICORSecurity.RepairItemGroupsInGroups(alog=alog)
    if 1:
        ICORSecurity.RepairGroupsInItemGroups(alog=alog)
    if 1:
        ICORSecurity.RepairProfileInUserGroups(alog=alog)
    if 1:
        ICORSecurity.RepairProfileInItemGroups(alog=alog)
    if 1:
        ICORSecurity.RepairUserGroupsInProfile(alog=alog)
    if 1:
        ICORSecurity.RepairItemGroupsInProfile(alog=alog)
