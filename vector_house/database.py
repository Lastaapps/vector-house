import time
import sqlite3
from sqlite3 import Connection
from typing import Tuple, Dict, List
import numpy as np

DB_DEFAULT_FILENAME = "wiki-index.db"


class WikiDatabase:
    def __init__(self, path: str = DB_DEFAULT_FILENAME, autoConnect: bool = True):
        self.path = path
        self.con: Connection | None = None
        if autoConnect:
            self.connect_database()

    def connect_database(self) -> None:
        """
        Creates the database file if needed
        and connects to it
        """
        if self.con != None: return
        self.con = sqlite3.connect(self.path, check_same_thread=False)
        self.create_if_needed()

    def create_if_needed(self) -> None:
        if not self.has_schema():
            self.create_database()

    def drop_if_exists(self) -> None:
        if self.has_schema():
            self.drop_database()

    def has_schema(self) -> bool:
        """Creates the db if it's schema is empty"""

        cur = self.con.cursor()

        cur = cur.execute(
            """
SELECT count(name) FROM sqlite_master WHERE type='table';
                """
        )

        return cur.fetchone()[0] > 2

    def create_database(self) -> None:
        """Creates a database scheme"""

        cur = self.con.cursor()
        cur.execute(
            """
CREATE TABLE term (
    term_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL
);
        """
        )

        cur.execute(
            """
CREATE TABLE document (
    doc_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    text TEXT NOT NULL
);
        """
        )

        cur.execute(
            """
CREATE TABLE value (
    doc_id INTEGER NOT NULL,
    term_id INTEGER NOT NULL,
    value DOUBLE PRECISION NOT NULL,
    FOREIGN KEY(term_id) REFERENCES document(term_id),
    FOREIGN KEY(doc_id) REFERENCES document(doc_id)
);
        """
        )

        self.commit()

    def drop_database(self) -> None:
        """
        Drops database schema
        """

        cur = self.con.cursor()

        cur.execute(
            """
DROP TABLE term;
        """
        )
        cur.execute(
            """
DROP TABLE document;
        """
        )
        cur.execute(
            """
DROP TABLE value;
        """
        )

        self.commit()

    def commit(self) -> None:
        """
        Commits staged changes
        """
        self.con.commit()

    def close(self) -> None:
        """
        Commits staged changes
        """
        self.con.close()

    def insert_document(self, title: str, text: str) -> int:
        """
        Inserts a new document
        Commit has to be called later!
        returns it's new id
        """
        cur = self.con.cursor()

        res = cur.execute(
            """
INSERT INTO document(title, text) VALUES(?, ?) RETURNING doc_id;
                    """,
            [title, text],
        )

        return res.fetchone()[0]

    def insert_term(self, name: str) -> int:
        """
        Inserts a new term
        Commit has to be called later!
        returns it's new id
        """
        cur = self.con.cursor()

        res = cur.execute(
            """
INSERT INTO term(name) VALUES(?) RETURNING term_id;
                    """,
            [name],
        )

        return res.fetchone()[0]

    def insert_value(self, term_id: int, doc_id: int, value: float) -> None:
        """
        Inserts a new value relation
        Commit has to be called later!
        returns it's new id
        """
        cur = self.con.cursor()

        res = cur.execute(
            """
INSERT INTO value(term_id, doc_id, value) VALUES(?, ?, ?);
                    """,
            [term_id, doc_id, value],
        )

    def has_term(self, name: str) -> bool:
        """
        Checks if the term is already presented
        """
        cur = self.con.cursor()

        res = cur.execute(
            """
SELECT name FROM term WHERE name = ?
                    """,
            [name],
        )

        return len(res.fetchall()) > 0

    def get_term_id(self, name: str) -> int:
        """
        Checks if the term is already presented
        """
        cur = self.con.cursor()

        res = cur.execute(
            """
SELECT term_id FROM term WHERE name = ?
                    """,
            [name],
        )

        return res.fetchone()[0]

    def get_term_by_id(self, id: int) -> str:
        """
        Checks if the term is already presented
        """
        cur = self.con.cursor()

        res = cur.execute(
            """
SELECT name FROM term WHERE term_id = ?
                    """,
            [id],
        )

        return res.fetchone()[0]

    def get_doc_id(self, title: str) -> int:
        """
        Checks if the term is already presented
        """
        cur = self.con.cursor()

        res = cur.execute(
            """
SELECT doc_id FROM document WHERE title = ?
                    """,
            [title],
        )

        return res.fetchone()[0]

    def get_doc_by_id(self, id: str) -> Tuple[str, str]:
        """
        Checks if the term is already presented
        """
        cur = self.con.cursor()

        res = cur.execute(
            """
SELECT title, text FROM document WHERE doc_id = ?
                    """,
            [id],
        )

        fetched = res.fetchone()
        return (fetched[0], fetched[1])

    def get_value_by_ids(self, term_id: int, doc_id: int) -> float:
        """
        Gets value for the pair given
        """
        cur = self.con.cursor()

        res = cur.execute(
            """
SELECT value FROM value WHERE term_id = ? AND doc_id = ?;
                    """,
            [term_id, doc_id],
        )

        return (res.fetchone() or [0.0])[0]

    def get_values_for_term(self, term_name: str) -> Dict[int, np.float32]:
        """
        Gets value for the pair given
        """
        cur = self.con.cursor()

        res = cur.execute(
            """
SELECT doc_id, value FROM term
JOIN value USING(term_id)
JOIN document USING(doc_id)
WHERE term.name = ?
ORDER BY term_id;
                    """,
            [term_name],
        )

        rows = res.fetchall()
        doc_id_iter = (x[0] for x in rows)
        value_iter = (np.float32(x[1]) for x in rows)
        to_return = dict(zip(doc_id_iter, value_iter))

        return to_return

    def get_values_for_terms(self, term_names: List[str]) -> Dict[int, np.float32]:
        """
        Gets value for the pair given
        """
        cur = self.con.cursor()

        question_marks = ','.join('?' * len(term_names))
        res = cur.execute(
            f"""
SELECT doc_id, value, term_rank FROM term
JOIN value USING(term_id)
JOIN document USING(doc_id)
JOIN (
    SELECT term_id, rank() OVER win AS term_rank FROM term
    WHERE name IN ({question_marks})
    WINDOW win AS (ORDER BY term_id)
) USING(term_id)
WHERE term.name IN ({question_marks})
ORDER BY doc_id, term_rank;
                    """,
            term_names + term_names,
        )

        rows = res.fetchall()
        dct : Dict[int, np.array[np.float32]] = {}
        for row in rows:
            doc_id, value, term_rank = row
            if doc_id not in dct.keys():
                dct[doc_id] = np.zeros(len(term_names))
            dct[doc_id][term_rank - 1] = value

        return dct

    def get_terms_for_doc(self, doc_id: int) -> Dict[str, np.float32]:
        """
        Gets terms in given document
        """
        cur = self.con.cursor()

        res = cur.execute(
            """
SELECT term.name, value FROM term
JOIN value USING(term_id)
JOIN document USING(doc_id)
WHERE doc_id = ?
ORDER BY term_id;
                    """,
            [doc_id],
        )

        rows = res.fetchall()
        term_names = [row[0] for row in rows]
        values = (np.float32(x[1]) for x in rows)
        to_return = dict(zip(term_names, values))
        return to_return

    def has_index(self) -> bool:
        """Checks if the database has created indexes"""
        cur = self.con.cursor()
        res = cur.execute(
            """
SELECT count(*) FROM sqlite_master WHERE type='index' and name='value_term_id';
                    """
        )

        return res.fetchone()[0] != 0

    def create_index(self):
        print("Creating index")

        cur = self.con.cursor()
        cur.execute(
            """
CREATE INDEX IF NOT EXISTS value_term_id ON value (term_id);
                    """
        )
        cur.execute(
            """
CREATE INDEX IF NOT EXISTS value_doc_id ON value (doc_id);
                    """
        )
        cur.execute(
            """
CREATE INDEX IF NOT EXISTS term_term_id ON value (term_id);
                    """
        )
        cur.execute(
            """
CREATE INDEX IF NOT EXISTS document_doc_id ON value (doc_id);
                    """
        )

    def drop_index(self):
        print("Dropping index")

        cur = self.con.cursor()
        cur.execute(
            """
DROP INDEX IF EXISTS term_term_id;
                    """
        )
        cur.execute(
            """
DROP INDEX IF EXISTS document_doc_id;
                    """
        )
        cur.execute(
            """
DROP INDEX IF EXISTS value_doc_id;
                    """
        )
        cur.execute(
            """
DROP INDEX IF EXISTS value_term_id;
                    """
        )

    def get_stats(self) -> Tuple[int, int, int]:
        """
        Returns the number of rows in the DB tables
        Row counts are in the order [terms, documents, values]
        """
        cur = self.con.cursor()

        res = cur.execute(""" SELECT count(*) FROM term; """)
        terms = res.fetchone()[0]

        res = cur.execute(""" SELECT count(*) FROM document; """)
        documents = res.fetchone()[0]

        res = cur.execute(""" SELECT count(*) FROM value; """)
        values = res.fetchone()[0]

        return (terms, documents, values)

    def print_stats(self) -> None:
        """Prints info about DB table sizes"""
        cur = self.con.cursor()

        terms, documents, values = self.get_stats()
        print(f"Terms: {terms}")
        print(f"Documents: {documents}")
        print(f"Values: {values}")
