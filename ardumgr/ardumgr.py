# -*- coding: utf-8 -*-

"""Main module."""

import re
from pkg_resources import parse_version
from pathlib import Path
from collections import OrderedDict
from .platform import Platform


class ArduMgr(object):

    def __init__(self, home_path):
        self._home_path = Path(str(home_path))

        revision_file_path = (self._home_path / 'revisions.txt')

        # Check if the specified Arduino installation version is before 1.5.0
        self._is_old_style_dirs = not revision_file_path.is_file()

        # The Arduino installation version is 1.5.0, so there is no IDE
        # run-time configuration available.
        self._runtime_cfg = OrderedDict()

        if not self._is_old_style_dirs:
            with revision_file_path.open() as revision_file:
                # The Arduino installation version is 1.5+, which includes
                # information about the IDE run-time configuration.
                match = re.search(
                    r'^ARDUINO\s+(?P<version>\d+\.\d+\.\d+)',
                    revision_file.read(),
                    re.VERBOSE | re.MULTILINE)
                version_text = match.group('version')
                if parse_version(version_text) < parse_version('1.5.0'):
                    self._is_old_style_dirs = True

                self._runtime_cfg['runtime'] = {
                    'ide': {
                        'path': self._home_path,
                        'version': version_text.replace('.', '_')
                    }
                }

        # Search platform dirs
        self._platforms = list()
        if self._is_old_style_dirs:
            self._platforms.append('avr')
        else:
            for adir in self._get_platform_base_dir().iterdir():
                self._platforms.append(adir.name)

    @property
    def platforms(self):
        return self._platforms

    def get_platform(self, id_):
        p = Platform(self, id_)

        # TODO: Need to fill the configurations from platform config files
        return p

    def _get_compatible_dir(self, path, platform_id):
        path = Path(path)
        if self._is_old_style_dirs:
            return path
        else:
            return path / str(platform_id)

    def _get_hardware_dir(self):
        return self._home_path / 'hardware'

    def _get_platform_base_dir(self):
        return self._home_path / 'hardware' / 'arduino'

    def _get_tools_base_dir(self):
        return self._home_path / 'hardware' / 'tools'

    def _get_tools_dir(self, platform_id):
        return self._get_compatible_dir(
            self._get_tools_base_dir(), platform_id)

    def _get_platform_dir(self, platform_id):
        return self._get_compatible_dir(
            self._get_platform_base_dir(), platform_id)
