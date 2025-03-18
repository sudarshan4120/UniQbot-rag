import utils  # This loads vars, do not remove

import scrapper
import Chunking


def run():
    scrapper.run_scrapper()
    Chunking.run_cleaner()


if __name__ == "__main__":
    run()
