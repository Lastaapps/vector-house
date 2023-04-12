# Vektůrkův domeček

## Setup
### Download
Download the latest dump from wiki
https://dumps.wikimedia.org/enwiki/
and extract it in the `wiki-data` folder.

### Usage
To open the page go to use `streamlit run src/vector_house/page.py`

### Index
To create an index run the app from cli with the `--index` flag.

If you want to limit the number of words processed in each document,
add also the flag `--limit` with the number of words.
The default limit is 42069 words.

Index size (doc count) is set to 8000 by default. You can change it with
`--size` flag in combination with the `index` frag.
