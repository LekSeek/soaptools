import argparse
import sys

from soaptools.actions import ALL_ACTIONS
from soaptools.exceptions import ApplicationException
from soaptools.helpers.py import Logger


def execute_command_from_args(args=None):
    if args is None:
        args = sys.argv[1:]
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(help="commands", dest="command")

    actions_map = {}
    for action in ALL_ACTIONS:
        action_parser = subparsers.add_parser(action.name, help=action.help)
        action.add_arguments_to_action_parser(action_parser)
        actions_map[action.name] = action

    args = parser.parse_args(args)
    if args.command in actions_map:
        actions_map[args.command].execute(args)
    else:
        Logger.info("Action not chosen. To list available actions try: python -msoaptools --help")
