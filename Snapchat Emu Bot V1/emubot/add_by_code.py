import queue
import threading
import time

import data
import errors
import snapchat

def thread_1(q, ac, to):

    step = 0

    while True:

        try:

            # Step 0: Create emu instance, get snapchat acc, set
            # counters and login.

            if step == 0:
                snap = snapchat.Snapchat()
                info = data.accounts.get()

                adds = 0

                errs = 0

                snap.sign_in(*info)

                print("%s %s SIGNED IN (%s)" % (snap.adbid, snap.emuid, info[0]))

                step = 1
            
            # Step 1: Fetch username, launch intent and add.

            if step == 1:
                name = data.usernames.get()

                snap.add_through_intent(name)

                print("%s %s USERADDED (%s)" % (snap.adbid, snap.emuid, name))

                q.put(name)
                data.usernames.remove(name)

                errs = 0

                if (adds := adds + 1) == ac:
                    step = 2

                else:
                    time.sleep(to)
            
            # Step 2: Close ADB, quit emulator and set step to 0.

            if step == 2:
                snap.close()

                step = 0
        
        except errors.ACC.PERM_LOCK:
            step = 2

            print("%s %s ACC.PERM_LOCK" % (snap.adbid, snap.emuid))
        
        except errors.ACC.TIMED_OUT:
            data.accounts.put(info)
            step = 2

            print("%s %s ACC.TIMED_OUT" % (snap.adbid, snap.emuid))
        
        except errors.ADB.TIMED_OUT:
            step = 2

            print("%s %s ADB.TIMED_OUT" % (snap.adbid, snap.emuid))
        
        except errors.ADD.RATELIMIT:
            step = 2

            print("%s %s ACC.TIMED_OUT" % (snap.adbid, snap.emuid))
        
        except errors.ADD.NOT_FOUND:
            if (errs := errs + 1) == 5:
                step = 2
            
            print("%s %s ADD.NOT_FOUND" % (snap.adbid, snap.emuid))
        
        except errors.ADD.DUPLICATE:
            print("%s %s ADD.DUPLICATE" % (snap.adbid, snap.emuid))
        
        except errors.EMU.TIMED_OUT:
            data.accounts.put(info)
            step = 2

            print("%s %s EMU.TIMED_OUT" % (snap.adbid, snap.emuid))
        
        except errors.EMU.SOFT_LOCK:
            data.accounts.put(info)
            step = 2

            print("%s %s EMU.TIMED_OUT" % (snap.adbid, snap.emuid))
        
        except errors.UIA.TIMED_OUT:
            data.accounts.put(info)
            step = 2

            print("%s %s EMU.TIMED_OUT" % (snap.adbid, snap.emuid))
        
        except errors.UIA.NOT_FOUND as error:
            data.accounts.put(info)
            step = 2

            print("%s %s EMU.TIMED_OUT" % (snap.adbid, snap.emuid))
            print("\t%s" % error)
        
        except Exception as error:
            data.accounts.put(info)
            step = 2

            print("%s %s UNDEFINED_ERR" % (snap.adbid, snap.emuid))
            print("\t%s" % error)


def thread_2(q):
    start_time = time.time()
    total_adds = 0

    time_stamp = 0

    while True:
        added = []

        while True:

            try:
                added.append(q.get(block=False if len(added) else True))

                total_adds += 1

            except queue.Empty:
                break
        
        if time.time() - time_stamp > 30:
        
            diff = int(3600 / (time.time() - start_time) * total_adds)

            print("%s adds per hour. (%s total)" % (diff, total_adds))

            time_stamp = time.time()

        with open("log.txt", "a") as f:
            f.write("\n".join(added) + "\n")


if __name__ == "__main__":
    import sys

    tc = 1   # Thread count
    ac = 20  # Add count
    to = 0   # Time out / sleep in seconds

    for arg in sys.argv[1:]:
        arg = arg.split("=")

        if len(arg) != 2:
            raise Exception("Error passing command-line arguments.")

        elif arg[0] == "-tc":
            tc = int(arg[1])
        
        elif arg[0] == "-ac":
            ac = int(arg[1])
        
        elif arg[0] == "-to":
            to = int(arg[1])
    
    lq = queue.Queue() # Queue for logging adds

    t = threading.Thread(target=thread_2, args=(lq,), daemon=True)
    t.start()

    for _ in range(tc):
        t = threading.Thread(target=thread_1, args=(lq, ac, to), daemon=True)
        t.start()
    
    try:
        input()

    except KeyboardInterrupt:
        pass

    data.usernames.exit_thread()
