import utils  # This loads vars, do not remove

import scrapper
import preprocessing
import model


def run_data_pipeline():
    scrapper.run_scrapper()
    preprocessing.run_cleaner()


if __name__ == "__main__":
    # run_data_pipeline()
    model.run_rag_claude()
