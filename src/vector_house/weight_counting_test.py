from vector_house.database import WikiDatabase
import vector_house.indexer as ind

DB_PATH_TEST = "../../indexer-test.db"
wiki_db = WikiDatabase(path = DB_PATH_TEST)
wiki_db.connect_database()
wiki_db.create_if_needed()

def test_weight_counting() -> None:
    wiki_db.drop_if_exists()
    wiki_db.create_database()

    title1 = "Clouds"
    text1 = "===Clouds=== Cloud albedo has substantial influence over atmospheric temperatures. Different types of clouds exhibit different reflectivity, theoretically ranging in albedo from a minimum of near 0 to a maximum approaching 0.8. On any given day, about half of Earth is covered by clouds, which reflect more sunlight than land and water. Clouds keep Earth cool by reflecting sunlight, but they can also serve as blankets to trap warmth. Albedo and climate in some areas are affected by artificial clouds, such as those created by the contrails of heavy commercial airliner traffic. A study following the burning of the Kuwaiti oil fields during Iraqi occupation showed that temperatures under the burning oil fires were as much as  colder than temperatures several miles away under clear skies."
    title2 = "Aerosol effects"
    text2 = "===Aerosol effects=== Aerosols (very fine particles/droplets in the atmosphere) have both direct and indirect effects on Earth's radiative balance. The direct (albedo) effect is generally to cool the planet; the indirect effect (the particles act as cloud condensation nuclei and thereby change cloud properties) is less certain. As per Spracklen et al. the effects are: Aerosol direct effect. Aerosols directly scatter and absorb radiation. The scattering of radiation causes atmospheric cooling, whereas absorption can cause atmospheric warming. Aerosol indirect effect. Aerosols modify the properties of clouds through a subset of the aerosol population called cloud condensation nuclei."
    title3 = "Test"
    text3 = "Clouds are cool."
    texts = {title1 : text1, title2 : text2, title3 : text3}

    terms = set() # ids of all terms
    absolute_freq = {}

    for page_title, text in texts.items():
        doc_id = wiki_db.insert_document(page_title, text)
        freq_dict = ind.lemmatize_text(text)
        ind.update_abs_freq(freq_dict, terms, doc_id, absolute_freq, wiki_db)

    relative_freq = ind.count_relative_freq(absolute_freq, terms)
    ind.weights_to_db(wiki_db, relative_freq, terms, len(texts))

    print("RELATIVE FREQUENCIES: ")
    for term_id, dict in relative_freq.items():
        print(wiki_db.get_term_by_id(term_id), "( id:", term_id, ") -> ", dict)

    doc_id1 = wiki_db.get_doc_id(title1)
    doc_id2 = wiki_db.get_doc_id(title2)
    doc_id3 = wiki_db.get_doc_id(title3)

    cloud_id = wiki_db.get_term_id('cloud') # cloud is in all texts
    assert(wiki_db.get_value_by_ids(cloud_id, doc_id1) == 0)
    assert(wiki_db.get_value_by_ids(cloud_id, doc_id2) == 0)
    assert(wiki_db.get_value_by_ids(cloud_id, doc_id3) == 0)

    substantial_id = wiki_db.get_term_id('substantial') # substantial only in text1
    assert(wiki_db.get_value_by_ids(substantial_id, doc_id1) == 1.58)
    assert(wiki_db.get_value_by_ids(substantial_id, doc_id2) == 0)
    assert(wiki_db.get_value_by_ids(substantial_id, doc_id3) == 0)

    assert(wiki_db.get_value_by_ids(200, doc_id1) == 0) # term id does not exist
    assert(wiki_db.get_value_by_ids(200, doc_id2) == 0)
    assert(wiki_db.get_value_by_ids(200, doc_id3) == 0)

    assert(wiki_db.get_value_by_ids(cloud_id, 50) == 0) # document id does not exist

    earth_id = wiki_db.get_term_id('earth') # earth 2x in text1, 1x in text2, 0x in text3
    assert(wiki_db.get_value_by_ids(earth_id, doc_id1) == 0.58)
    assert(wiki_db.get_value_by_ids(earth_id, doc_id2) == 0.29)
    assert(wiki_db.get_value_by_ids(earth_id, doc_id3) == 0)

    wiki_db.drop_database()
    wiki_db.commit()
