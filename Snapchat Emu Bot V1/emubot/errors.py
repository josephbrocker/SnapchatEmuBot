# TODO: Better error stuff ... sigh

class ACC:

    class PERM_LOCK(Exception):
        pass

    class TIMED_OUT(Exception):
        pass

    class RATELIMIT(Exception):
        pass


class ADB:

    class TIMED_OUT(Exception):
        pass

    class PUSH_FILE(Exception):
        pass


class ADD:

    class RATELIMIT(Exception):
        pass

    class NOT_FOUND(Exception):
        pass

    class NO_SEND_1(Exception):
        pass

    class NO_SEND_2(Exception):
        pass

    class NO_SEND_3(Exception):
        pass

    class DUPLICATE(Exception):
        pass

    class TIMED_OUT(Exception):
        pass

    class NO_BUTTON(Exception):
        pass

    class ERR_COUNT(Exception):
        pass
    
    class ADD_COUNT(Exception):
        pass

    class NO_RESULT(Exception):
        pass


class REG:

    class USN_ERROR(Exception):
        pass

    class PWD_ERROR(Exception):
        pass

    class EMAIL_ERR(Exception):
        pass

    class SUB_ERROR(Exception):
        pass


class EMU:

    class TIMED_OUT(Exception):
        pass

    class SOFT_LOCK(Exception):
        pass


class UIA:

    class TIMED_OUT(Exception):
        pass

    class NOT_FOUND(Exception):
        pass


class CV2:

    class NOT_FOUND(Exception):
        pass