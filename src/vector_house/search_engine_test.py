from vector_house.database import WikiDatabase

DB_PATH_TEST = "wiki-test-index.db"
db = WikiDatabase(path=DB_PATH_TEST)
db.connect_database()


def test_find_vectors() -> None:
    """Tests getting weights for terms"""
    db.drop_if_exists()
    db.create_database()

    terms = ["t1", "t2", "t3", "t4"]
    term_ids = [db.insert_term(x) for x in terms]
    doc_titles = ["d1", "d2", "d3", "d4"]
    doc_ids = [db.insert_document(x, "body") for x in terms]

    db.insert_value(term_ids[0], doc_ids[0], 1)
    db.insert_value(term_ids[1], doc_ids[1], 2)
    db.insert_value(term_ids[1], doc_ids[2], 3)
    db.insert_value(term_ids[2], doc_ids[0], 4)
    db.insert_value(term_ids[2], doc_ids[3], 5)

    assert db.get_values_for_term(terms[0]) == {
        doc_ids[0]: 1,
    }
    assert db.get_values_for_term(terms[1]) == {
        doc_ids[1]: 2,
        doc_ids[2]: 3,
    }
    assert db.get_values_for_term(terms[2]) == {
        doc_ids[0]: 4,
        doc_ids[3]: 5,
    }
    assert db.get_values_for_term(terms[3]) == {}

    db.drop_database()
    db.commit()
