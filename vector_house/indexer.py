from vector_house.database import WikiDatabase
import glob
import nltk
import math
import mwxml
import string
from collections import defaultdict
import itertools
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from wiki_dump_reader import Cleaner
from typing import List, Tuple

nltk.download("wordnet")
nltk.download("stopwords")

# Max number of Wiki pages to index
INDEX_SIZE = 1000  # 8192
WORD_LIMIT = 42069
XML_LOCATION = "wiki-data/*wiki-*-pages-articles-multistream.xml"


def get_file_name() -> str:
    file_name = None
    for name in glob.glob(XML_LOCATION):
        print(f"Found file: {name}")
        if file_name == None:
            file_name = name

    if file_name == None:
        print("No file found, exiting")
        exit()

    return file_name


cleaner = Cleaner()


def remove_wiki_shit(text) -> str:
    """Remove wiki formatting from the text"""

    text = cleaner.clean_text(text)
    text, links = cleaner.build_links(text)

    return text


def lemmatize_text(text: str, limit: int = 0) -> dict:
    """Lemmatize the text, remove stop words and count frequencies."""

    if limit == 0:
        limit = WORD_LIMIT

    text_no_punct = text.translate(
        str.maketrans("", "", string.punctuation)
    )  # remove punctuation
    tokens = nltk.word_tokenize(text_no_punct)
    lemmatizer = WordNetLemmatizer()

    stop_words = set(stopwords.words("english"))
    extra_stop_words = {"like", "&ndash;"}
    stop_words.update(extra_stop_words)

    freq_dict = defaultdict(int)
    for token in itertools.islice(tokens, limit):
        word = token.lower()
        if word not in stop_words:
            word = lemmatizer.lemmatize(word)
            freq_dict[word] += 1

    return freq_dict


def update_abs_freq(
    freq_dict: dict, terms: set, doc_id: int, abs_dict: dict, wiki_db: WikiDatabase
) -> None:
    """Updates dictionary with absolute frequencies and adds terms to the database."""

    for term, value in freq_dict.items():
        term_id = 0
        if wiki_db.has_term(term):
            term_id = wiki_db.get_term_id(term)
        else:
            term_id = wiki_db.insert_term(term)

        terms.add(term_id)
        abs_dict.setdefault(term_id, {})[doc_id] = value


def count_relative_freq(absolute_freq: dict, terms: set) -> dict:
    """Counts relative frequencies of terms in all documents. Zero frequency is left out."""

    relative_freq = {}
    for term_id in terms:
        if term_id not in absolute_freq:
            continue

        cur_dict = absolute_freq[term_id]
        max_freq = max(cur_dict.values())
        for doc_id, freq in cur_dict.items():
            relative_freq.setdefault(term_id, {})[doc_id] = round(freq / max_freq, 2)

    return relative_freq


def count_weight(num_of_docs: int, tf_ij: int, df_i: int) -> float:
    """Count weight of term in given document."""

    idf_i = math.log(num_of_docs / df_i, 2)

    return round(tf_ij * idf_i, 2)


def weights_to_db(
    wiki_db: WikiDatabase,
    relative_freq: dict,
    terms: set,
    num_of_docs: int,
    top_docs: int,
) -> None:
    for term_id in terms:
        if term_id not in relative_freq:
            continue

        cur_dict = relative_freq[term_id]
        weights: List[Tuple[int, float]] = []

        for doc_id, value in cur_dict.items():
            tf_ij = value  # normalized term frequency
            df_i = len(cur_dict)  # num of docs containing term
            weight = count_weight(num_of_docs, tf_ij, df_i)
            if top_docs == 0:
                wiki_db.insert_value(term_id, doc_id, weight)
            else:
                weights.append((doc_id, weight))

        if top_docs == 0:
            continue

        weights.sort(reverse=True, key=lambda x: x[1])

        for doc_id, weight in itertools.islice(weights, top_docs):
            wiki_db.insert_value(term_id, doc_id, weight)


def recreate_index(
    index_size: int, limit: int, top_docs: int, wiki_db: WikiDatabase = WikiDatabase()
) -> None:
    """Reads wiki dump and processes it"""

    if limit != 0:
        print(f"Using token limit: {limit}")

    if top_docs != 0:
        print(f"Using top docs: {top_docs}")

    if index_size == 0:
        index_size = INDEX_SIZE

    file_name = get_file_name()
    print(f"Using {file_name}")
    dump = mwxml.Dump.from_file(open(file_name, encoding="utf8"))
    print(dump.site_info.name, dump.site_info.dbname)

    wiki_db.drop_if_exists()
    wiki_db.create_if_needed()

    terms = set()  # ids of all terms
    absolute_freq = {}
    pages_counter = 0

    for page in dump:
        page_id = page.id
        page_title = page.title
        revision = next(x for x in page)
        if revision.model != "wikitext":
            continue

        text = revision.text
        text = remove_wiki_shit(text)
        if text.startswith("REDIRECT"):
            continue

        print(f"{pages_counter:5} - {page_id:5}: {page_title}")
        doc_id = wiki_db.insert_document(page_title, text)
        freq_dict = lemmatize_text(text, limit)
        update_abs_freq(freq_dict, terms, doc_id, absolute_freq, wiki_db)

        pages_counter += 1
        if pages_counter >= index_size:
            break

    relative_freq = count_relative_freq(absolute_freq, terms)
    weights_to_db(wiki_db, relative_freq, terms, pages_counter, top_docs)
    wiki_db.commit()

    wiki_db.create_index()
    wiki_db.print_stats()