# -*- coding: utf-8 -*-
import sys
import time

import icorapi

UID = 0


def Test_API_ClassExists(amax=1000):
    di, dp = {}, {}
    adt1a = time.clock()
    for cid in range(1, amax + 1):
        di[cid] = icorapi.ClassExists(UID, cid, usepg=0)
    adt1b = time.clock()
    adt2a = time.clock()
    for cid in range(1, amax + 1):
        dp[cid] = icorapi.ClassExists(UID, cid, usepg=1)
    adt2b = time.clock()
    wgood = 1
    for cid in range(1, amax + 1):
        if di[cid] != dp[cid]:
            wgood = 0
    ti, tp = adt1b - adt1a, adt2b - adt2a
    print 'Test_API_ClassExists [%d]=%d - ICOR: %0.5f, PG: %0.5f, ratio: %0.2f' % (amax, wgood, ti, tp, ti / tp)


if __name__ == '__main__':
    if 1:
        Test_API_ClassExists()
