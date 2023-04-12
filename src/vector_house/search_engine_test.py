import numpy as np
from database import WikiDatabase
from database_test import run_with_db
import search_engine as se


@run_with_db
def test_find_vectors(db: WikiDatabase) -> None:
    """Tests getting weights for terms"""

    terms = ["t1", "t2", "t3", "t4"]
    term_ids = [db.insert_term(x) for x in terms]
    doc_titles = ["d1", "d2", "d3", "d4"]
    doc_ids = [db.insert_document(x, "body") for x in doc_titles]

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


def test_cos_sim() -> None:
    """Tests counting cosine similarity"""

    wanted = np.array([1, 1, 1])

    assert (
        round(se.count_cos_sim(np.array([0.1, 0.2, 0.3]), np.array([0.4, 0.5, 0.6])), 2)
        == 0.97
    )
    assert round(se.count_cos_sim(np.array([0.1, 0.2, 0.3]), wanted), 2) == 0.93
    assert round(se.count_cos_sim(np.array([0, 0, 0]), wanted), 2) == -1


def test_search() -> None:
    """Tests finding top 10 most similar documents"""

    data = {
        1: np.array([0, 0, 0]),
        2: np.array([0.1, 0.3, 0.1]),
        3: np.array([0.2, 0.1, 0.15]),
        4: np.array([0, 0, 0.1]),
        5: np.array([0.5, 0.4, 0.3]),
        6: np.array([0.3, 0.3, 0.25]),
        7: np.array([0.45, 0.5, 0.45]),
        8: np.array([0.1, 0.7, 0.7]),
        9: np.array([0.8, 0.4, 0.8]),
        10: np.array([0.9, 0.7, 0.6]),
        11: np.array([0.7, 0.7, 0.7]),
        12: np.array([0.2, 0.4, 0.9]),
        13: np.array([0, 0, 0]),
    }
    assert se.search(data) == [11, 7, 6, 10, 5, 3, 9, 8, 2, 12]

    data = {
        1: np.array([0, 0, 0]),
        2: np.array([0.1, 0.3, 0.1]),
        3: np.array([0.2, 0.1, 0.15]),
    }
    assert se.search(data) == [3, 2, 1]

    assert se.search({}) == []
