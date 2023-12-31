# Vektůrkův domeček
Vector house - this is where the fun happens.

To see more, please read the project [report](report.pdf).

Vector house is a vector based search engine used to search en variant of Wikipedia. 
It was developed in 2023 by Naďa Fučelová and Petr Laštovička during
the BI-VWM (Web and multimedia db searching) course at FIT CTU.

It the site is still up, you can try it out at
[https://lastope2.sh.cvut.cz/vector_house/].

## Setup
### Download
Download the latest dump from wiki
https://dumps.wikimedia.org/enwiki/
and extract it in the `wiki-data` folder.

Create a virtual env `python -m venv .venv`, source it `source .venv/bin/activate` and install requirements
`pip install -r requirements.txt`.

## Usage
### Web
To open the page go to use `streamlit run vector_house/page.py`

### CLI
To view help, run `python -m vector_house --help` or `./run --help`.

All the commands below use the default database `wiki-index.db`
unless you specify another one by using the `--db path` option.

#### Searching
To search the database run `./run search query`.

To search for similar documents use
`./run sim doc_id` where the `doc_id` is returned by 
the `search` or `sim` function.

To view a found document, run `./run show doc_id`.


#### Index
To create an index run this cli command `./run index`.

If you want to limit the number of words processed in each document,
add also the flag `--limit` with the number of words.
The default limit is 42069 words.

If you want for each term store only the top n documents
with the highest score use `--top-docs` option.
Otherwise the count is not limited.

Index size (doc count) is set to 8000 by default. You can change it with
`--size` flag in combination with the `index` frag.

Run `./run info` to show db internal info.

Run `./run db-index {create|drop}` to create/drop database column indexes.

#### Benchmark
Run `./run benchmark` to start auto benchmarks.
Run `./run benchmark --create-index` once before to create more different indexes.

### Tests
To run tests, run the `pytest vector_house`.

## License
Vector house is licensed under the `GNU GPL v3.0` license
