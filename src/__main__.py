from docopt import docopt
from src.config import __version__

__doc__ = """
Paralink Node is responsible for accessing real world data and relaying it back
to smart contracts via JSON RPC.

Usage: paralink-node [--version] <command> [<args>...] [options <args>]

Commands:
   node       node actions, such as start.
   accounts   manage accounts.

options:
   -h, --help       display this message.
   -v, --version    show version and exit.

see 'paralink-node <command> --help' for more information on a specific command.
"""


def main():
    args = docopt(__doc__, version=__version__, options_first=True)

    if args["<command>"] == "node":
        import src.cli.node

        src.cli.node.main()


if __name__ == "__main__":
    main()
