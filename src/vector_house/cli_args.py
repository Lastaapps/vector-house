import click

import indexer as ind
from database import WikiDatabase


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
        wiki_db = WikiDatabase()
        wiki_db.connect_database()

        print("Showing index stats")
        wiki_db.print_stats()
        has_index = wiki_db.has_index()
        print(f"Indexes created: {has_index}")
    else:
        # Started with a parameter
        print("(Re)creating index")
        ind.recreate_index(limit, size)
