
import glob
import mwxml
from wiki_dump_reader import Cleaner

# Max number of Wiki pages to index
INDEX_SIZE = 42 # 8192
XML_LOCATION = "../../wiki-data/*wiki-*-pages-articles-multistream.xml"


def get_file_name() -> str:
    file_name = None
    for name in glob.glob(XML_LOCATION):
        print(f"Found file: {name}")
        if (file_name == None):
            file_name = name

    if (file_name == None):
        print("No file found, exiting")
        exit()

    return file_name



cleaner = Cleaner()
def remove_wiki_shit(text) -> str:
    """Remove wiki formatting from the text"""

    text = cleaner.clean_text(text)
    text, links = cleaner.build_links(text)

    return text

def lemmatize_text(text) -> str:
    # TODO do the true lemmatization
    return text


def create_index() -> None:
    """Reads wiki dump and processes it"""
    
    file_name = get_file_name()
    print(f"Using {file_name}")
    dump = mwxml.Dump.from_file(open(file_name))
    print(dump.site_info.name, dump.site_info.dbname)
    

    # TODO create database


    pages_counter = 0
    for page in dump:
        page_id = page.id
        page_title = page.title
        print(f"{page_id}: {page_title}")
        for revision in page:
            if (revision.model != "wikitext"):
                continue

            text = revision.text[:256]
            text = remove_wiki_shit(text)
            text = lemmatize_text(text)
            # TODO process
            print(text, "\n")
    
        pages_counter += 1
        if pages_counter >= INDEX_SIZE:
            break

def update_index():
    pass

def drop_index():
    # TODO drop database
    pass
