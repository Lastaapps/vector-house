from typing import Callable
from database import WikiDatabase
import random as rnd

DB_PATH_TEST = "wiki-test-index.db"


def run_with_db(fun: Callable[[WikiDatabase], None]) -> None:
    """Decorator for database testing"""

    def run():
        db = WikiDatabase(path=DB_PATH_TEST)
        db.connect_database()
        db.drop_if_exists()
        db.create_database()

        def close():
            db.drop_database()
            db.commit()
            db.close()

        try:
            fun(db)
        except AssertionError:
            close()
            raise
        else:
            close()

    return run


@run_with_db
def test_insert_document(db: WikiDatabase) -> None:
    for i in range(8):
        title = "Title " + str(i)
        text = "Text " + str(i)

        id1 = db.insert_document(title, text)
        assert id1 == i + 1

        id2 = db.get_doc_id(title)
        assert id1 == id2

        title_db, text_db = db.get_doc_by_id(id1)
        assert title_db == title
        assert text_db == text


@run_with_db
def test_insert_term(db: WikiDatabase) -> None:
    for i in range(8):
        name = "Term " + str(i)

        id1 = db.insert_term(name)
        assert id1 == i + 1

        id2 = db.get_term_id(name)
        assert id1 == id2


@run_with_db
def test_insert_value(db: WikiDatabase) -> None:
    TEST_SIZE = 42

    for i in range(TEST_SIZE):
        title = "Title " + str(i)
        text = "Text " + str(i)
        db.insert_document(title, text)

        name = "Term " + str(i)
        db.insert_term(name)

    for i in range(TEST_SIZE):
        doc_id = rnd.randint(1, TEST_SIZE)
        term_id = rnd.randint(1, TEST_SIZE)
        value = rnd.randint(0, 1000) / 1000

        if db.get_value_by_ids(term_id, doc_id) != 0:
            continue

        db.insert_value(term_id, doc_id, value)
        stored = db.get_value_by_ids(term_id, doc_id)
        assert stored == value
