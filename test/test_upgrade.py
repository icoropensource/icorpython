# -*- coding: utf-8 -*-
from icorupgrade import upgrade
import icordbmain.adoutil as ADOLibInit


def Main():
    aupgrade = upgrade.ICORUpgrade()
    if 0:
        aupgrade.DBAccessMarkSimilar()
    if 0:
        aupgrade.DBAccessMoveHosts()
    if 0:
        aupgrade.CheckDBAccess(verbose=1)
    if 0:
        aupgrade.CheckDBAccessByStruct(verbose=1)
    if 0:
        aupgrade.MethodsCorrectBackTicks()
    if 0:
        aupgrade.CheckNewAPI()
    if 0:
        aupgrade.SecurityRemoveUnusedItems()
    if 0:
        aupgrade.ModernizeWebsite('6latki')
    if 1:
        aupgrade.ModernizeWebsites(lexclude=['6latki', ])


if __name__ == '__main__':
    Main()
