from docopt import docopt
from src.config import __version__

import src.cli.node
import src.cli.accounts
from src.logging import setup_logging

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

    setup_logging()

    if args["<command>"] == "node":
        src.cli.node.main()
    elif args["<command>"] == "accounts":
        src.cli.accounts.main()


if __name__ == "__main__":
    main()
