import click

import vector_house.indexer as ind


@click.command()
@click.option("--index", is_flag=True, default=False, help="Recreates index")
def app(index: bool):
    """Default, launches gui"""

    if not index:
        # Start normal
        # TODO
        print("TODO")
    else:
        # Started with a parameter
        print("(Re)creating index")
        ind.recreate_index()
