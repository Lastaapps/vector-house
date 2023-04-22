import click

import vector_house.indexer as ind
from vector_house.database import WikiDatabase


@click.command()
@click.option("--index", is_flag=True, default=False, help="Recreates index")
@click.option("--db-index-create", is_flag=True, default=False, help="Creates db index")
@click.option("--db-index-drop", is_flag=True, default=False, help="Deletes db index")
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
def app(
    index: bool, limit: int, size: int,
        db_index_create: bool, db_index_drop: bool,
        ):
    """Default, launches gui"""

    if db_index_create:
        wiki_db = WikiDatabase()
        wiki_db.connect_database()
        print(f"Has index: {has_index}")
        wiki_db.create_index()
        print("Done, index created")
        return

    if db_index_drop:
        wiki_db = WikiDatabase()
        wiki_db.connect_database()
        has_index = wiki_db.has_index()
        print(f"Has index: {has_index}")
        wiki_db.drop_index()
        print("Done, index dropped")
        return
        
    if index:
        # Started with a parameter
        print("(Re)creating index")
        ind.recreate_index(limit, size)
        return

    # Start normal
    wiki_db = WikiDatabase()
    wiki_db.connect_database()

    print("Showing index stats")
    wiki_db.print_stats()
    has_index = wiki_db.has_index()
    print(f"Indexes created: {has_index}")
