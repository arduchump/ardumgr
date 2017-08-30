import re
import string
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
        return self._get_children("boards")

    @property
    def programmers(self):
        return self._get_children("programmers")

    @property
    def tools(self):
        return self._get_children("tools")

    def get_board_supported_cpus(self, board):
        """
        @return A list of supported cpu id will be return. If empty list
        returned, it means there have a default cpu and without any other
        options.
        """
        return self._get_children("boards.%s.menu.cpu" % board)

    def get_expanded(self, key):
        text = self._cfg[key]

        while True:
            formatter = string.Formatter()
            names = []
            for _, field_name, _, _ in formatter.parse(text):
                if field_name is None:
                    continue

                names.append(field_name)

            if len(names) <= 0:
                return text

            # Search name matched values
            kwargs = dict()
            for name in names:
                kwargs[name] = self._cfg[name]
            text = formatter.format(**kwargs)

    def _get_children(self, key_prefix):
        names = []
        key_prefix = key_prefix.replace(".", r"\.")
        pattern = r"%s\.(\w+)" % key_prefix
        regexp = re.compile(pattern)

        for akey in self._cfg.keys():
            matched = regexp.match(akey)
            if matched is None:
                continue

            names.append(matched.group(1))

        return list(set(names))

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
