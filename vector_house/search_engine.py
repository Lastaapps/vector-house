from typing import List, Dict, Tuple
import numpy as np
from queue import PriorityQueue

from vector_house.database import WikiDatabase


def find_vectors(db: WikiDatabase, terms: List[str]) -> Dict[int, np.array]:
    """
    Finds weight vectors for the terms given
    """
    size = len(terms)
    to_return: Dict[int, np.array] = dict()

    print("Finding docs")
    for i in range(size):
        term = terms[i]
        from_db = db.get_values_for_term(term)

        for doc_with_value in from_db.items():
            doc_id = doc_with_value[0]
            if doc_id not in to_return.keys():
                to_return[doc_id] = np.zeros(size)

            value = doc_with_value[1]
            to_return[doc_id][i] = value

    return to_return


def count_cos_sim(vec1: np.array, vec2: np.array) -> float:
    """
    Counts cosine similarity of two vectors
    """

    if np.all(vec1 == 0) or np.all(vec2 == 0):
        return -1

    norm_vec1 = np.linalg.norm(vec1)  # euclidean
    norm_vec2 = np.linalg.norm(vec2)
    return np.dot(vec1, vec2) / (norm_vec1 * norm_vec2)


def search(data: Dict[int, np.array], wanted: np.array = None) -> List[int]:
    """
    Returns ids of top 10 most relevant documents in order
    """

    if not data:
        return []

    if wanted is None:
        num_of_terms = len(list(data.values())[0])
        wanted = np.ones(num_of_terms)

    top_docs = PriorityQueue(maxsize=11)

    print("Counting cos similarity")
    for doc_id, vector in data.items():
        cos_sim = count_cos_sim(vector, wanted)
        top_docs.put((cos_sim, doc_id))

        if top_docs.full():
            top_docs.get()

    if top_docs.full():
        top_docs.get()

    res = []
    while not top_docs.empty():
        res.append(top_docs.get()[1])

    return res[::-1]  # swap
