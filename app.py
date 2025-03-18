import utils  # This loads vars, do not remove

import scrapper
import preprocessing


def run():
    scrapper.run_scrapper()
    preprocessing.run_cleaner()


if __name__ == "__main__":
    run()
