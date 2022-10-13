import client_for_api
import data
import errors
import snapchat
import time


class Context:

    MAX_ERR = 5
    MAX_ADD = 100

    def __init__(self):
        self.info = None
        self.snap = None

        self.adds = []
        self.errs = []

        self.prev = None


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
    """ Trigger sync by opening friending presenter.
    """

    context.snap.open_add_friends_presenter()


def _FUNC_03(context):
    """ Get usn and uid, then add user with intent.
    """

    usn = data.usernames.get()
    uid = client_for_api.get_uid_for_usn(usn)

    if context.prev:
        lnkt = context.snap.db_get_friend_link_type(context.prev)

        if not lnkt:
            context.errs.append(uid)
        
        elif int(lnkt) == 0:  # confirmed
            context.adds.append(uid)

        elif int(lnkt) == 1:  # requested
            context.adds.append(uid)
        
        elif int(lnkt) == 4:  # requested (suggested)
            context.adds.append(uid)

        else:
            context.errs.append(uid)

    print("%s %s ADD_COUNT (%s)" % (
        context.snap.adbid, context.snap.emuid, len(context.adds)))

    if len(context.errs) >= Context.MAX_ERR:
        raise errors.ADD.ERR_COUNT()
    
    if len(context.adds) >= Context.MAX_ADD:
        raise errors.ADD.ADD_COUNT()

    context.snap.add_with_friending_intent(uid, usn)

    context.prev = uid
    
    print("%s %s FRIENDING (%s)" % (
        context.snap.adbid, context.snap.emuid, context.prev))
    
    time.sleep(3)  # TODO: Find a better way ...


def thread_1():

    step = 0

    while True:

        try:
            if step == 0:
                context = Context()

                step = 1
            
            if step == 1:
                _FUNC_01(context)

                step = 2
            
            if step == 2:
                _FUNC_02(context)

                step = 3
            
            if step == 3:
                _FUNC_03(context)
            
            if step == 4:
                context.snap.close()

                step = 0

        except errors.ADD.ERR_COUNT:
            step = 4

            print("%s %s ADD.ERR_COUNT" % (
                context.snap.adbid, context.snap.emuid))

        except errors.ADD.ADD_COUNT:
            step = 4

            print("%s %s ADD.ADD_COUNT" % (
                context.snap.adbid, context.snap.emuid))
            
        except errors.ADD.NO_RESULT:
            step = 4

            print("%s %s ADD.NO_RESULT" % (
                context.snap.adbid, context.snap.emuid))

        except errors.ACC.PERM_LOCK:
            step = 4

            print("%s %s ACC.PERM_LOCK" % (
                context.snap.adbid, context.snap.emuid))
        
        except errors.ACC.TIMED_OUT:
            data.accounts.put(context.info)
            step = 4

            print("%s %s ACC.TIMED_OUT" % (
                context.snap.adbid, context.snap.emuid))
        
        except errors.ADB.TIMED_OUT:
            step = 4

            print("%s %s ADB.TIMED_OUT" % (
                context.snap.adbid, context.snap.emuid))
        
        except errors.EMU.TIMED_OUT:
            data.accounts.put(context.info)
            step = 4

            print("%s %s EMU.TIMED_OUT" % (
                context.snap.adbid, context.snap.emuid))
        
        except errors.EMU.SOFT_LOCK:
            data.accounts.put(context.info)
            step = 4

            print("%s %s EMU.SOFT_LOCK" % (
                context.snap.adbid, context.snap.emuid))
        
        except errors.UIA.TIMED_OUT:
            step = 4

            print("%s %s UIA.TIMED_OUT" % (
                context.snap.adbid, context.snap.emuid))
        
        except errors.UIA.NOT_FOUND as error:
            step = 4

            print("%s %s UIA.NOT_FOUND" % (
                context.snap.adbid, context.snap.emuid))
            print("\t%s" % error)
        
        except Exception as error:
            step = 4

            print("%s %s UNDEFINED_ERR" % (
                context.snap.adbid, context.snap.emuid))
            print("\t%s" % error)


if __name__ == "__main__":
    import sys
    import threading

    t = threading.Thread(target=thread_1, daemon=True)
    t.start()
    
    try:
        input()

    except KeyboardInterrupt:
        pass