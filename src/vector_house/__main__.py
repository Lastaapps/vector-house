import os

import vector_house.indexer as ind


def pwd() -> None:
    dir_path = os.path.dirname(os.path.realpath(__file__))
    os.chdir(dir_path)
    print(f"Running in {dir_path}")


def main() -> None:
    print("Hello, vector home is starting...")
    pwd()

    ind.create_index()

    print("Bye")


main()
