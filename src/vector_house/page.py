#from vector_house.database import WikiDatabase
from database import WikiDatabase
import indexer as ind
import numpy as np
import search_engine as se
import streamlit as st
import time

def get_pages(keywords: list) -> list:
    """Gets ids of 10 pages to show"""

    vectors = se.find_vectors(st.session_state.wiki_db, keywords)

    if "sim_to" not in st.session_state or st.session_state.sim_to.size == 0:
        pages = se.search(vectors)
    else:
        pages = se.search(vectors, st.session_state.sim_to)

    return pages

def set_new_state(page_id: int):
    """Sets new state to show similar pages to given one"""

    wiki_db = st.session_state.wiki_db
    dict_term_val = wiki_db.get_terms_for_doc(page_id)
    st.session_state.keywords = list(dict_term_val.keys())
    st.session_state.sim_to = np.array(list(dict_term_val.values()))
    st.session_state.name = wiki_db.get_doc_by_id(page_id)[0]
    st.experimental_rerun()


def print_pages(pages: list) -> None:
    """ Prints the title and the text of pages, shows buttons"""

    st.write("---")
    wiki_db = st.session_state.wiki_db
    for page_id in pages:
        title, text = wiki_db.get_doc_by_id(page_id)
        st.write(f"<h4 style='text-align: left'>{title}</h4>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: justify'>{text[:5000]}</p>", unsafe_allow_html=True)

        if st.button("Show whole text", key = title):
            st.markdown(f"<p style='text-align: justify'>{text}</p>", unsafe_allow_html=True)
            st.session_state.reload = False

        if st.button("Show similar pages", key=page_id):
            st.session_state.reload = True
            set_new_state(page_id)


def go_to_top():
    """Goes to the top of the page"""

    js = '''
<script>
    var body = window.parent.document.querySelector(".main");
    console.log(body);
    body.scrollTop = 0;
</script>
'''
    st.components.v1.html(js)


def run_page():

    st.set_page_config(page_title="Vektůrkův domeček", page_icon=":house:", layout="wide")
    st.subheader("Wikipedia searcher 🔍")

    if st.session_state.keywords == []:
        st.session_state.reload = True
        keywords = st.text_input("I would like to see wikipedia pages about:")
        st.session_state.name = keywords
        st.session_state.keywords = list(ind.lemmatize_text(keywords).keys())

    st.write("Showing pages about:", st.session_state.name)

    if st.session_state.reload:
        start_time = time.time()
        st.session_state.pages = get_pages(st.session_state.keywords)
        end_time = time.time()
        st.session_state.time = round(end_time - start_time, 2)

    if "time" in st.session_state:
        st.write("Time taken (in seconds):", st.session_state.time)

    print_pages(st.session_state.pages)

    if st.session_state.reload:
        st.session_state.reload = False
        go_to_top()


if "wiki_db" not in st.session_state:
    st.session_state.keywords = []
    st.session_state.wiki_db = WikiDatabase()
    st.session_state.wiki_db.connect_database()
    st.session_state.reload = True

run_page()
