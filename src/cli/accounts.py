from docopt import docopt

from src.network import accounts

__doc__ = """
Usage: paralink-node accounts <command> [<arguments> ...] [options]

Commands:
   import <private_key>     Import private key into paralink dir.

Manage accounts.
"""


def main():
    args = docopt(__doc__)

    try:
        if args["<command>"] == "import":
            accounts.load()
            accounts.import_key(*args["<arguments>"])
    except TypeError:
        print(
            f"Invalid arguments for command '{args['<command>']}'. Try paralink-node accounts --help"
        )
        return


if __name__ == "__main__":
    main()
