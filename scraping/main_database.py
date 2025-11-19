"---This will scrape all the links and turn it to a database---"
import glob
from Scraping.scrape_website import scrape
from Scraping.merge_json_files import merge
from Scraping.translate_and_ind_id import translate
from Database.json_to_SQL import json_to_sql


# Only filenames
filenames = [fp.split("/")[-1] for fp in glob.glob("links/*")]
for filesname in filenames:
    print("")
    scrape("filename")
merge()
translate()
json_to_sql()