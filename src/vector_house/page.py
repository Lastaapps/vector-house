from database import WikiDatabase
import indexer as ind
import search_engine as se
import streamlit as st

# page with emojis: https://www.webfx.com/tools/emoji-cheat-sheet/

wiki_db = ind.recreate_index()

def get_pages(keywords: str) -> list:
    lem_keywords = list(ind.lemmatize_text(keywords).keys())
    vectors = se.find_vectors(wiki_db, lem_keywords)
    pages = se.search(vectors)
    return pages

def run_page(wiki_db: WikiDatabase):
    st.set_page_config(page_title="Vekturkův domeček", page_icon=":house:", layout="wide")
    st.subheader("Wikipedia searcher 🔍")
    st.write("")

    keywords = st.text_input("I would like to see wikipedia pages about:")
    st.write("Showing pages about", keywords)

    pages = get_pages(keywords)

    st.write("---")
    for page_id in pages:
        title, text = wiki_db.get_doc_by_id(page_id)
        st.write(f"<h4 style='text-align: left'>{title}</h4>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: justify'>{text[:5000]}</p>", unsafe_allow_html=True)


run_page(wiki_db)