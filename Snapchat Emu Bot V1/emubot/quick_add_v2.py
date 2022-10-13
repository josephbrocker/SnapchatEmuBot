import data
import errors
import snapchat
import time
import utils


class Context:

    MAX_ADD = 100
    MAX_ERR = 5

    def __init__(self, q):
        self.stat = q  # stats queue

        self.info = None
        self.snap = None

        self.sugg = []

        self.adds = []
        self.skip = []

        self.prev = None
    
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
    """ Trigger sync by opening friending presenter.
    """

    context.snap.open_add_friends_presenter()
    
    time.sleep(3)  # TODO: Find a better way ...


def _FUNC_03(context):
    """ Get suggested users, check for error and add.
    """

    corr = set(context.skip) - set(context.adds)
    
    for user in corr:
        context.skip.remove(user)
        context.adds.append(user)
    
    sugg = context.snap.db_get_suggested_users()

    if context.prev:
        if context.prev in sugg:
            context.skip.append(context.prev)
        else:
            context.adds.append(context.prev)
            context.stat_update(context.prev)

    print("%s %s ADD_COUNT (%s)" % (
        context.snap.adbid, context.snap.emuid, len(context.adds)))
    
    if not sugg:
        raise errors.ADD.NO_RESULT()

    if len(context.skip) >= Context.MAX_ERR:
        raise errors.ADD.ERR_COUNT()
    
    if len(context.adds) >= Context.MAX_ADD:
        raise errors.ADD.ADD_COUNT()
    
    for user in sugg:
        if user in context.skip:
            continue

        info = user.split("|")

        uid = info[0]
        usn = info[1]
        dpn = info[2]

        if not utils.name_check(dpn):
            continue
        
        break  # New user found
    
    else:
        raise errors.ADD.NO_RESULT()
    
    context.snap.add_with_friending_intent(uid, usn)

    context.prev = user

    print("%s %s FRIENDING (%s)" % (
        context.snap.adbid, context.snap.emuid, context.prev))
    
    time.sleep(3)  # TODO: Find a better way ...


def thread_1(q):

    step = 0

    while True:

        try:
            if step == 0:
                context = Context(q)

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


def thread_2(q):
    start_time = time.time()

    total_adds = 0
    lastupdate = 0

    while True:

        try:
            q.get(block=False if total_adds else True)
            total_adds += 1

        except queue.Empty:
            time.sleep(1)

        if total_adds < 1:
            continue

        if lastupdate and time.time() - lastupdate < 30:
            continue

        rt = time.time() - start_time

        ah = total_adds / rt * 3600

        print("%s adds per hour. (%s total) rt: %s seconds" % (
            int(ah), total_adds, int(rt)))

        lastupdate = time.time()


if __name__ == "__main__":
    import queue
    import sys
    import threading

    tc = 1  # Thread count

    for arg in sys.argv[1:]:
        arg = arg.split("=")

        if len(arg) != 2:
            raise Exception("Error passing command-line arguments.")

        elif arg[0] == "-tc":
            tc = int(arg[1])
    
    q = queue.Queue()
    
    t = threading.Thread(target=thread_2, daemon=True, args=(q,))
    t.start()

    for _ in range(tc):
        t = threading.Thread(target=thread_1, daemon=True, args=(q,))
        t.start()
    
    try:
        input()

    except KeyboardInterrupt:
        pass
