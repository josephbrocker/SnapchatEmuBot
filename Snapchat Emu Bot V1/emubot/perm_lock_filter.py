import queue
import threading

import data
import errors
import snapchat


def thread_1(q1: queue.Queue, q2: queue.Queue):

    step = 0

    while True:

        try:

            if step == 0:

                snap = snapchat.Snapchat()

                info = data.accounts.get()

                snap.sign_in(*info)

                q1.put(info)

                print("%s %s SIGNED IN (%s)" % (
                    snap.adbid, snap.emuid, info[0]))

                step = 1

            if step == 1:
                snap.close()

                step = 0
    
        except errors.ACC.PERM_LOCK:
            q2.put(info)

            step = 1

            print("%s %s ACC.PERM_LOCK" % (snap.adbid, snap.emuid))
        
        except errors.ACC.TIMED_OUT:
            data.accounts.put(info)

            step = 1

            print("%s %s ACC.TIMED_OUT" % (snap.adbid, snap.emuid))

        except errors.ADB.TIMED_OUT:
            data.accounts.put(info)

            step = 1

            print("%s %s ADB.TIMED_OUT" % (snap.adbid, snap.emuid))

        except errors.EMU.TIMED_OUT:
            data.accounts.put(info)

            step = 1

            print("%s %s EMU.TIMED_OUT" % (snap.adbid, snap.emuid))

        except errors.EMU.SOFT_LOCK:
            data.accounts.put(info)

            step = 1

            print("%s %s EMU.SOFT_LOCK" % (snap.adbid, snap.emuid))

        except errors.UIA.TIMED_OUT:
            data.accounts.put(info)

            step = 1

            print("%s %s UIA.TIMED_OUT" % (snap.adbid, snap.emuid))

        except errors.UIA.NOT_FOUND as error:
            data.accounts.put(info)

            step = 1

            print("%s %s UIA.NOT_FOUND" % (snap.adbid, snap.emuid))
            print("\t%s" % error)
        
        except Exception as error:
            data.accounts.put(info)

            step = 1

            print("%s %s UNDEFINED_ERR" % (snap.adbid, snap.emuid))
            print("\t%s" % error)


def thread_2(q1: queue.Queue):

    while True:
        info = q1.get()

        with open("LOGIN_SUCCESS.txt", "a") as f:
            f.write(":".join(info) + "\n")


def thread_3(q2: queue.Queue):

    while True:
        info = q2.get()

        with open("LOGIN_FAILURE.txt", "a") as f:
            f.write(":".join(info) + "\n")


if __name__ == "__main__":
    import sys
    import threading

    tc = 1

    for arg in sys.argv[1:]:
        arg = arg.split("=")

        if len(arg) != 2:
            raise Exception("Error passing command-line arguments.")

        elif arg[0] == "-tc":
            tc = int(arg[1])
        
    q1 = queue.Queue()
    q2 = queue.Queue()

    t2 = threading.Thread(target=thread_2, args=(q1,), daemon=True)
    t2.start()

    t3 = threading.Thread(target=thread_3, args=(q2,), daemon=True)
    t3.start()

    for _ in range(tc):
        t = threading.Thread(target=thread_1, args=(q1, q2), daemon=True)
        t.start()
    
    try:
        input()

    except KeyboardInterrupt:
        pass