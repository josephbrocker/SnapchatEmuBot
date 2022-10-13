import data
import errors
import os
import snapchat
import time


ATTACHMENT_URL = None

try:
    with open("attachment_url.txt") as f:
        ATTACHMENT_URL = f.read().strip()

except FileNotFoundError:
    pass


class Context:

    def __init__(self):
        self.info = None
        self.snap = None

        self.snaps = []
        self.users = []


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
    """ Get upload data and convert to Snap objects.
    """

    media = os.listdir("snaps")
    snaps = []

    for f in media:
        snaps.append(snapchat.Snap("snaps/%s" % f))
    
    context.snaps = snaps


def _FUNC_03(context):
    """ Get Snap objects and push them to the device.
    """

    for s in context.snaps:
        context.snap.push_snap_to_emulator(s)
    
    print("%s %s FILES RDY (%s)" % (
        context.snap.adbid, context.snap.emuid, len(context.snaps)))


def _FUNC_04(context):
    """ Get user ids from friends w/ friendLinkType 0.
    """

    users = context.snap.db_get_user_ids()

    print("%s %s FRNDS GET (%s)" % (
        context.snap.adbid, context.snap.emuid, len(users)))

    context.users = users


def _FUNC_05(context):
    """ Push snap to the live view.
    """

    snap = context.snaps[0]

    context.snap.push_snap_to_liveview(snap, ATTACHMENT_URL)

    print("%s %s MEDIA RDY (%s)" % (
        context.snap.adbid, context.snap.emuid, snap.name))


def _FUNC_06(context):
    """ Toggle the add friend menu.
    """

    context.snap.send_snap_open_select()

    time.sleep(3)

    context.snap.send_snap_exit_select()

    time.sleep(3)


def _FUNC_07(context):
    """ Create the shortcut to group recipients under.
    """

    stlst = context.snap.db_set_shortcut()

    print("%s %s STLST SET (%s)" % (
        context.snap.adbid, context.snap.emuid, stlst))
    
    context.stlst = stlst


def _FUNC_08(context):
    """ Add up to 200 recipients to the SendToList.
    """

    users = context.users[:200]

    context.snap.db_add_user_ids(context.stlst, users)

    print("%s %s FRNDS SET (%s)" % (
        context.snap.adbid, context.snap.emuid, len(users)))


def _FUNC_09(context):
    """ Open friend menu, select all under shortcut.
    """

    context.snap.send_snap_open_select()

    time.sleep(3)

    context.snap.send_snap_to_shortcut()

    time.sleep(3)


def _FUNC_10(context):
    """ Send the snap to all the selected recipients.
    """

    context.snap.send_snap_send_button()

    print("%s %s SNAP SENT" % (
        context.snap.adbid, context.snap.emuid))


def _FUNC_11(context):
    """ Close ADB, exit emulator etc.
    """

    context.snap.close()


def thread_1():

    step = 0

    while True:

        try:
            if step == 0:
                context = Context()

                step = 1

            if step == 1:  # Get account data, create instance.
                _FUNC_01(context)

                step = 2

            if step == 2:  # Get snaps
                _FUNC_02(context)

                if context.snaps:
                    step = 3

                else:
                    step = 11

            if step == 3:  # Set snaps
                _FUNC_03(context)

                step = 4

            if step == 4:  # Get users
                _FUNC_04(context)

                if context.users:
                    step = 5
                
                else:
                    step = 11

            if step == 5:  # Push a snap to live / camera view.
                _FUNC_05(context)

                step = 6

            if step == 6:  # Toggle send to menu.
                _FUNC_06(context)

                step = 7

            if step == 7:  # Create new shortcut.
                _FUNC_07(context)

                step = 8

            if step == 8:  # Add up to 200 recipients to stlst.
                _FUNC_08(context)

                step = 9

            if step == 9:  # Select all recipients of shortcut.
                _FUNC_09(context)

                step = 10

            if step == 10:  # Send snap.
                _FUNC_10(context)

                del context.users[:200]

                if context.users:
                    step = 5
                
                else:
                    del context.snaps[0]

                    if context.snaps:
                        step = 4
                    
                    else:
                        step = 11

                        time.sleep(10)
            
            if step == 11:  # Close and exit ADB, instance etc.
                _FUNC_11(context)

                step = 0

        except errors.ACC.PERM_LOCK:
            step = 11

            print("%s %s ACC.PERM_LOCK" % (
                context.snap.adbid, context.snap.emuid))
        
        except errors.ACC.TIMED_OUT:
            data.accounts.put(context.info)
            step = 11

            print("%s %s ACC.TIMED_OUT" % (
                context.snap.adbid, context.snap.emuid))
        
        except errors.ADB.TIMED_OUT:
            step = 11

            print("%s %s ADB.TIMED_OUT" % (
                context.snap.adbid, context.snap.emuid))
        
        except errors.EMU.TIMED_OUT:
            data.accounts.put(context.info)
            step = 11

            print("%s %s EMU.TIMED_OUT" % (
                context.snap.adbid, context.snap.emuid))
        
        except errors.EMU.SOFT_LOCK:
            data.accounts.put(context.info)
            step = 11

            print("%s %s EMU.SOFT_LOCK" % (
                context.snap.adbid, context.snap.emuid))
        
        except errors.UIA.TIMED_OUT:
            step = 11

            print("%s %s UIA.TIMED_OUT" % (
                context.snap.adbid, context.snap.emuid))
        
        except errors.UIA.NOT_FOUND as error:
            step = 11

            print("%s %s UIA.NOT_FOUND" % (
                context.snap.adbid, context.snap.emuid))
            print("\t%s" % error)
        
        except Exception as error:
            step = 11

            print("%s %s UNDEFINED_ERR" % (
                context.snap.adbid, context.snap.emuid))
            print("\t%s" % error)


if __name__ == "__main__":
    import sys
    import threading

    tc = 1  # Thread count

    for arg in sys.argv[1:]:
        arg = arg.split("=")

        if len(arg) != 2:
            raise Exception("Error passing command-line arguments.")

        elif arg[0] == "-tc":
            tc = int(arg[1])

    for _ in range(tc):
        t = threading.Thread(target=thread_1, daemon=True)
        t.start()
    
    try:
        input()

    except KeyboardInterrupt:
        pass