# -*- coding: utf-8 -*-


class ICORException(Exception):

    def __init__(self, errmsg=''):
        Exception.__init__(self, errmsg)


class ICORExceptionReplication(ICORException):
    pass


class ICORExceptionDBStruct(ICORException):
    pass


class ICORExceptionDBStructObsolete(ICORException):
    pass


class ICORExceptionAPI(ICORException):
    pass


class ICORExceptionAPIObsolete(ICORExceptionAPI):
    pass


class ICORExceptionAPIImplementationPending(ICORExceptionAPI):
    pass


class ICORExceptionDatabase(ICORException):
    pass
