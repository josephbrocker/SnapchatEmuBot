import queue
import time

import manager_adb
import manager_ldp


_q1 = queue.Queue()
_q2 = queue.Queue()
_q3 = queue.Queue()


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
def _cleanup():
    """ Coordinate / forward closing tasks to managers.
    """

    q_ret = _q3.get(block=False)

    emuid = q_ret[0]
    adbid = q_ret[1]

    # Stop ADB
    manager_adb._q3.put(adbid)

    # Quit LDP
    manager_ldp._q3.put(emuid)


@run_until_queue_empty
def _forward_ldp_tasks():
    """ Coordinate / forward start tasks for LDP manager.
    """

    _q1.get(block=False)

    manager_ldp._q1.put("OK")


@run_until_queue_empty
def _forward_adb_tasks():
    """ Coordinate / forward start tasks for ADB manager.
    """

    q_ret = manager_ldp._q2.get(block=False)

    emuid = q_ret[0]
    adbid = q_ret[1]

    manager_adb._q1.put((emuid, adbid))


@run_until_queue_empty
def _forward_rdy_tasks():
    """ Forward instances with established ADB connection.
    """

    q_ret = manager_adb._q2.get(block=False)

    emuid = q_ret[0]
    adbid = q_ret[1]

    _q2.put((emuid, adbid))


def thread():
    while True:

        # Prioritize to free up resources.
        _cleanup()
        
        _forward_ldp_tasks()
        
        _forward_adb_tasks()
        
        _forward_rdy_tasks()
        
        time.sleep(1)


def start():
    _q1.put("OK")

    # Wait for instance to be ready.

    q_ret = _q2.get()

    emuid = q_ret[0]
    adbid = q_ret[1]

    return emuid, adbid


def close(emuid, adbid):
    _q3.put((emuid, adbid))
