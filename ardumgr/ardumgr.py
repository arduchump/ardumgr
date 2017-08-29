# -*- coding: utf-8 -*-

"""Main module."""

import re
import packaging.version
from pathlib import Path
from collections import OrderedDict


class ArduMgr(object):

    def __init__(self, home_path):
        self._home_path = Path(str(home_path))

        revision_file_path = (self._home_path / 'revisions.txt')

        # Check if the specified Arduino installation version is before 1.5.0
        self._is_before_v1_5_0 = not revision_file_path.is_file()

        # The Arduino installation version is 1.5.0, so there is no IDE
        # run-time configuration available.
        self._runtime_cfg = OrderedDict()

        if not self._is_before_v1_5_0:
            with revision_file_path.open("rb") as revision_file:
                # The Arduino installation version is 1.5+, which includes
                # information about the IDE run-time configuration.
                match = re.search(
                    r'^ARDUINO\s+(?P<version>\d+\.\d+\.\d+)',
                    revision_file.read(),
                    re.VERBOSE | re.MULTILINE)
                version_text = match.group('version')
                if (packaging.version.parse(version_text) <
                        packaging.version.parse('1.5.0')):
                    self._is_before_v1_5_0 = True

                self._runtime_cfg['runtime'] = {
                    'ide': {
                        'path': self._home_path,
                        'version': version_text.replace('.', '_')
                    }
                }
