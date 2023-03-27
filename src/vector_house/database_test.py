from .database import WikiDatabase
import random as rnd

DB_PATH_TEST = "wiki-test-index.db"
db = WikiDatabase(path=DB_PATH_TEST)
db.connect_database()


def test_insert_document() -> None:
    db.drop_if_exists()
    db.create_database()
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

    db.drop_database()
    db.commit()


def test_insert_term() -> None:
    db.drop_if_exists()
    db.create_database()
    for i in range(8):
        name = "Term " + str(i)

        id1 = db.insert_term(name)
        assert id1 == i + 1

        id2 = db.get_term_id(name)
        assert id1 == id2

    db.drop_database()
    db.commit()


def test_insert_value() -> None:
    db.drop_if_exists()
    db.create_database()
    for i in range(8):
        title = "Title " + str(i)
        text = "Text " + str(i)
        db.insert_document(title, text)

        name = "Term " + str(i)
        db.insert_term(name)

    for i in range(8):
        doc_id = rnd.randint(1, 8)
        term_id = rnd.randint(1, 8)
        value = rnd.randint(0, 1000) / 1000

        db.insert_value(term_id, doc_id, value)
        stored = db.get_value_by_ids(term_id, doc_id)
        assert stored == value
    db.drop_database()
    db.commit()
