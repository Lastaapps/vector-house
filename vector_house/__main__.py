import os

import vector_house.cli_args as args


def pwd() -> None:
    module_dir = os.path.dirname(os.path.realpath(__file__))
    work_dir = os.getcwd()
    os.chdir(work_dir)
    print(f"Running in {work_dir}")


def main() -> None:
    print("Hello, vector home is starting...")
    pwd()

    args.app()

    print("Bye")


main()
