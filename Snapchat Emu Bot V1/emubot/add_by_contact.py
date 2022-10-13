import data
import errors
import snapchat
import time
import uuid


class Context:

    MAX_AMT = 500

    def __init__(self, q):
        self.stat = q  # stats queue

        self.adds_1 = []
        self.adds_2 = []

        self.info = None
        self.snap = None
    
    def stat_update(self, uid):
        self.stat.put(uid)


def _FUNC_01(context):
    """ Get account data, setup instance and log in.
    """
    
    info = data.accounts.get()
    context.info = info

    snap = snapchat.Snapchat()
    context.snap = snap

    snap.sign_in(*info)

    print("%s %s SIGNED IN (%s)" % (snap.adbid, snap.emuid, info[0]))


def _FUNC_02(context):
    """ Add contact with phone to android contacts.
    """

    info = data.phone_numbers.get()

    context.snap.add_contact(info)

    print("%s %s PHONE ADD (%s)" % (
        context.snap.adbid, context.snap.emuid, info))


def _FUNC_03(context):
    """ Trigger a db sync and dump results from db.
    """

    