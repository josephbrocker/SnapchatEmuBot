import random
import re
import subprocess




with open("blocked_terms.txt") as f:
    blocked_terms = f.read().strip().lower().split("\n")


def remove_all_emus():
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

        i = emulator[0]
        n = emulator[1]

        if i == '0':
            continue

        if n == "DONT-DELETE":
            continue

        subprocess.run(["ldconsole", "remove", "--name", n])

        print("removed %s" % n)


def get_random_str(length=3):
    chars = "abcdefghijklmnopqrstuvwxyz0123456789"

    return "".join([random.choice(chars) for _ in range(length)])


def name_check(name):
    """ Remove all weird shit from display name, extract words and check
    against blocked terms.

    TODO: This is a bandaid fix, improve later.

    """
    
    clean = name.encode("ascii", errors="ignore").decode("ascii")

    clean = "".join([c or " " for c in clean if not c.isdigit()])
    
    words = re.findall(r"[^\W\d][\w'-]*(?<=\w)", clean)

    for word in words:

        if word.lower() in blocked_terms:
            return False
    
    return True
    

if __name__ == "__main__":
    with open("test_names.txt", encoding="utf-8") as f:
        for line in f:
            line = line.strip()

            if not line:
                continue

            print("[%s]" % line, name_check(line))