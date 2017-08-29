
class Platform(object):
    """
    A readonly platform object contained all informations related to specific
    platform.
    """

    def __init__(self, id_, cfg):
        self._id = id_
        self._cfg = cfg

    @property
    def id_(self):
        return self._id

    @property
    def cfg(self):
        return self._cfg
