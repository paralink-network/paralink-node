import argparse
import textwrap

from src import create_app


def parse_arguments():
    """Parses command line parameters using `argparse` module.
    """
    parser = argparse.ArgumentParser(
        prog="paralink-node",
        description=textwrap.dedent(
            """\
        Paralink Network

        Paralink Node is responsible for accessing real world data and relaying it back
        to smart contracts via JSON RPC.
        """
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("-H", "--host", help="specify host", default="127.0.0.1")
    parser.add_argument("-p", "--port", help="specify JSON RPC port", default=7424)
    parser.add_argument("-t", "--timeout", help="specify IPFS GET timeout", default=3)

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()

    app = create_app(args)
    app.run(host=args.host, port=args.port, debug=True)
