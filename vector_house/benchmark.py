from vector_house.database import WikiDatabase
from vector_house.indexer import recreate_index
from vector_house.search_engine import search, find_vectors
from typing import Callable
import numpy as np
import os
import os.path
import time

BENCHMARK_DIR = "benchmark"

sizes = [2000, 8000, 16000, 32000]
# limits   = [100, 200, 400, 800, 0]
# top_docs = [100, 200, 400, 800, 0]
limits = [200, 800, 0]
top_docs = [0]


def iterate(fun: Callable[[str, int, int, int, bool], None]):
    """size, limit, top_docs, sequential"""
    for size in sizes:
        for limit in limits:
            for top_doc in top_docs:
                db_name = f"{BENCHMARK_DIR}/wiki-index-{size}-{limit}-{top_doc}.db"

                fun(db_name, size, limit, top_doc, False)
                fun(db_name, size, limit, top_doc, True)


def create_indexes():
    if not os.path.isdir(BENCHMARK_DIR):
        os.mkdir(BENCHMARK_DIR)

    def create_index(
        db_name: str, size: int, limit: int, top_docs: int, sequential: bool
    ):
        if sequential:
            return

        if os.path.isfile(db_name):
            print(f"Skipping {db_name}")
            return

        print(f"Creating name {db_name}")
        wiki_db = WikiDatabase(db_name)
        wiki_db.connect_database()
        wiki_db.create_if_needed()
        recreate_index(size, limit, top_docs, wiki_db)

    iterate(create_index)
    print("Done")


search_queries = [
    x.split()
    for x in [
        "adolf stalin",
        "banana monkey",
        "argentina america bull blanket",
        "production neighborhood insure point detail tract salmon garlic lend solid disappoint asylum grow space crosswalk egg habit railroad timber interface",
        "exclude infrastructure illustrate president distinct surface thought save public trail attract announcement body security consideration fuel if lie prosper display",
        "retired toss rider string cool absolute charter obligation situation salvation error nap cat flour digital original manner jockey rugby pledge",
        "fascinate houseplant judge positive patience invisible prosecute practice spite physics hemisphere cassette program speed return falsify provoke disagree baseball competition",
    ]
]


def benchmark():
    delim = "\t"
    print(
        "BR",
        "Size",
        "Limit",
        "TopDocs",
        "Sequential",
        "Terms",
        "Documents",
        "Values",
        "Time",
        sep=delim,
    )

    def benchmark_db(
        db_name: str, size: int, limit: int, top_docs: int, sequential: bool
    ):
        wiki_db = WikiDatabase(db_name)
        wiki_db.connect_database()

        if sequential:
            wiki_db.drop_index()
        else:
            wiki_db.create_index()

        start_time = time.time()

        for query in search_queries:
            vectors = find_vectors(wiki_db, query)
            pages = [x[1] for x in search(vectors)]
            for i in range(len(pages)):
                page_id = pages[i]
                dict_term_val = wiki_db.get_terms_for_doc(page_id)
                keywords = list(dict_term_val.keys())
                sim_to = np.array(list(dict_term_val.values()))
                vectors = find_vectors(wiki_db, keywords)
                pages = [x[1] for x in search(vectors, sim_to)]

        end_time = time.time()

        terms, documents, values = wiki_db.get_stats()
        duration = end_time - start_time
        print(
            "BR",
            size,
            limit,
            top_docs,
            int(sequential),
            terms,
            documents,
            values,
            round(duration, 1),
            sep=delim,
        )

    iterate(benchmark_db)
