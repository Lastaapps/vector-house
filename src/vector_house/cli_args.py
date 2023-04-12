import click

import indexer as ind


@click.command()
@click.option("--index", is_flag=True, default=False, help="Recreates index")
@click.option(
    "--limit",
    is_flag=False,
    default=0,
    help="Limits the number of first words to be processed",
)
@click.option(
    "--size",
    is_flag=False,
    default=0,
    help="Number of documents to index",
)
def app(index: bool, limit: int, size: int):
    """Default, launches gui"""

    if not index:
        # Start normal
        # TODO
        print("TODO")
    else:
        # Started with a parameter
        print("(Re)creating index")
        ind.recreate_index(limit, size)
