import glob
import nltk
import mwxml
import string
from collections import defaultdict
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from wiki_dump_reader import Cleaner

nltk.download("wordnet")
nltk.download("stopwords")

# Max number of Wiki pages to index
INDEX_SIZE = 8192
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


def create_index() -> None:
    """Reads wiki dump and processes it"""

    file_name = get_file_name()
    print(f"Using {file_name}")
    dump = mwxml.Dump.from_file(open(file_name, encoding="utf8"))
    print(dump.site_info.name, dump.site_info.dbname)

    # TODO create database

    pages_counter = 0
    for page in dump:
        page_id = page.id
        page_title = page.title
        print(f"{page_id}: {page_title}")
        revision = next(x for x in page)
        if revision.model != "wikitext":
            continue

        text = revision.text
        text = remove_wiki_shit(text)
        if text.startswith("REDIRECT"):
            continue

        freq_dict = lemmatize_text(text)
        print(text[:256])
        print(freq_dict, end = "\n")
        print()

        pages_counter += 1
        if pages_counter >= INDEX_SIZE:
            break


def drop_index() -> None:
    # TODO drop database
    pass
