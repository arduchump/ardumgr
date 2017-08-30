import copy


class Programmer(object):
    """
    Programmer is a tool use for these tasks:

    1. Upload binary program to your board
    2. Flash erase/dump/write
    3. Board configuration change or reading
    """

    def __init__(self, platform, programmer, board, cpu):
        self._platform = copy.deepcopy(platform)
        self._programmer = programmer
        self._board = board
        self._cpu = cpu
