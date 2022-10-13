import queue
import subprocess
import time
import uuid

import manager_emu


_q1 = queue.Queue()
_q2 = queue.Queue()
_q3 = queue.Queue()

cache = {}


def run_until_queue_empty(func):
    """ Runs `func` until it throw a queue.Empty exception.
    """

    def wrapper():
        while True:

            try:
                func()

            except queue.Empty:
                break

    return wrapper


@run_until_queue_empty
def _disconnect():
    """ Quit and remove LDP instances by emuid.
    """

    emuid = _q3.get(block=False)

    subprocess.run(
        [
            "ldconsole", 
            "quit", 
            "--name", 
            emuid
        ]
    )

    time.sleep(1)

    subprocess.run(
        [
            "ldconsole", 
            "remove", 
            "--name", 
            emuid
        ]
    )


def _update_new():
    try:
        _q1.get(block=False)
    
    except queue.Empty:
        return
    
    emuid = uuid.uuid4().hex

    subprocess.run(
        [
            "ldconsole", 
            "copy", 
            "--name", 
            emuid, 
            "--from", 
            "0"
        ]
    )

    time.sleep(1)

    # Find

    s_ret = subprocess.run(
        [
            "ldconsole", 
            "list2"
        ], 
        capture_output=True, 
        encoding="utf-8"
    )

    for emulator in s_ret.stdout.split("\n"):

        if not emulator:
            continue

        emulator = emulator.split(",")

        try:
            i = emulator[0]
            n = emulator[1]
        
        except IndexError:
            continue

        if n == emuid:
            adbid = "127.0.0.1:%s" % (5555 + int(i)*2)
            break
        
    else:
        manager_emu._q1.put("OK")
        return
    
    # Launch

    subprocess.run(
        [
            "ldconsole", 
            "launch", 
            "--name", 
            emuid
        ]
    )

    # Pass instance to cache

    cache[emuid] = {
        "emuid": emuid,
        "adbid": adbid,
        "time_": time.time()
    }


def _update_old():
    """ Update cache with new instance reports
    """

    s_ret = subprocess.run(
        [
            "ldconsole", 
            "list2"
        ], 
        capture_output=True, 
        encoding="utf-8"
    )

    for emulator in s_ret.stdout.split("\n"):

        if not emulator:
            continue

        emulator = emulator.split(",")

        try:
            emuid = emulator[1]
            start = emulator[4]
        
        except IndexError:
            continue

        if not cache.get(emuid):
            continue

        adbid = cache[emuid]["adbid"]

        if int(start) == 1:
            del cache[emuid]
            _q2.put((emuid, adbid))
            continue

        old_t = cache[emuid]["time_"]
        new_t = time.time()

        if (new_t - old_t) < 60:
            continue

        del cache[emuid]

        _q3.put(emuid)
        _q1.put("OK")


def thread():
    while True:

        # Prioritize to free up resources.
        _disconnect()

        _update_new()

        _update_old()

        time.sleep(1)