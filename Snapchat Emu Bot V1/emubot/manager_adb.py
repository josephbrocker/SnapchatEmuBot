import queue
import subprocess
import time

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
    """ Disconnect old / existing ADB connections.
    """

    adbid = _q3.get(block=False)

    subprocess.run(
        [
            "adb", 
            "disconnect", 
            adbid
        ]
    )


@run_until_queue_empty
def _update_new():
    """ Update cache with new devices.
    """

    q_ret = _q1.get(block=False)

    emuid = q_ret[0]
    adbid = q_ret[1]

    cache[adbid] = {
        "emuid": emuid,
        "adbid": adbid,
        "time_": time.time()
    }


def _update_old():
    """ Update cache with old devices.
    """

    s_ret = subprocess.run(
        [
            "adb", 
            "devices"
        ], 
        capture_output=True, 
        encoding="utf-8"
    )

    for device in s_ret.stdout.split("\n"):

        if not device.startswith("127.0.0.1"):
            continue

        adbid, status = device.split("\t")

        if not cache.get(adbid):
            continue
        
        emuid = cache[adbid]["emuid"]

        if status == "device":
            del cache[adbid]
            _q2.put((emuid, adbid))
            continue
        
        old_t = cache[adbid]["time_"]
        new_t = time.time()

        if (new_t - old_t) < 60:
            continue

        del cache[adbid]

        manager_emu._q3.put((emuid, adbid))
        manager_emu._q1.put("OK")


def thread():
    while True:

        # Prioritize to free up resources.
        _disconnect()

        _update_new()

        _update_old()

        time.sleep(1)
