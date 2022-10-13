import os
import random
import time
import uuid

import emulator
import errors

import templates


proxies = []

with open("proxies.txt") as f:
    for line in f:
        proxies.append(line.strip())


class Snap:

    def __init__(self, file_path):

        self.path = file_path
        self.file = file_path.split("/")[-1]
        self.name = self.file.split(".")[0]

        snap_type = self.file.split(".")[1].lower()

        if snap_type == "jpg":
            self.type = "image/*"
        
        if snap_type == "png":
            self.type = "image/*"
        
        if snap_type == "mp4":
            self.type = "snapvideo/*"
        
        self._uri = None
    
    @property
    def uri(self):
        if not self._uri:
            raise Exception("File hasn't been pushed to device yet.")
        
        return self._uri
    
    @uri.setter
    def uri(self, value):
        self._uri = value


class Snapchat(emulator.Emulator):

    def __init__(self):
        super().__init__()

        package = "com.snapchat.android"

        if proxies:
            self.proxy(random.choice(proxies))

        # Grant all permissions so we don't get dialogues asking for
        # them.
        
        self.grant(package, "android.permission.CAMERA")

        self.grant(package, "android.permission.WRITE_CONTACTS")
        self.grant(package, "android.permission.GET_ACCOUNTS")
        self.grant(package, "android.permission.READ_CONTACTS")

        self.grant(package, "android.permission.ACCESS_FINE_LOCATION")
        self.grant(package, "android.permission.ACCESS_COARSE_LOCATION")

        self.grant(package, "android.permission.RECORD_AUDIO")

        self.grant(package, "android.permission.READ_CALL_LOG")
        self.grant(package, "android.permission.READ_PHONE_STATE")
        self.grant(package, "android.permission.CALL_PHONE")
        self.grant(package, "android.permission.WRITE_CALL_LOG")
        self.grant(package, "android.permission.USE_SIP")
        self.grant(package, "android.permission.PROCESS_OUTGOING_CALLS")

        self.grant(package, "android.permission.READ_EXTERNAL_STORAGE")
        self.grant(package, "android.permission.WRITE_EXTERNAL_STORAGE")

        # Start snapchat
        
        self.run(package)

    def get_search_status(self):
        # This is hardcoded for 540 w 960 h screens

        img = self.screencap()

        val = sum(img[310, 450])

        if val == 744 or val == 705:
            return 1
        
        if val == 765:
            return 2
        
        if val == 442:
            return 3

        return 0

    def sign_in(self, username, password, proxy_host=None, proxy_port=None):
        # Set proxy if one is given

        if proxy_host and proxy_port:
            self.proxy("%s:%s" % (proxy_host, proxy_port))

        # Click "Log In"

        bounds = self.get_element_loc(
            "//*[@class='android.widget.TextView' and @text='Log In']", 
            retries=30
        )
        
        self.send("input tap %s %s" % bounds)

        # Click "Username" field

        bounds = self.get_element_loc(
            "//*[@resource-id='com.snapchat.android:id/username_or_email_field']")
        
        self.send("input tap %s %s" % bounds)

        # Fill in username

        self.send("input text %s" % username)

        # Click "Password" field

        bounds = self.get_element_loc(
            "//*[@resource-id='com.snapchat.android:id/password_field']")
        
        self.send("input tap %s %s" % bounds)

        # Fill in password

        self.send("input text '%s'" % password)

        # Click "Log In" button

        bounds = self.get_element_loc(
            "//*[@resource-id='com.snapchat.android:id/button_text' and @text='Log In']")
        
        self.send("input tap %s %s" % bounds)

        # Wait for login to complete

        for _ in range(30):

            bounds = self.get_element_loc(
                "//*[@resource-id='com.snapchat.android:id/button_text' and @text='Logging In']",
                retries=1,
                raise_error=False
            )

            if not bounds:
                break

            time.sleep(1)
        
        else:
            raise errors.ACC.TIMED_OUT()
        
        # Check for errors

        message = self.get_element_txt(
            "//*[@resource-id='com.snapchat.android:id/login_error_message']",
            retries=1,
            raise_error=False
        )

        if not message:
            pass

        elif message.startswith("Oh no!"):
            raise errors.ACC.PERM_LOCK()
            
        elif message.startswith("Your account has been locked"):
            raise errors.ACC.PERM_LOCK()
        
        else:
            raise errors.EMU.SOFT_LOCK()

        # Dismiss camera error prompt (if presented)

        bounds = self.get_element_loc(
            "//*[@resource-id='android:id/button2']",
            raise_error=False
        )

        if bounds:
            self.send("input tap %s %s" % bounds)

        # Confirm login was successful
        
        self.get_element_loc(
            "//*[@resource-id='com.snapchat.android:id/hova_header_search_icon']")

    def sign_up(
        self,
        username,
        password,
        email,
        f_name,
        l_name
    ):
        # --- Screen 1 -------------------------------------------------

        # Click "Sign Up"

        bounds = self.get_element_loc(
            "//*[@class='android.widget.TextView' and @text='Sign Up']", 
            retries=30
        )
        
        self.send("input tap %s %s" % bounds)

        # Wait till page is ready

        self.get_element_loc(
            "//*[@resource-id='com.snapchat.android:id/display_name_first_name_field']")

        self.send("input keyevent KEYCODE_TAB")

        # Fill in "First Name" field

        self.send("input keyevent KEYCODE_TAB")
        
        self.send("input text %s" % f_name)

        # Fill in "Last Name" field

        self.send("input keyevent KEYCODE_TAB")

        self.send("input text %s" % l_name)

        # Click "Sign Up & Accept"

        bounds = self.get_element_loc(
            "//*[@class='android.widget.TextView' and @text='Sign Up & Accept']")

        self.send("input tap %s %s" % bounds)

        # --------------------------------------------------------------

        # --- Screen 2 -------------------------------------------------

        # Wait till page is ready

        self.get_element_loc(
            "//*[@resource-id='com.snapchat.android:id/birthday_form_field']")

        # Set month slider to unlock "Continue" button

        self.send("input keyevent KEYCODE_DPAD_UP")
        
        # Tap "Continue"

        bounds = self.get_element_loc(
            "//*[@resource-id='com.snapchat.android:id/button_text' and @text='Continue']",
            retries=1
        )

        self.send("input tap %s %s" % bounds)

        # --------------------------------------------------------------

        # --- Screen 3 -------------------------------------------------

        # Tap "Change my username" (if presented)

        bounds = self.get_element_loc(
            "//*[@resource-id='com.snapchat.android:id/change_username_link']",
            raise_error=False
        )

        if bounds:

            self.send("input tap %s %s" % bounds)

            # Tap username field

            bounds = self.get_element_loc(
                "//*[@resource-id='com.snapchat.android:id/username_form_field']")

            self.send("input tap %s %s" % bounds)

            # See if there's a pre-filled username and erase it
            
            self.select_all()

            self.send("input keyevent KEYCODE_DEL")
        
        # Fill in username

        self.send("input text %s" % username)

        # Make sure username is available

        for _ in range(6):

            message = self.get_element_txt(
                "//*[@resource-id='com.snapchat.android:id/username_available_subtext']",
                retries=1,
                raise_error=False,
            )

            if message:
                break
            
            message = self.get_element_txt(
                "//*[@resource-id='com.snapchat.android:id/username_error_message']",
                retries=1,
                raise_error=False,
            )
            
            if message:
                raise errors.REG.USN_ERROR(message)

        # Tap "Continue"

        bounds = self.get_element_loc(
            "//*[@resource-id='com.snapchat.android:id/button_text' and @text='Continue']")

        self.send("input tap %s %s" % bounds)

        # --------------------------------------------------------------

        # --- Screen 4 -------------------------------------------------

        # Find password field

        bounds = self.get_element_loc(
            "//*[@resource-id='com.snapchat.android:id/password_form_field']")

        # Fill in password

        self.send("input text %s" % password)

        # Tap "Continue"

        bounds = self.get_element_loc(
            "//*[@resource-id='com.snapchat.android:id/button_text' and @text='Continue']")

        self.send("input tap %s %s" % bounds)

        # Make sure we're not in a loading screen

        for _ in range(30):

            bounds = self.get_element_loc(
                "//*[@resource-id='com.snapchat.android:id/button_spinner']",
                retries=1,
                raise_error=False
            )

            if not bounds:
                break
        
        else:
            raise errors.REG.PWD_ERROR("Stuck loading.")

        # Check for error

        error = self.get_element_txt(
            "//*[@resource-id='com.snapchat.android:id/password_error_message']",
            retries=1,
            raise_error=False
        )

        if error:
            raise errors.REG.PWD_ERROR(error)

        # --------------------------------------------------------------

        # --- Screen 5 -------------------------------------------------

        skip = False

        # Check for phone or email screen here

        bounds = self.get_element_loc(
            "//*[starts-with(@resource-id, 'com.snapchat.android:id/signup_with_email_instead')]",
            raise_error=False
        )

        if bounds:

            # Click "Sign up with email instead"

            skip = True

            self.send("input tap %s %s" % bounds)
        
        # Fill in email

        bounds = self.get_element_loc(
            "//*[@resource-id='com.snapchat.android:id/email_field']")

        self.send("input text %s" % email)

        # Tap "Continue"

        bounds = self.get_element_loc(
            "//*[@resource-id='com.snapchat.android:id/button_text' and @text='Continue']")

        self.send("input tap %s %s" % bounds)

        # Check for errors

        error = self.get_element_txt(
            "//*[@resource-id='com.snapchat.android:id/email_error_message']",
            retries=1,
            raise_error=False
        )

        if error:
            raise errors.REG.EMAIL_ERR(error)
    
        # --- Screen 6 -------------------------------------------------

        # Tap "Skip" on phone number screen

        if not skip:

            bounds = self.get_element_loc(
                "//*[@resource-id='com.snapchat.android:id/skip_button']",
                retries=6
            )

            self.send("input tap %s %s" % bounds)
        
        # --------------------------------------------------------------

        # --- Screen 7 -------------------------------------------------
        
        # Tap "Skip" on find your friends screen

        bounds = self.get_element_loc(
            "//*[@resource-id='com.snapchat.android:id/skip_button']")

        self.send("input tap %s %s" % bounds)

        # --------------------------------------------------------------

        # --- Screen 8 -------------------------------------------------

        # Tap "Skip" on confirmation screen

        bounds = self.get_element_loc(
            "//*[@resource-id='com.snapchat.android:id/cancel_button']")

        self.send("input tap %s %s" % bounds)

        # --------------------------------------------------------------

        # --- Screen 8.5 -----------------------------------------------

        # Skip bitmoji

        bounds = self.get_element_loc(
            "//*[@text='Skip']",
            raise_error=False
        )
        
        if bounds:
            self.send("input tap %s %s" % bounds)

        # --------------------------------------------------------------

        # --- Screen 9 -------------------------------------------------

        # Dismiss camera error prompt (if presented)

        bounds = self.get_element_loc(
            "//*[@resource-id='android:id/button2']",
            raise_error=False
        )

        if bounds:
            self.send("input tap %s %s" % bounds)

        # --------------------------------------------------------------

        # --- Screen 10 ------------------------------------------------

        # Confirm registration was successful
        
        bounds = self.get_element_loc(
            "//*[@resource-id='com.snapchat.android:id/hova_header_search_icon']")

        # --------------------------------------------------------------

        return True
    
    def open_memories(self):
        self.send("am start -d snapchat://memories/")

        # Make sure we on the memories page

        self.get_element_loc("//*[@text='Memories']")
        
        # Enable memories if needed

        bounds = self.get_element_loc(
            "//*[@text='Welcome to your Memories!']",
            retries=1,
            raise_error=False
        )

        if not bounds:
            return True
        
        bounds = self.get_element_loc(
            "//*[@resource-id='com.snapchat.android:id/memories_empty_state_button']")
        
        self.send("input tap %s %s" % bounds)
        
        return True
    
    def navigate_to_camera_roll(self):        
        # Select "Camera Roll"

        bounds = self.get_element_loc(
            "//*[@text='Camera Roll']",
            retries=30
        )

        self.send("input tap %s %s" % bounds)

        # Check if we are on the camera roll page

        self.get_element_loc(
            "//*[@resource-id='com.snapchat.android:id/memories_page_camera_roll_title']")
        
        return True
    
    def select_snap_from_memories(self, index=0):
        # Get image grid

        bounds = self.get_element_loc(     
            "//*[@resource-id='com.snapchat.android:id/grid_frameable_container']",
            index=index
        )
        
        self.send("input tap %s %s" % bounds)

        # Click CTA

        bounds = self.get_element_loc(
            "//*[@resource-id='com.snapchat.android:id/send_btn']")
        
        self.send("input tap %s %s" % bounds)

        time.sleep(1)

        # Deal with chat retention (if presented)

        bounds = self.get_element_loc(
            "//*[@resource-id='com.snapchat.android:id/chat_retention_dismiss']",
            raise_error=False
        )

        if bounds:
            self.send("input tap %s %s" % bounds)

        time.sleep(1)

        # Confirm we're on recipient screen and enter text field

        bounds = self.get_element_loc(
            "//*[@resource-id='com.snapchat.android:id/input_field_edit_text']")
        
        self.send("input tap %s %s" % bounds)
        
        return True
    
    def add_recipient_to_snap(self, username):
        # Search username

        self.send("input text %s" % username)

        time.sleep(3)

        # Wait for result or assume user can't be found

        for _ in range(6):
            status = self.get_search_status()

            if status == 2:
                break

            time.sleep(1)

        if status == 3:
            raise errors.ADD.RATELIMIT()
        
        if status == 1:
            raise errors.ADD.NOT_FOUND()

        if status == 0:
            raise errors.CV2.NOT_FOUND()
        
        self.send("input tap 270 320")

        time.sleep(1)

        # for _ in range(3):
        #     status = self.get_search_status()

        #     if status == 3:
        #         return True

        #     time.sleep(1)
        
        # raise errors.CV2.NOT_FOUND()

        return True

    def send_snap_to_recipients(self):
        # Close keyboard and back out of search screen

        self.send("input keyevent KEYCODE_BACK")
        self.send("input keyevent KEYCODE_BACK")
        
        # Send snap to recipients

        bounds = self.get_element_loc(
            "//*[@resource-id='com.snapchat.android:id/send_to_send_button']")
        
        self.send("input tap %s %s" % bounds)

        time.sleep(.25)
        self.send("input keyevent KEYCODE_BACK")

        i = 0
        s = 0

        while (i < (3 if s == 0 else 30)):

            status = self.get_element_txt(
                "//*[@resource-id='com.snapchat.android:id/status_bar_secondary_text']",
                retries=1,
                raise_error=False
            )
            
            i += 1

            if not status:
                pass  # Ignore no results and keep looping.

            elif status.startswith("Send"):
                s = 1
            
            elif status.startswith("Sent"):
                break
            
            elif status.startswith("Could not send."):
                raise errors.ADD.NO_SEND_3()
            
            else:
                print("UNDEFINED STATUS BAR TEXT:", status)
        
        else:

            if s == 0:
                raise errors.ADD.NO_SEND_1()
            
            if s == 1:
                raise errors.ADD.NO_SEND_2()
        
        return True
    
    def add_through_intent(self, username):
        self.send("am start -d snapchat://add/%s" % username)

        # Dismiss camera error prompt (if presented)

        bounds = self.get_element_loc(
            "//*[@resource-id='android:id/button2']",
            retries=1,
            raise_error=False
        )

        if bounds:
            self.send("input tap %s %s" % bounds)
        
        # Make sure intent is ready

        try:
            bounds = self.get_element_loc(
                "//*[@resource-id='com.snapchat.android:id/scan_add_friend_card_button_add_friend']",
                retries=10
            )

            # Click add

            self.send("input tap %s %s" % bounds)

        except errors.UIA.NOT_FOUND:
        
            message = self.get_element_txt(
                "//*[@resource-id='com.snapchat.android:id/scan_card_msg_display_name']")

            if not message:
                raise
            
            elif message.startswith("Oops!"):
                raise errors.ADD.NOT_FOUND()
            
            elif message.endswith("friend!"):
                raise errors.ADD.DUPLICATE()
    
    def sub_through_search(self, username):
        # Dismiss camera error prompt (if presented)

        bounds = self.get_element_loc(
            "//*[@resource-id='android:id/button2']",
            retries=1,
            raise_error=False
        )

        if bounds:
            self.send("input tap %s %s" % bounds)
        
        # Make sure we on home screen

        bounds = self.get_element_loc(
            "//*[@resource-id='com.snapchat.android:id/hova_header_search_icon']")

        self.send("input tap %s %s" % bounds)

        self.get_element_loc(
            "//*[@class='android.widget.EditText' and @text='Search']")

        self.send("input text %s" % username)

        try:
            bounds = self.get_element_loc(
                "//*[@class='android.widget.TextView' and @text='Subscribe']")

        except errors.UIA.NOT_FOUND:
            raise errors.REG.SUB_ERROR()

        self.send("input tap %s %s" % bounds)

        time.sleep(3)

    def add_through_keyword_new_v1(self, keyword):
        self.send("am start -d snapchat://add-friends/.*")

        # Dismiss camera error prompt (if presented)

        bounds = self.get_element_loc(
            "//*[@resource-id='android:id/button2']",
            retries=1,
            raise_error=False
        )

        if bounds:
            self.send("input tap %s %s" % bounds)

        # Find the input field

        bounds = self.get_element_loc(
            "//*[@resource-id='com.snapchat.android:id/input_field_edit_text']")

        # Click the input field

        self.send("input tap %s %s" % bounds)

        # Select all to clear any previous keyword

        self.select_all()

        # Enter keyword

        self.send("input text '%s'" % keyword)

        time.sleep(3)

        # # Make screenshot of device to extract all the info we need

        # img_og = self.screencap()

        # # Make sure the search went correctly

        # img = img_og[207:240, 23:517]

        # txt = pytesseract.image_to_string(img).strip()

        # if txt != "Add Friends":
        #     raise errors.ADD.FRIENDING()

    def get_search_status_new_v1(self):
        # This is hardcoded for 540 w 960 h screens

        # Make screenshot of device to extract all the info we need

        img_og = self.screencap()

        # Use pixel color value to make sure we have a result

        val = sum(img_og[265, 35])

        if val != 765:
            return 0  # No result found

        # Use pixel color value to make sure we can add user

        val = sum(img_og[297, 419])

        if val != 0:
            return 1  # No 'Add' option
        
        return 2  # Ready to add
    
    def add_suggested_search_result_new_v1(self):
        for _ in range(5):
            status = self.get_search_status_new_v1()

            if status == 2:
                break

            time.sleep(1)
        
        else:
            if status == 0:
                raise errors.ADD.NOT_FOUND()
            
            if status == 1:
                raise errors.ADD.RATELIMIT()

        self.send("input tap 450 300")

        return True

    def add_through_keyword_new_v2(self, keyword):
        self.send("am start -d snapchat://add-friends/.*")

        # Dismiss camera error prompt (if presented)

        bounds = self.get_element_loc(
            "//*[@resource-id='android:id/button2']",
            retries=1,
            raise_error=False
        )

        if bounds:
            self.send("input tap %s %s" % bounds)
        
        # Find the input field

        bounds = self.get_element_loc(
            "//*[@class='android.widget.EditText']")
        
        # Click the input field

        self.send("input tap %s %s" % bounds)

        # Select all to clear any previous keyword

        self.select_all()

        # Enter keyword

        self.send("input text '%s'" % keyword)

        time.sleep(3)
    
    def add_suggested_search_result_new_v2(self):
        # Find all addable search results

        addable_elements = self.get_element_all(
            "//*[@class='android.widget.TextView' and @text='Add']",
            raise_error=False
        )

        if not addable_elements:
            raise errors.ADD.NOT_FOUND()
        
        amt_old = len(addable_elements)
        
        # Get bounds

        bounds = addable_elements[0].get("bounds")

        bounds = bounds.replace("][", " ").replace("[", "").replace("]", "")
        
        c1, c2 = bounds.split(" ")

        x1, y1 = [int(c) for c in c1.split(",")]
        x2, y2 = [int(c) for c in c2.split(",")]

        bounds = (x2 - x1) // 2 + x1, (y2 - y1) // 2 + y1

        # Add result

        self.send("input tap %s %s" % bounds)

        time.sleep(3)

        # Make sure add was successful

        addable_elements = self.get_element_all(
            "//*[@class='android.widget.TextView' and @text='Add']",
            raise_error=False
        )

        if not addable_elements:
            amt_new = 0
        else:
            amt_new = len(addable_elements)

        if amt_new >= amt_old:
            raise errors.ADD.RATELIMIT()

        # Scroll down

        self.send("input swipe 0 350 0 249 1000")
        
        return True
    
    def db_set_shortcut(self):

        mdb = "/data/data/com.snapchat.android/databases/main.db"

        id_ = str(uuid.uuid4())

        cmd = """

        DELETE
          FROM SendToList			-- shortcuts
        ;
            
        DELETE
          FROM SendToListMember		-- recipients
        ;

        INSERT
          INTO SendToList
             ( identifier
             , name
             , creationTime
             , rank
             )
        VALUES 
             ( "%s"				    -- identifier
             , "💰"					-- name
             , %s       			-- creationTime
             , 0					-- rank
             )
        ;

        """ % (id_, int(time.time()))

        ret = self.send("sqlite3 %s '%s' '.exit'" % (mdb, cmd))

        return id_
    
    def db_get_user_ids(self):

        mdb = "/data/data/com.snapchat.android/databases/main.db"

        cmd = """

        SELECT userId
          FROM Friend
         WHERE friendLinkType = 0   -- added back
         LIMIT -1
        OFFSET 2					-- skip Snapchat and own username
        ;

        """

        ret = self.send("sqlite3 %s '%s' '.exit'" % (mdb, cmd))

        return ret.strip().split("\n")
    
    def db_add_user_ids(self, id_, user_ids: list):

        mdb = "/data/data/com.snapchat.android/databases/main.db"

        ids = "\n             , ".join(
            ["(\"%s\",\"%s\",1)" % (id_, uid) for uid in user_ids])

        cmd = """

        INSERT
          INTO SendToListMember
             ( listIdentifier
             , recipientId
             , recipientType
             )
        VALUES 
               %s
        ;

        """ % ids

        ret = self.send("sqlite3 %s '%s' '.exit'" % (mdb, cmd))

        return ret

    def push_snap_to_emulator(self, snap: Snap):

        ret = self.push(snap.path, "/sdcard/DCIM/")

        # Insert new file into the standard media ContentProvider

        uri = "content://media/external/%s/media/"

        if snap.type == "image/*":
            uri = uri % "images"
        
        if snap.type == "snapvideo/*":
            uri = uri % "video"

        cmd = "content insert"

        cmd += " --uri %s" % uri
        cmd += " --bind _data:s:/storage/emulated/0/DCIM/%s" % snap.file

        ret = self.send(cmd)

        # Query the content _id

        cmd = "content query --projection _id"

        cmd += " --uri %s" % uri
        cmd += " --where \"title='%s'\"" % snap.name

        ret = self.send(cmd)

        assert "_id=" in ret

        _id = ret.strip().split(" ")[-1].split("=")[-1]

        # Set uri of the file we pushed to the emulator

        snap.uri = uri + _id

    def push_snap_to_liveview(self, snap: Snap, url=None):

        cmd = "am start -a %s -t %s --eu %s %s " % (
            "android.intent.action.SEND",
            snap.type,
            "android.intent.extra.STREAM",
            snap.uri
        )

        if url:
            cmd += "--es url %s " % url
        
        cmd += "com.vsco.cam"

        for _ in range(2):

            self.send(cmd)

            print("Command sent.", cmd)

            time.sleep(3)

            bounds = self.get_element_loc(
                "//*[@resource-id='com.snapchat.android:id/send_btn']",
                retries=10,
                raise_error=False
            )

            if not bounds:
                self.send("input keyevent KEYCODE_BACK")

                try:
                    self.get_element_loc(
                        "//*[@resource-id='com.snapchat.android:id/send_btn']")

                except errors.UIA.NOT_FOUND:
                    continue
            
            break

        else:
            raise errors.UIA.NOT_FOUND()
            
        bounds = self.get_element_loc(
            "//*[@resource-id='com.snapchat.android:id/cancel_button']",
            raise_error=False
        )
        
        if bounds:
            self.send("input tap %s %s" % bounds)

    def send_snap_open_select(self):

        bounds = self.get_element_loc(
            "//*[@resource-id='com.snapchat.android:id/send_btn']",
            unstuck=True
        )
        
        self.send("input tap %s %s" % bounds)

        self.get_element_loc(
            "//*[@class='android.widget.TextView' and @text='👋 New Friends']")

    def send_snap_exit_select(self):

        bounds = self.get_element_loc(
            "//*[@resource-id='com.snapchat.android:id/subscreen_top_left']",
            unstuck=True
        )
        
        self.send("input tap %s %s" % bounds)

    def send_snap_send_button(self):

        bounds = self.get_element_loc(
            "//*[@resource-id='com.snapchat.android:id/send_to_send_button']")
        
        self.send("input tap %s %s" % bounds)

        self.get_element_loc(
            "//*[@resource-id='com.snapchat.android:id/hova_page_title']")
        
        self.send("input keyevent KEYCODE_BACK")

        time.sleep(5)
    
    def send_snap_to_shortcut(self):

        bounds = self.get_element_loc(
            "//*[@class='android.widget.TextView' and @text='💰']",
            unstuck=True
        )

        self.send("input tap %s %s" % bounds)

        # Make sure the header is being shown

        self.get_element_loc(
            "//*[@resource-id='com.snapchat.android:id/send_to_section_header']",
            unstuck=True
        )

        # This is hardcoded for 540 w 960 h

        self.send("input tap %s %s" % (435, 220))
    
    def db_get_suggested_users(self):

        mdb = "/data/data/com.snapchat.android/databases/main.db"

        cmd = templates.all.get("sql_suggested")

        ret = self.send("sqlite3 %s '%s' '.exit'" % (mdb, cmd))

        ret = ret.strip()

        if not ret:
            return None

        return ret.split("\n")
    
    def add_with_friending_intent(self, uid, usn):

        cmd = templates.all.get("int_friending") % (usn, uid)

        self.send(cmd)

        self.get_element_loc(
            "//*[@text='item_dismiss_button']", retries=5)
    
    def open_add_friends_presenter(self):

        cmd = templates.all.get("int_addfriend")

        self.send(cmd)

        self.get_element_loc(
            "//*[@text='item_dismiss_button']", retries=30)
    
    def db_get_friend_link_type(self, uid):

        mdb = "/data/data/com.snapchat.android/databases/main.db"

        cmd = templates.all.get("sql_link_type") % (uid)

        ret = self.send("sqlite3 %s '%s' '.exit'" % (mdb, cmd))

        return ret.strip()
