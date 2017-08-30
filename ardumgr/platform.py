import re
from rabird.core.configparser import ConfigParser


class Platform(object):
    """
    A readonly class contained all informations related to specific
    platform.
    """

    def __init__(self, manager, id_):
        self._manager = manager
        self._id = id_
        self._cfg = dict()

        cfg_file_base_keys = [
            ("platform.txt", None),
            ("boards.txt", "boards"),
            ("programmers.txt", "programmers"),
        ]

        for file_name, key in cfg_file_base_keys:
            apath = (manager._get_platform_dir(id_) / file_name)
            if apath.exists():
                with apath.open() as afile:
                    self._parse_cfg(afile, key)

    @property
    def id_(self):
        return self._id

    @property
    def cfg(self):
        return self._cfg

    @property
    def boards(self):
        names = []
        for akey in self._cfg.keys():
            matched = re.match(r"boards\.(\w+)\.name", akey)
            if matched is None:
                continue

            names.append(matched.group(1))

        return names

    @property
    def programmers(self):
        names = []
        for akey in self._cfg.keys():
            matched = re.match(r"programmers\.(\w+)\.name", akey)
            if matched is None:
                continue

            names.append(matched.group(1))

        return names

    def _parse_cfg(self, fp, base_key=None):
        cfgparser = ConfigParser()
        cfgparser.readfp(fp)

        if base_key is None:
            base_key = ""
        else:
            base_key = base_key + "."

        items = cfgparser.items(cfgparser.UNNAMED_SECTION)
        for option, value in items:
            # Filter all empty/comment options away
            if (option.startswith(cfgparser._EMPTY_OPTION)
                    or option.startswith(cfgparser._COMMENT_OPTION)):
                continue

            self._cfg["%s%s" % (base_key, option)] = value
