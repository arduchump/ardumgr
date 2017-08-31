import re
import string
import copy
from contextlib import contextmanager
from pathlib import Path
from rabird.core.configparser import ConfigParser


class ConfigsMgr(dict):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def load(self, fp, base_key=None):
        @contextmanager
        def fp_close(fp_tuple):
            try:
                yield fp_tuple[0]
            finally:
                if fp_tuple[1]:
                    fp_tuple[0].close()

        is_open_by_us = False
        if isinstance(fp, str) or isinstance(fp, Path):
            fp = Path(fp)
            if not fp.exists():
                return dict()

            fp = fp.open()
            is_open_by_us = True

        if base_key is None:
            base_key = ""
        else:
            base_key = base_key + "."

        with fp_close((fp, is_open_by_us)) as fp:
            cfgparser = ConfigParser()
            cfgparser.readfp(fp)

            items = cfgparser.items(cfgparser.UNNAMED_SECTION)
            for option, value in items:
                # Filter all empty/comment options away
                if (option.startswith(cfgparser._EMPTY_OPTION)
                        or option.startswith(cfgparser._COMMENT_OPTION)):
                    continue

                self["%s%s" % (base_key, option)] = value

    def get_overrided(self, key):
        runtime_os = self["runtime.os"]
        runtime_os_specific_key = "%s.%s" % (key, runtime_os)

        try:
            return self[runtime_os_specific_key]
        except:
            return self[key]

    def get_expanded(self, key):
        text = self.get_overrided(key)

        while True:
            formatter = string.Formatter()
            has_field = False
            snippets = []
            for literal_text, field_name, _, _ in formatter.parse(text):
                if literal_text:
                    snippets.append(literal_text)

                if field_name:
                    snippets.append(self.get_overrided(field_name))
                    has_field = True

            if not has_field:
                return text

            text = "".join(snippets)

    def get_subtree(self, key_prefix):
        subtree = dict()
        key_prefix = key_prefix.replace(".", r"\.")
        pattern = r"%s\.(.*)" % key_prefix
        regexp = re.compile(pattern)

        for akey, value in self.items():
            matched = regexp.match(akey)
            if matched is None:
                continue

            if ((matched.group(1) == "name")
                    or (matched.group(1).startswith("menu."))):
                continue

            subtree[matched.group(1)] = value

        return subtree

    def get_children(self, key_prefix):
        names = []
        key_prefix = key_prefix.replace(".", r"\.")
        pattern = r"%s\.(\w+)" % key_prefix
        regexp = re.compile(pattern)

        for akey in self.keys():
            matched = regexp.match(akey)
            if matched is None:
                continue

            names.append(matched.group(1))

        return list(set(names))


class Platform(object):
    """
    A readonly class contained all informations related to specific
    platform.
    """

    def __init__(self, manager, id_):
        self._manager = manager
        self._id = id_
        self._cfgs = copy.deepcopy(manager._runtime_cfgs)

        cfg_file_base_keys = [
            ("platform.txt", None),
            ("boards.txt", "boards"),
            ("programmers.txt", "programmers"),
        ]

        for file_name, key in cfg_file_base_keys:
            apath = (manager._get_platform_dir(id_) / file_name)
            self._cfgs.load(apath, key)

    @property
    def id_(self):
        return self._id

    @property
    def cfgs(self):
        return self._cfgs

    @property
    def boards(self):
        return self._cfgs.get_children("boards")

    @property
    def programmers(self):
        return self._cfgs.get_children("programmers")

    @property
    def tools(self):
        return self._cfgs.get_children("tools")

    def get_board_supported_cpus(self, board):
        """
        @return A list of supported cpu id will be return. If empty list
        returned, it means there have a default cpu and without any other
        options.
        """
        return self._cfgs.get_children("boards.%s.menu.cpu" % board)
