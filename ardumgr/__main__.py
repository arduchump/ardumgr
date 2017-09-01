#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Console script for ardumgr."""

import click
import yaml
from pathlib import Path
from .ardumgr import ArduMgr
from .programmer import Programmer
from .configs import Platform


def calc_max_len(str_list, spaces=4):
    max_len = 0
    for astr in str_list:
        max_len = max(max_len, len(astr))

    max_len += spaces
    return max_len


def print_table(alist, callback):
    max_len = calc_max_len(alist)
    for element in alist:
        result = callback(element)
        if not result:
            continue

        left, right = result
        click.echo("%s%s%s" % (left, " " * (max_len - len(left)), right))


@click.group()
@click.option('-c', '--config', type=click.File('r'), default=None)
@click.option('-p', '--preference', multiple=True, default=None)
@click.pass_context
def main(ctx, config, preference):
    """Console script for ardumgr."""

    configs = dict()
    if config:
        configs.update(yaml.load(config))

    if preference:
        for value in preference:
            parts = value.split("=", 1)
            if len(parts) != 2:
                raise click.BadOptionUsage(
                    "Wrong format of preference : %s" % value)

            configs[parts[0].strip()] = parts[1].strip()

    if "runtime.ide.path" not in configs:
        raise click.BadOptionUsage(
            'Preference "runtime.ide.path" undefined! '
            'It must be defined by "-p" option or contained in config file.')

    ide_path = configs["runtime.ide.path"].strip()
    if (not ide_path) or (not Path(ide_path).exists()):
        raise click.BadOptionUsage(
            "Arduino IDE path not found: %s" % ide_path)

    manager = ArduMgr(configs)
    ctx.obj["manager"] = manager


@main.group()
@click.pass_context
def show(ctx):
    """
    Show details
    """


@show.command(name="platforms")
@click.pass_context
def show_platforms(ctx):
    """
    Show supported platforms
    """

    manager = ctx.obj["manager"]

    def parse(id_):
        platform = Platform(manager, id_)
        return id_, platform.cfgs["name"]
    print_table(manager.platforms, parse)


@show.command(name="oss")
@click.pass_context
def show_oss(ctx):
    """
    Show supported os
    """

    manager = ctx.obj["manager"]

    for anos in manager.oss:
        click.echo(anos)


@show.command(name="programmers")
@click.argument("platform")
@click.pass_context
def show_programmers(ctx, platform):
    """
    Show supported programmers on specific platform.
    """

    manager = ctx.obj["manager"]

    if platform not in manager.platforms:
        raise click.BadParameter("Unsupported platform!")

    platform = Platform(manager, platform)

    def parse(id_):
        name = platform.cfgs["programmers.%s.name" % id_]
        return id_, name
    print_table(platform.programmers, parse)


@show.command(name="boards")
@click.argument("platform")
@click.pass_context
def show_boards(ctx, platform):
    """
    Show supported boards on specific platform.
    """

    manager = ctx.obj["manager"]

    if platform not in manager.platforms:
        raise click.BadParameter("Unsupported platform!")

    platform = Platform(manager, platform)

    def parse(id_):
        name = platform.cfgs["boards.%s.name" % id_]
        return id_, name

    print_table(platform.boards, parse)


@show.command(name="tools")
@click.argument("platform")
@click.pass_context
def show_tools(ctx, platform):
    """
    Show supported tools on specific platform.
    """

    manager = ctx.obj["manager"]

    if platform not in manager.platforms:
        raise click.BadParameter("Unsupported platform!")

    platform = Platform(manager, platform)

    def parse(id_):
        # Tools does not have a name
        return id_, ""

    print_table(platform.tools, parse)


@show.command(name="tools")
@click.argument("platform")
@click.pass_context
def show_tools(ctx, platform):
    """
    Show supported tools on specific platform.
    """

    manager = ctx.obj["manager"]

    if platform not in manager.platforms:
        raise click.BadParameter("Unsupported platform!")

    platform = Platform(manager, platform)

    def parse(id_):
        # Tools does not have a name
        return id_, ""

    print_table(platform.tools, parse)


@show.command(name="version")
@click.pass_context
def show_version(ctx):
    """
    Show Arduino IDE version
    """

    manager = ctx.obj["manager"]

    click.echo(manager.version)


@show.command(name="intversion")
@click.pass_context
def show_intversion(ctx):
    """
    Show Arduino IDE version (int value)
    """

    manager = ctx.obj["manager"]

    click.echo(manager.int_version)


@show.command(name="pref")
@click.argument("key")
@click.pass_context
def show_pref(ctx, key):
    """
    Show internal preferences (RAW)
    """

    manager = ctx.obj["manager"]
    platform = Platform(manager, manager._runtime_cfgs["ardumgr.platform"])
    programmer = Programmer(platform)
    click.echo(programmer._platform.cfgs.get_overrided(key))


@show.command(name="epref")
@click.argument("key")
@click.pass_context
def show_epref(ctx, key):
    """
    Show internal preferences (EXPANDED)
    """

    manager = ctx.obj["manager"]
    platform = Platform(manager, manager._runtime_cfgs["ardumgr.platform"])
    programmer = Programmer(platform)
    click.echo(programmer._platform.cfgs.get_expanded(key))


if __name__ == "__main__":
    main(obj={})
