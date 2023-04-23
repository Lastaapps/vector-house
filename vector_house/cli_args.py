import click

import vector_house.indexer as ind
from vector_house.database import WikiDatabase, DB_DEFAULT_FILENAME
import vector_house.benchmark as bk


@click.group(
    help="Vector house command line interface\nManage indexes and more.",
)
def app():
    """Root, idk"""
    pass


@click.command("info", help="Show info about an index (DB)")
@click.option("--db", default=DB_DEFAULT_FILENAME)
def info(db: str):
    # Start normal
    wiki_db = WikiDatabase(db)
    wiki_db.connect_database()

    print("Showing index stats")
    wiki_db.print_stats()
    has_index = wiki_db.has_index()
    print(f"Indexes created: {has_index}")


@click.command("index", help="Creates index (DB)")
@click.option("--db", default=DB_DEFAULT_FILENAME)
@click.option(
    "--limit",
    is_flag=False,
    default=0,
    help="Limits the number of first words to be processed",
)
@click.option(
    "--top-docs",
    is_flag=False,
    default=0,
    help="For each term store only top k docs",
)
@click.option(
    "--size",
    is_flag=False,
    default=0,
    help="Number of documents to index",
)
def index(size: int, limit: int, top_docs: int, db: str):
    """Handles the list command"""

    # Started with a parameter
    print("Creating index")
    ind.recreate_index(size, limit, top_docs, WikiDatabase(db))


@click.command("create", help="Crete database column indexes")
@click.option("--db", default=DB_DEFAULT_FILENAME)
def db_index_create(db: str):
    wiki_db = WikiDatabase(db)
    wiki_db.connect_database()
    has_index = wiki_db.has_index()
    print(f"Has index: {has_index}")
    wiki_db.create_index()
    print("Done, index created")


@click.command("drop", help="Drop database column indexes")
@click.option("--db", default=DB_DEFAULT_FILENAME)
def db_index_drop(db: str):
    wiki_db = WikiDatabase(db)
    wiki_db.connect_database()
    has_index = wiki_db.has_index()
    print(f"Has index: {has_index}")
    wiki_db.drop_index()
    print("Done, index dropped")


@click.group("db-index", help="Handle database column indexes")
def db_index():
    """Handles the dish command"""
    pass


@click.command("benchmark", help="Benchmark databases")
@click.option(
    "--create-index", is_flag=True, default=False, help="Recreates benchmark indexes"
)
def benchmark(create_index: bool):
    """Handles the info command"""

    if create_index:
        bk.create_indexes()
    else:
        bk.benchmark()


db_index.add_command(db_index_create)
db_index.add_command(db_index_drop)

app.add_command(info)
app.add_command(index)
app.add_command(db_index)
app.add_command(benchmark)
