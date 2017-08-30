from rabird.core.configparser import ConfigParser


class Platform(object):
    """
    A readonly class contained all informations related to specific
    platform.
    """

    def __init__(self, manager, id_):
        self._manager = manager
        self._id = id_

        cfgparser = ConfigParser()
        adir = manager._get_platform_dir(id_)
        for file_path in adir.glob('*.txt'):
            if not file_path.is_file():
                continue

            with file_path.open() as afile:
                cfgparser.readfp(afile)

        self._cfg = dict(cfgparser.items(cfgparser.UNNAMED_SECTION))

    @property
    def id_(self):
        return self._id

    @property
    def cfg(self):
        return self._cfg
