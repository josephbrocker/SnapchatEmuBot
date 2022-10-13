import queue
import threading
import time

import data
import errors
import snapchat


def thread_1(q, bc, bs):
    step = 0

    while True:

        try:

            # Step 0: Create emu instance, get snapchat acc, set 
            # counters and login.

            if step == 0:
                snap = snapchat.Snapchat()
                info = data.accounts.get()

                amt1 = 0
                amt2 = 0

                adds = []

                errs = 0
                rlim = 0

                snap.sign_in(*info)

                print("%s %s SIGNED IN (%s)" % (snap.adbid, snap.emuid, info[0]))

                step = 1
            
            # Step 1: Open memories, navigate to camera roll and select 
            # the snap that we want to send.
            
            if step == 1:
                snap.open_memories()
                snap.navigate_to_camera_roll()
                snap.select_snap_from_memories()

                step = 2
            
            # Step 2: Add recipient to snap, increment the counter by 1 
            # until it reaches 20.
            
            if step == 2:
                recp = data.usernames.get()

                snap.add_recipient_to_snap(recp)

                print("%s %s SEARCH OK (%s)" % (snap.adbid, snap.emuid, recp))

                errs = 0  # Reset search error count

                adds.append(recp)

                if (amt1 := amt1 + 1) % bs == 0:
                    step = 3
            
            # Step 3: Send snap to recipients, increment the counter by 
            # 1 until it reaches 2. Reset counter for step 2.
            
            if step == 3:
                snap.send_snap_to_recipients()

                print("%s %s SNAP SENT (%s)" % (snap.adbid, snap.emuid, amt1))

                for recp in adds:
                    q.put(recp)
                    data.usernames.remove(recp)

                adds = []

                if (amt2 := amt2 + 1) >= bc or rlim:
                    step = 4
                else:
                    step = 1
            
            # Close ADB connection, quit and remove emulator instance, 
            # set step back to 0.
            
            if step == 4:
                snap.close()

                step = 0

        except errors.ACC.PERM_LOCK:
            step = 4

            print("%s %s ACC.PERM_LOCK" % (snap.adbid, snap.emuid))

        except errors.ACC.TIMED_OUT:
            data.accounts.put(info)
            step = 4

            print("%s %s ACC.TIMED_OUT" % (snap.adbid, snap.emuid))

        except errors.ADB.TIMED_OUT:
            step = 4

            print("%s %s ADB.TIMED_OUT" % (snap.adbid, snap.emuid))

        except errors.ADD.RATELIMIT:
            if len(adds):
                step = 3
                rlim = 1
            else:
                step = 4

            print("%s %s ADD.RATELIMIT" % (snap.adbid, snap.emuid))

        except errors.ADD.NOT_FOUND:
            if (errs := errs + 1) == 5:
                if len(adds):
                    step = 3
                    rlim = 1
                else:
                    step = 4
                
            snap.select_all()
            
            print("%s %s ADD.NOT_FOUND" % (snap.adbid, snap.emuid))
        
        except errors.ADD.NO_SEND_1:
            step = 1

            amt1 = amt1 - len(adds)
            adds = []

            print("%s %s ADD.NO_SEND_1" % (snap.adbid, snap.emuid))
        
        except errors.ADD.NO_SEND_2:
            step = 4

            print("%s %s ADD.NO_SEND_2" % (snap.adbid, snap.emuid))

        except errors.ADD.NO_SEND_3:
            step = 4

            print("%s %s ADD.NO_SEND_3" % (snap.adbid, snap.emuid))
        
        except errors.CV2.NOT_FOUND:
            step = 4

            print("%s %s CV2.NOT_FOUND" % (snap.adbid, snap.emuid))

        except errors.EMU.TIMED_OUT:
            data.accounts.put(info)
            step = 4

            print("%s %s EMU.TIMED_OUT" % (snap.adbid, snap.emuid))

        except errors.EMU.SOFT_LOCK:
            data.accounts.put(info)
            step = 4

            print("%s %s EMU.SOFT_LOCK" % (snap.adbid, snap.emuid))
        
        except errors.UIA.TIMED_OUT:
            data.accounts.put(info)
            step = 4

            print("%s %s UIA.TIMED_OUT" % (snap.adbid, snap.emuid))

        except errors.UIA.NOT_FOUND as error:
            data.accounts.put(info)
            step = 4

            print("%s %s UIA.NOT_FOUND" % (snap.adbid, snap.emuid))
            print("\t%s" % error)
        
        except Exception as error:
            data.accounts.put(info)
            step = 4

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

        with open("log.txt", "a") as f:
            f.write("\n".join(added) + "\n")


if __name__ == "__main__":
    import sys

    tc = 1   # Thread count
    bc = 1   # Batch count
    bs = 20  # Batch size

    for arg in sys.argv[1:]:
        arg = arg.split("=")

        if len(arg) != 2:
            raise Exception("Error passing command-line arguments.")

        elif arg[0] == "-tc":
            tc = int(arg[1])
        
        elif arg[0] == "-bc":
            bc = int(arg[1])
        
        elif arg[0] == "-bs":
            bs = int(arg[1])

    lq = queue.Queue()  # Queue for logging adds

    t = threading.Thread(target=thread_2, args=(lq,), daemon=True)
    t.start()

    for _ in range(tc):
        t = threading.Thread(target=thread_1, args=(lq, bc, bs), daemon=True)
        t.start()
    
    try:
        input()

    except KeyboardInterrupt:
        pass
    
    data.usernames.exit_thread()
