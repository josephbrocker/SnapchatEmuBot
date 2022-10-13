_int_friending = """

am start

-a android.intent.action.VIEW_00000000-0000-0000-0000-000000000000

-d snapchat://friending/addfriends/.*

-n com.snapchat.android/com.snap.mushroom.MainActivity

--es
com.snap.identity.api.PendingIntentExtras.sender_username
%s

--es
com.snap.identity.api.PendingIntentExtras.sender_user_id
%s

--ez
com.snap.identity.api.PendingIntentExtras.accept_friend_pending
true

--ez
fromServerNotification
true

--es
type
ADDFRIEND

--es
notificationAction
ACCEPT

-f 268468224

"""


_int_addfriend = """

am start

-n com.snapchat.android/com.snap.mushroom.MainActivity

-d snapchat://add-friends/

"""


_con_contacts_add = """

content insert

--uri
content://com.android.contacts/raw_contacts

--bind
account_name:s:%s

--bind
account_type:s:NULL

"""


_con_contacts_get = """

content query

--uri
content://com.android.contacts/raw_contacts

--projection
_id

--where
"account_name='%s'"

"""


_con_contacts_put = """

content insert

--uri
content://com.android.contacts/data

--bind
raw_contact_id:i:%s

--bind
mimetype:s:vnd.android.cursor.item/phone_v2

--bind
data1:s:%s

"""


_sql_suggested = """

    SELECT SuggestedFriend.userId
         , Friend.username
         , Friend.displayName
      FROM SuggestedFriend
INNER JOIN Friend
        ON ( suggestedFriend.userId = Friend.userId )
     WHERE SuggestedFriend.added = 0
;

"""


_sql_link_type = """

SELECT friendLinkType
  FROM Friend
 WHERE userId = "%s"
;

"""


def _parse(template):
    template = template.strip()

    while "\n\n" in template:
        template = template.replace("\n\n", "\n")
    
    return template.replace("\n", " ")


all = {
    "int_friending": _parse(_int_friending),
    "int_addfriend": _parse(_int_addfriend),
    "sql_suggested": _parse(_sql_suggested),
    "sql_link_type": _parse(_sql_link_type),
    "con_contacts_add": _parse(_con_contacts_add),
    "con_contacts_get": _parse(_con_contacts_get),
    "con_contacts_put": _parse(_con_contacts_put),
}
