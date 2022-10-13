import queue
import threading
import time

import data
import errors
import markov_usn_gen
import snapchat
import utils


def thread_1(q1, q2, bc, bs, strict, noadd, use_email, export_proxy):
    step = 0

    amt1 = 0
    amt2 = 0

    adds = []

    errs = 0
    rlim = 0

    while True:

        try:

            # Step 0: Create snap instance, user details and attempt to 
            # sign up.

            if step == 0:

                snap = snapchat.Snapchat()

                # f_name = random.choice(names)
                f_name = markov_usn_gen.generate_name(6, 10)
                l_name = "."

                username = "%s%s" % (f_name, utils.get_random_str(3))
                password = "blackops1"
                
                if use_email:
                    email, email_pass = data.emails.get()

                else:
                    email = "%s@gmail.com" % username

                snap.sign_up(username, password, email, f_name, l_name)

                print("%s %s SIGNED UP (%s)" % (
                    snap.adbid, snap.emuid, username))

                amt1 = 0
                amt2 = 0

                adds = []

                errs = 0
                rlim = 0

                if noadd:
                    step = 5
                else:
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

                errs = 0

                adds.append(recp)

                if (amt1 := amt1 + 1) % bs == 0:
                    step = 3
            
            # Step 3: Send snap to recipients, increment the counter by 
            # 1 until it reaches 2. Reset counter for step 2.

            if step == 3:

                snap.send_snap_to_recipients()

                print("%s %s SNAP SENT (%s)" % (snap.adbid, snap.emuid, amt1))

                for recp in adds:
                    q1.put(recp)
                    data.usernames.remove(recp)
                
                adds = []

                if (amt2 := amt2 + 1) >= bc or rlim:
                    if not rlim or not strict:
                        q2.put((username, password))
                    step = 4
                else:
                    step = 1

            # Step 4: Add account to export queue if it performed any
            # adds and clean up instance.

            if step == 4:
                snap.close()

                step = 0
            
            # Step 5: -noadd option, add account to export queue after
            # registration.

            if step == 5:
                if use_email:
                    if export_proxy:
                        q2.put((username, password, email, email_pass, snap._proxy))
                    else:
                        q2.put((username, password, email, email_pass))
                else:
                    if export_proxy:
                        q2.put((username, password, snap._proxy))
                    else:
                        q2.put((username, password))

                step = 4

        except errors.ADB.TIMED_OUT:
            step = 4

            print("%s %s ADB.TIMED_OUT" % (snap.adbid, snap.emuid))

        except errors.EMU.TIMED_OUT:
            step = 4

            print("%s %s EMU.TIMED_OUT" % (snap.adbid, snap.emuid))
        
        except errors.UIA.TIMED_OUT:
            step = 4

            print("%s %s UIA.TIMED_OUT" % (snap.adbid, snap.emuid))
        
        except errors.UIA.NOT_FOUND as error:
            step = 4

            print("%s %s UIA.NOT_FOUND" % (snap.adbid, snap.emuid))
            print("\t%s" % error)
        
        except errors.REG.USN_ERROR as error:
            step = 4

            print("%s %s REG.USN_ERROR" % (snap.adbid, snap.emuid))
            print("\t%s" % error)

        except errors.REG.PWD_ERROR as error:
            step = 4

            print("%s %s REG.PWD_ERROR" % (snap.adbid, snap.emuid))
            print("\t%s" % error)
        
        except errors.REG.EMAIL_ERR as error:
            step = 4

            print("%s %s REG.EMAIL_ERR" % (snap.adbid, snap.emuid))
            print("\t%s" % error)
        
        except errors.REG.SUB_ERROR:
            step = 4

            print("%s %s REG.SUB_ERROR" % (snap.adbid, snap.emuid))

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

        except Exception as error:
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


def thread_3(q):
    start_time = time.time()
    total_accs = 0

    while True:
        info = q.get()

        with open("output.txt", "a") as f:
            f.write(":".join(info) + "\n")

        if (total_accs := total_accs + 1) % 5:
            continue

        diff = int(3600 / (time.time() - start_time) * total_accs)

        print("%s accs per hour. (%s total)" % (diff, total_accs))


if __name__ == "__main__":
    import sys

    tc = 1      # Thread count
    bc = 1      # Batch count
    bs = 20     # Batch size
    st = True   # Strict mode
    na = False  # No-Add mode
    ue = False  # Use real emails
    ep = False  # Export proxy

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
        
        elif arg[0] == "-st":
            st = arg[1].lower() != "false"
        
        elif arg[0] == "-na":
            na = arg[1].lower() == "true"
        
        elif arg[0] == "-ue":
            ue = arg[1].lower() == "true"
        
        elif arg[0] == "-ep":
            ep = arg[1].lower() == "true"

    lq = queue.Queue()  # Queue for logging adds
    eq = queue.Queue()  # Export queue

    t2 = threading.Thread(target=thread_2, args=(lq,), daemon=True)
    t2.start()

    t3 = threading.Thread(target=thread_3, args=(eq,), daemon=True)
    t3.start()

    for _ in range(tc):
        t = threading.Thread(
            target=thread_1,args=(lq, eq, bc, bs, st, na, ue, ep), daemon=True)

        t.start()

    try:
        input()

    except KeyboardInterrupt:
        pass
    
    data.usernames.exit_thread()