# -*- coding: utf-8 -*-

"""Main module."""

import re
import sys
from pkg_resources import parse_version
from pathlib import Path
from .configs import ConfigsMgr, Platform


class ArduMgr(object):

    def __init__(self, home_path):
        self._home_path = Path(str(home_path))

        # Check if the specified Arduino installation version is before 1.5.0
        version_text = self.version
        self._is_old_style_dirs = (parse_version(self.version)
                                   < parse_version('1.5.0'))

        # The Arduino installation version is 1.5.0, so there is no IDE
        # run-time configuration available.
        self._runtime_cfgs = ConfigsMgr()

        self._runtime_cfgs['runtime.ide.path'] = self._home_path
        self._runtime_cfgs['runtime.ide.version'] = (
            version_text.replace('.', '_'))

        # Load runtime preferences
        preferences_path = self.user_dir / "preferences.txt"
        self._runtime_cfgs.load(preferences_path)

        # Analyse runtime tools paths
        user_tools_dir = self.user_dir / "packages" / "arduino" / "tools"
        for tool_base_dir in user_tools_dir.iterdir():
            if not tool_base_dir.is_dir():
                continue

            # Included multi-versions tool
            for adir in tool_base_dir.iterdir():
                if not adir.is_dir():
                    continue

                value = str(adir)

                key = 'runtime.tools.%s.path' % tool_base_dir.name
                self._runtime_cfgs[key] = value

                key = 'runtime.tools.%s-%s.path' % (
                    tool_base_dir.name, adir.name)
                self._runtime_cfgs[key] = value

                key = 'runtime.tools.arduino-%s-%s.path' % (
                    tool_base_dir.name, adir.name)
                self._runtime_cfgs[key] = value

        # Add runtime os config
        key = "runtime.os"
        self._runtime_cfgs[key] = "linux"
        if sys.platform == "win32":
            self._runtime_cfgs[key] = "windows"
        elif sys.platform == "darwin":
            self._runtime_cfgs[key] = "macosx"

        # Search platform dirs
        self._platforms = list()
        if self._is_old_style_dirs:
            self._platforms.append('avr')
        else:
            for adir in self._get_platform_base_dir().iterdir():
                self._platforms.append(adir.name)

    @property
    def oss(self):
        """
        Return a series OS (OSs)

        Reference: https://github.com/arduino/Arduino/wiki/Arduino-IDE-1.5-3rd-party-Hardware-specification#global-predefined-properties
        """

        return ["linux", "windows", "macosx"]

    @property
    def platforms(self):
        return self._platforms

    @property
    def version(self):
        """
        Detect Arduino IDE's version, return 1.0.0 if failed.
        """

        version = "1.0.0"  # Default

        while True:
            revision_file_path = self._home_path / "lib/version.txt"
            if revision_file_path.exists():
                with revision_file_path.open() as revision_file:
                    match = re.search(
                        r'^[^:]+:(?P<version>[\d\.]+)',
                        revision_file.read(),
                        re.VERBOSE | re.MULTILINE)
                    if match is not None:
                        version = match.group('version')

            revision_file_path = (self._home_path / 'revisions.txt')
            if revision_file_path.exists():
                with revision_file_path.open() as revision_file:
                    # The Arduino installation version is 1.5+, which includes
                    # information about the IDE run-time configuration.
                    match = re.search(
                        r'^ARDUINO\s+(?P<version>\d+\.\d+\.\d+)',
                        revision_file.read(),
                        re.VERBOSE | re.MULTILINE)
                    if match is not None:
                        version = match.group('version')

            break

        return version

    @property
    def user_dir(self):
        user_dir = Path.home() / ".arduino"

        # After 1.6.10, user dir changed from .arduino to .arduino15
        #
        # Reference :
        # https://build.opensuse.org/package/view_file/CrossToolchain:avr/Arduino/Arduino.changes?expand=1
        version_text = self.version
        if parse_version(version_text) >= parse_version('1.6.10'):
            user_dir = Path.home() / ".arduino15"

        return user_dir

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
