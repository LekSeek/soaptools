from argparse import Namespace, ArgumentParser


class Action:
    name: str
    help: str

    @classmethod
    def execute(cls, arguments: Namespace):
        pass

    @classmethod
    def add_arguments_to_action_parser(cls, action_parser: ArgumentParser):
        raise NotImplementedError()
