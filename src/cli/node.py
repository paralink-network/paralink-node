import argparse
import textwrap
from docopt import docopt

from src import create_app

__doc__ = """
Usage: paralink-node node <command> [<arguments> ...] [options]

Commands:
   start [--host]           Start the node.

Options:
   --host <host>            Specify host to run on [default: 127.0.0.1]
   --port <port>            Specify port to run on [default: 7424]
   --timeout <timeout>      Specify IPFS GET timeout [default: 3]

Use node command to start the node.
"""


def main():
    args = docopt(__doc__)

    if args["<command>"] == "start":
        app = create_app(args)
        app.run(host=args["--host"], port=args["--port"], debug=True)


if __name__ == "__main__":
    main()
