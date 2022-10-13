import cv2
import numpy as np
import subprocess
import threading
import time
import uuid

from lxml import etree

import errors
import manager_emu
import manager_adb
import manager_ldp
import templates
import utils


subprocess.run("adb kill-server && adb start-server")


# Remove all old emulators.
utils.remove_all_emus()


t = threading.Thread(target=manager_emu.thread, daemon=True)
t.start()

t = threading.Thread(target=manager_adb.thread, daemon=True)
t.start()

t = threading.Thread(target=manager_ldp.thread, daemon=True)
t.start()


class Emulator:

    def __init__(self):
        q_ret = manager_emu.start()

        self.emuid = q_ret[0]
        self.adbid = q_ret[1]

        self._proxy = None
    
    def close(self):
        manager_emu.close(self.emuid, self.adbid)
    
    def send(self, command, timeout=60, capture_output=True, encoding="utf-8"):
        try:
            ret = subprocess.run(
                [
                    "adb",
                    "-s",
                    self.adbid,
                    "shell",
                    command
                ],
                timeout=timeout,
                capture_output=capture_output,
                encoding=encoding
            )
        
        except subprocess.TimeoutExpired:
            raise errors.ADB.TIMED_OUT(command)

        if capture_output:
            return ret.stdout
        
        return True
    
    def grant(self, package, perm):
        self.send("pm grant %s %s" % (package, perm))

    def push(self, src, dst):
        try:
            ret = subprocess.run(
                [
                    "adb",
                    "-s",
                    self.adbid,
                    "push",
                    src,
                    dst
                ],
                timeout=60
            )
        
        except subprocess.TimeoutExpired:
            raise errors.ADB.PUSH_FILE(dst)
        
        return True
    
    def run(self, packagename):
        subprocess.run(
            [
                "ldconsole",
                "runapp",
                "--name",
                self.emuid,
                "--packagename",
                packagename
            ]
        )

    def proxy(self, proxy):
        self.send("settings put global http_proxy %s" % proxy)
        self._proxy = proxy

    def screencap(self, save_to_file=False):
        ret = self.send("screencap -p", encoding=False)

        # Have to undo ADBs EOL character conversion
        img = ret.replace(b'\r\n', b'\n')

        img = cv2.imdecode(np.frombuffer(img, np.uint8), cv2.IMREAD_COLOR)

        if save_to_file:
            cv2.imwrite("errors/%s_%d.png" % (self.emuid, time.time()), img)

        return img

    def dump(self, unstuck=False):
        for _ in range(6):
            ret = self.send("uiautomator dump")

            if ret:
                break
            
            time.sleep(1)

            if unstuck:
                self.send("input keyevent KEYCODE_SPACE")
        
        else:
            raise errors.UIA.TIMED_OUT()
        
        ret = self.send("cat /sdcard/window_dump.xml", encoding=False)

        xml = etree.fromstring(ret)

        return xml
    
    def dump_uix_and_app(self):
        self.send("screencap -p /sdcard/app.png")
        self.send("uiautomator dump /sdcard/uix.uix")

    def get_element_loc(self, xpath, index=0, retries=3, raise_error=True, unstuck=False):
        for _ in range(retries):

            xml = self.dump(unstuck=unstuck)

            ret = xml.xpath(xpath)

            if ret:
                break

            time.sleep(1)

        else:

            if not raise_error:
                return False

            raise errors.UIA.NOT_FOUND(xpath)
        
        bounds = ret[index].get("bounds")

        bounds = bounds.replace("][", " ").replace("[", "").replace("]", "")
        
        c1, c2 = bounds.split(" ")

        x1, y1 = [int(c) for c in c1.split(",")]
        x2, y2 = [int(c) for c in c2.split(",")]

        return (x2 - x1) // 2 + x1, (y2 - y1) // 2 + y1

    def get_element_txt(self, xpath, index=0, retries=3, raise_error=True):
        for _ in range(retries):

            xml = self.dump()

            ret = xml.xpath(xpath)

            if ret:
                break

            time.sleep(1)

        else:

            if not raise_error:
                return False

            raise errors.UIA.NOT_FOUND(xpath)
        
        return ret[index].get("text")
    
    def get_element_all(self, xpath, retries=3, raise_error=True):
        for _ in range(retries):

            xml = self.dump()

            ret = xml.xpath(xpath)

            if ret:
                break

            time.sleep(1)
        
        else:

            if not raise_error:
                return False
            
            raise errors.UIA.NOT_FOUND(xpath)

        return ret
    
    def select_all(self):
        command = ""

        command += "sendevent /dev/input/event3 1 29 1;"
        command += "sendevent /dev/input/event3 1 30 1;"
        command += "sendevent /dev/input/event3 1 30 0;"
        command += "sendevent /dev/input/event3 1 29 0;"
        command += "sendevent /dev/input/event3 0 0  0 "

        self.send(command)

        time.sleep(1)
    
    def add_contact(self, name=None, phone=None):
        if not name:
            name = uuid.uuid4().hex
        
        # Add raw contact
        
        cmd = templates.all.get("con_contacts_add") % name

        ret = self.send(cmd)

        # Get id

        cmd = templates.all.get("con_contacts_get") % name

        ret = self.send(cmd)

        assert "_id=" in ret

        cid = ret.strip().split(" ")[-1].split("=")[-1]

        # Add phone

        cmd = templates.all.get("con_contacts_put") % (cid, phone)

        ret = self.send(cmd)
