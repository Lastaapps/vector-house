
import os 

import vekturkuv_domecek.indexer as ind


def pwd():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    os.chdir(dir_path)
    print(f"Running in {dir_path}")

def main():
    print("Hello, vector home is starting...")
    pwd()
    
    ind.create_index()

    print("Bye")

main()
