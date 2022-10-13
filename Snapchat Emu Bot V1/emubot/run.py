import os
import re
import signal
import subprocess
import sys
import time


def kill_all_ldplayer_processes():
    mycmd = subprocess.run(
        [
            "tasklist"
        ], 
        capture_output=True, 
        encoding="utf-8"
    )

    tasks = re.findall("dnplayer.exe\s*([0-9]+) .*", mycmd.stdout)

    for pid in tasks:
        os.kill(int(pid), signal.SIGTERM)


if __name__ == "__main__":

    cmd = sys.argv[1:]

    run = True

    while run:

        # Start

        p = subprocess.Popen(
            [
                "python",
                *cmd
            ],
            stdin=subprocess.PIPE,
            shell=True
        )

        # Sleep

        try:
            time.sleep(3600 * 4)

        except KeyboardInterrupt:
            run = False

        # Stop

        p.stdin.write(b':peepoStop:\n')
        p.stdin.flush()

        # Wait

        p.wait()

        # Kill

        kill_all_ldplayer_processes()
