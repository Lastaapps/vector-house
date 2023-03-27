from typing import List, Dict, Tuple
import numpy as np
from vector_house.database import WikiDatabase


def find_vectors(db: WikiDatabase, terms: List[str]) -> Dict[int, np.array]:
    """
    Finds weight vectors for the terms given
    """
    size = len(terms)
    to_return: Dict[int, np.array] = dict()

    for i in range(size):
        term = terms[i]
        from_db = db.get_values_for_term(term)

        for doc_with_value in from_db.items():
            doc_id = doc_with_value[0]
            if doc_id not in to_return.keys():
                to_return[doc_id] = np.zeros(size)

            value = doc_with_value[1]
            to_return[doc_id][i] = value


def search(data: Dict[int, np.array]) -> List[int]:
    pass
