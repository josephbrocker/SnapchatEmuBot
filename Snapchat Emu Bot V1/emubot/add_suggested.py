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

                rlim = 0

                snap.sign_in(*info)

                print("%s %s SIGNED IN (%s)" % (snap.adbid, snap.emuid, info[0]))

                step = 1

            # Step 1: Open friending page and look for keyword.

            if step == 1:
                keyw = data.usernames.get()
                
                try:
                    snap.add_through_keyword_new_v1(keyw)

                    step = 2
                
                except errors.UIA.NOT_FOUND:
                    
                    snap.add_through_keyword_new_v2(keyw)

                    step = 4

            # Step 2: Add all suggested search results until target add
            # count is met, or a ratelimit is found.

            if step == 2:
                snap.add_suggested_search_result_new_v1()

                if (adds := adds + 1) >= ac or rlim:
                    step = 3

                print("%s %s USR ADDED (%s)" % (snap.adbid, snap.emuid, adds))

                q.put("+")

                time.sleep(to)
            
            # Step 3: Close ADB connection, quit and remove emulator
            # instance, set step back to 0.

            if step == 3:
                snap.close()

                step = 0
            
            # Step 4: Add all suggested search results until target add
            # count is met, or a ratelimit is found. (V2)

            if step == 4:
                snap.add_suggested_search_result_new_v2()

                if (adds := adds + 1) >= ac or rlim:
                    step = 3
                
                print("%s %s USR ADDED (%s)" % (snap.adbid, snap.emuid, adds))

                q.put("+")

        except errors.ACC.PERM_LOCK:
            step = 3

            print("%s %s ACC.PERM_LOCK" % (snap.adbid, snap.emuid))

        except errors.ACC.TIMED_OUT:
            data.accounts.put(info)
            step = 3

            print("%s %s ACC.TIMED_OUT" % (snap.adbid, snap.emuid))

        except errors.ADB.TIMED_OUT:
            step = 3

            print("%s %s ADB.TIMED_OUT" % (snap.adbid, snap.emuid))

        except errors.ADD.RATELIMIT:
            step = 3

            print("%s %s ADD.RATELIMIT" % (snap.adbid, snap.emuid))

        except errors.ADD.NOT_FOUND:
            step = 1
            
            print("%s %s ADD.NOT_FOUND" % (snap.adbid, snap.emuid))

        except errors.EMU.TIMED_OUT:
            data.accounts.put(info)
            step = 3

            print("%s %s EMU.TIMED_OUT" % (snap.adbid, snap.emuid))

        except errors.EMU.SOFT_LOCK:
            data.accounts.put(info)
            step = 3

            print("%s %s EMU.SOFT_LOCK" % (snap.adbid, snap.emuid))

        except errors.UIA.TIMED_OUT:
            data.accounts.put(info)
            step = 3

            print("%s %s UIA.TIMED_OUT" % (snap.adbid, snap.emuid))

        except errors.UIA.NOT_FOUND as error:
            data.accounts.put(info)
            step = 3

            print("%s %s UIA.NOT_FOUND" % (snap.adbid, snap.emuid))
            print("\t%s" % error)
        
        except Exception as error:
            data.accounts.put(info)
            step = 3

            print("%s %s UNDEFINED_ERR" % (snap.adbid, snap.emuid))
            print("\t%s" % error)


def thread_2(q):
    start_time = time.time()
    total_adds = 0

    while True:
        added = []

        while True:

            try:
                added.append(q.get(block=False if len(added) else True))

                total_adds += 1

            except queue.Empty:
                break
        
        diff = int(3600 / (time.time() - start_time) * total_adds)

        print("%s adds per hour. (%s total)" % (diff, total_adds))


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
    
    lq = queue.Queue()  # Queue for logging adds

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