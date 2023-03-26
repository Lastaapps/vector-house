import sqlite3
from sqlite3 import Connection
from typing import Tuple

DB_PATH = "../../wiki-index.db"


class WikiDatabase:
    def __init__(self, path: str = DB_PATH):
        self.path = path
        self.con: Connection | None = None

    def connect_database(self) -> None:
        """
        Creates the database file if needed
        and connects to it
        """
        self.con = sqlite3.connect(self.path)

    def create_if_needed(self) -> None:
        if not self.has_schema():
            self.create_database()

    def drop_if_exists(self) -> None:
        if self.has_schema():
            self.drop_database()

    def has_schema(self) -> bool:
        """Creates the db if it's schema is empty"""

        cur = self.con.cursor()

        cur = cur.execute("""
SELECT name FROM sqlite_master WHERE type='table' AND name='term';
                """)
        
        return cur.fetchone() != None
        

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

    # TODO intersect
