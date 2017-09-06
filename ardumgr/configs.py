import re
import string
from contextlib import contextmanager
from pathlib import Path
from rabird.core.configparser import ConfigParser
from collections import KeysView, ItemsView, ValuesView, OrderedDict


class ConfigsMgrKeys(KeysView):
    pass


class ConfigsMgrItems(ItemsView):
    pass


class ConfigsMgrValues(ValuesView):
    pass


class ConfigsMgr(OrderedDict):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._base = None

    def base_on(self, other_mgr):
        self._base = other_mgr

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
                return OrderedDict()

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
        subtree = OrderedDict()
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

    def get_tool_subtree(self, tool_name):
        key_prefix = "tools.%s" % tool_name
        raw_subtree = self.get_subtree(key_prefix)
        subtree = OrderedDict()

        for k, v in raw_subtree.items():
            if ".params." in k:
                k = k.replace(".params.", ".")

            subtree[k] = v

        return subtree

    def get_children(self, key_prefix):
        names = []
        key_prefix = key_prefix.replace(".", r"\.")
        pattern = r"%s\.(\w+)" % key_prefix
        regexp = re.compile(pattern)

        for akey in self.keys():
            if akey == "boards.menu.cpu":
                # Removed unused child item from boards.txt
                continue

            matched = regexp.match(akey)
            if matched is None:
                continue

            names.append(matched.group(1))

        return list(set(names))

    def keys(self):
        return ConfigsMgrKeys(self)

    def items(self):
        return ConfigsMgrItems(self)

    def values(self):
        return ConfigsMgrValues(self)

    def __getitem__(self, name):
        if self._base:
            try:
                return super().__getitem__(name)
            except:
                return self._base[name]
        else:
            return super().__getitem__(name)

    def __setitem__(self, key, value):
        # We only support str type value!
        if value is None:
            value = ""
        else:
            value = str(value)

        # Parse ardumgr settings automatically
        if key.startswith('ardumgr.'):
            # Convert preferences to Arduino IDE required format
            if key == 'ardumgr.home_path':
                super().__setitem__('runtime.ide.path', value)
            elif key == 'ardumgr.package':
                super().__setitem__('target_package', value)
            elif key == 'ardumgr.programmer':
                super().__setitem__("programmer", "arduino:%s" % value)
            elif key == 'ardumgr.board':
                super().__setitem__("board", value)

                if 'ardumgr.cpu' in self:
                    super().__setitem__(
                        "custom_cpu", "%s_%s" % (value, self['ardumgr.cpu']))
            elif key == 'ardumgr.cpu':
                if 'ardumgr.board' in self:
                    super().__setitem__(
                        "custom_cpu", "%s_%s" % (self['ardumgr.board'], value))
            elif key == 'ardumgr.serial_port':
                super().__setitem__("serial.port", value)

        super().__setitem__(key, value)

    def __contains__(self, item):
        if self._base:
            if not super().__contains__(item):
                return item in self._base

            return False
        else:
            return super().__contains__(item)

    def __iter__(self):
        if self._base:
            def mixin_iter(self_keys, self_iter, base_iter):
                current_it = self_iter
                for akey in current_it:
                    yield akey

                current_it = base_iter
                for akey in current_it:
                    if akey in self_keys:
                        continue

                    yield akey

            return mixin_iter(
                super().keys(), super().__iter__(), iter(self._base))
        else:
            return super().__iter__()


class Platform(object):
    """
    A readonly class contained all informations related to specific
    platform.
    """

    def __init__(self, manager, id_):
        self._manager = manager
        self._id = id
        self._cfgs = ConfigsMgr()
        self._cfgs.base_on(manager._cfgs)

        self._cfgs["runtime.platform.path"] = str(
            manager._get_platform_dir(id_))

        cfg_file_base_keys = [
            ("platform.txt", None),
            ("boards.txt", "boards"),
            ("programmers.txt", "programmers"),
        ]

        for file_name, key in cfg_file_base_keys:
            apath = (manager._get_platform_dir(id_) / file_name)
            self._cfgs.load(apath, key)

        self._cfgs["target_platform"] = str(id_)

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
