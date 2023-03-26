import database as db
import glob
import nltk
import math
import mwxml
import string
from collections import defaultdict
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from wiki_dump_reader import Cleaner

nltk.download("wordnet")
nltk.download("stopwords")

# Max number of Wiki pages to index
INDEX_SIZE = 100 # 8192
XML_LOCATION = "../../wiki-data/*wiki-*-pages-articles-multistream.xml"


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

def lemmatize_text(text) -> dict:
    """Lemmatize the text, remove stop words and count frequencies."""

    text_no_punct = text.translate(str.maketrans("", "", string.punctuation)) # remove punctuation
    tokens = nltk.word_tokenize(text_no_punct)
    lemmatizer = WordNetLemmatizer()

    stop_words = set(stopwords.words('english'))
    extra_stop_words = {'like', '&ndash;'}
    stop_words.update(extra_stop_words)

    freq_dict = defaultdict(int)
    for token in tokens:
        word = token.lower()
        if word not in stop_words:
            word = lemmatizer.lemmatize(word)
            freq_dict[word] += 1

    return freq_dict

def update_abs_freq(freq_dict: dict, terms: set, doc_id: int, abs_dict: dict) -> None:
    for term, value in freq_dict.items():
        terms.add(term)
        abs_dict.setdefault(term, {})[doc_id] = value

def count_relative_freq(absolute_freq: dict, terms: set) -> dict:
    """Counts relative frequencies of terms in all documents. Zero frequency is left out."""

    relative_freq = {}
    for term in terms:
        cur_dict = absolute_freq[term]
        max_freq = max(cur_dict.values())
        for doc_id, freq in cur_dict.items():
            relative_freq.setdefault(term, {})[doc_id] = round(freq/max_freq, 2)
    
    return relative_freq

def count_weight(relative_freq: dict, term: string, doc_id: int, num_of_docs: int) -> float:
    """Count weight of term in given document."""

    if term not in relative_freq: # maybe check in terms
        return 0
    if doc_id not in relative_freq[term]:
        return 0
    
    tf_ij = relative_freq[term][doc_id] # normalized term frequency
    df_i = len(relative_freq[term]) # num of docs containig term
    idf_i = math.log(num_of_docs/df_i, 2)

    return round(tf_ij * idf_i, 2)

def create_database() -> db.WikiDatabase:
    wiki_db = db.WikiDatabase()
    wiki_db.connect_database()
    wiki_db.create_if_needed()
    return wiki_db

def add_lemmas_to_db(wiki_db: db.WikiDatabase, freq_dict: dict, doc_id: int) -> None:
    word_id = 0
    for word, freq in freq_dict.items():
        if wiki_db.has_term(word):
            word_id = wiki_db.get_term_id(word)
        else:
            word_id = wiki_db.insert_term(word)
        
        wiki_db.insert_value(word_id, doc_id, freq)
    
    wiki_db.commit()

def create_index() -> None:
    """Reads wiki dump and processes it"""

    file_name = get_file_name()
    print(f"Using {file_name}")
    dump = mwxml.Dump.from_file(open(file_name, encoding="utf8"))
    print(dump.site_info.name, dump.site_info.dbname)

    # TODO create database

    terms = set()
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
        
        print(f"{page_id}: {page_title}")
        update_abs_freq(lemmatize_text(text), terms, page_id, absolute_freq) # TODO change page_id to actual doc_id in db

        pages_counter += 1
        if pages_counter >= INDEX_SIZE:
            break
    
    relative_freq = count_relative_freq(absolute_freq, terms)

def drop_index() -> None:
    # TODO drop database
    pass
