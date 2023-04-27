import click
from typing import List
import numpy as np

import vector_house.indexer as ind
import vector_house.search_engine as sr
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


@click.command("search", help="Searches for the query given")
@click.option("--db", default=DB_DEFAULT_FILENAME)
@click.argument("query", nargs = -1)
def search(query: List[str], db: str):
    """Searches for the query given"""
    if len(query) == 0:
        print("Empty query, exiting")
        return

    print("Searching for:", " ".join(query))

    wiki_db = WikiDatabase(db)
    vectors = sr.find_vectors(wiki_db, query)
    pages = sr.search(vectors)
    titles = [(x[0], x[1], wiki_db.get_doc_by_id(x[1])[0]) for x in pages]
    for sim, doc_id, title in titles:
        print(f"{sim:.2f} {doc_id:6d}:", title)


@click.command("sim", help="Show similar docs to the doc id given")
@click.option("--db", default=DB_DEFAULT_FILENAME)
@click.argument("doc_id", type=int)
def sim(doc_id: int, db: str):
    """Searches for the query given"""

    wiki_db = WikiDatabase(db)

    src_title, _ = wiki_db.get_doc_by_id(doc_id)
    print(f"Searching similar pages to: {doc_id} - {src_title}")

    dict_term_val = wiki_db.get_terms_for_doc(doc_id)
    keywords = list(dict_term_val.keys())
    sim_to = np.array(list(dict_term_val.values()))
    vectors = sr.find_vectors(wiki_db, keywords)
    pages = sr.search(vectors, sim_to)
    titles = [(x[0], x[1], wiki_db.get_doc_by_id(x[1])[0]) for x in pages]
    for sim, doc_id, title in titles:
        print(f"{sim:.2f} {doc_id:6d}:", title)


@click.command("show", help="Show document by it's id")
@click.option("--db", default=DB_DEFAULT_FILENAME)
@click.argument("doc_id", type=int)
def show(doc_id: int, db: str):
    """Searches for the query given"""

    print("Searching for doc with id:", doc_id)

    wiki_db = WikiDatabase(db)
    title, text = wiki_db.get_doc_by_id(doc_id)
    print(title)
    print(text)


db_index.add_command(db_index_create)
db_index.add_command(db_index_drop)

app.add_command(info)
app.add_command(index)
app.add_command(db_index)
app.add_command(benchmark)
app.add_command(search)
app.add_command(sim)
app.add_command(show)
