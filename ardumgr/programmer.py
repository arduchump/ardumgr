import copy
from .exceptions import ArduMgrError


class Programmer(object):
    """
    Programmer is a tool use for these tasks:

    1. Upload binary program to your board
    2. Flash erase/dump/write
    3. Board configuration change or reading
    """

    def __init__(
            self, platform, programmer, board, cpu=None, serial_port=None):

        self._platform = copy.deepcopy(platform)
        self._programmer = programmer
        self._board = board
        self._cpu = cpu
        self._serial_port = serial_port

        platform = self._platform  # Use new created platform

        # Check if cpu related to specfic board
        cpus = platform.get_board_supported_cpus(board)
        if cpus:
            if cpu is None:
                raise ArduMgrError(
                    "You must specific a cpu for board \"%s\"! Choice : %s" % (
                        board, cpus))
            elif cpu not in cpus:
                raise ArduMgrError(
                    "Board \"%s\" don't support cpu \"%s\"!" % (board, cpu))
        elif cpu is not None:
            raise ArduMgrError(
                "Board have a default cpu, don't specfic it yourself!" % board)

        # Specific serial port settings if it valid
        if serial_port:
            platform.cfgs["serial.port"] = serial_port

        # Find board and cpu specific configs and expand it to our platform
        key = "boards.%s" % board
        subtree = platform.cfgs.get_subtree(key)
        platform.cfgs.update(subtree)

        if cpu:
            key = "boards.%s.menu.cpu" % board
            subtree = platform.cfgs.get_subtree(key)
            platform.cfgs.update(subtree)

        # Set programmer config
        platform.cfgs["programmer"] = "arduino:%s" % programmer

        # Expand upload tool configs
        upload_tool = platform.cfgs["upload.tool"]
        subtree = platform.cfgs.get_subtree("tools.%s" % upload_tool)
        platform.cfgs.update(subtree)
