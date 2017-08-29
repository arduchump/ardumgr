#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Console script for ardumgr."""

import click
from .ardumgr import ArduMgr


@click.command()
@click.argument('home_path')
def main(home_path):
    """Console script for ardumgr."""

    am = ArduMgr(home_path)


if __name__ == "__main__":
    main()
