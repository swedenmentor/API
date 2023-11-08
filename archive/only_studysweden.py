#%% 1.Import crawler module and libraries
from data_crawler.crawler import Crawler
import jsonlines
import os

#%% 2.Set parameters
max_depth = 10

file_paths = {
    'chiaselund': os.path.join('../data_crawler', 'crawled_data'),
    'migrationsverket': os.path.join('../data_crawler', 'crawled_data'),
    'skatterverket': os.path.join('../data_crawler', 'crawled_data'),
    'studyinsweden': os.path.join('../data_crawler', 'crawled_data')
}

urls = {
    'chiaselund': 'https://www.chiaselund.com/',
    'migrationsverket': 'https://www.migrationsverket.se/',
    'skatterverket': 'https://www.skatteverket.se/',
    'studyinsweden': 'https://studyinsweden.se/',
}

merged_data = os.path.join('../data_crawler', 'crawled_data', 'merged_data.jsonl')

#%% 3.Crawling data and write to a final jsonl file
#! Example in studyinsweden

# NOTE: page should be written as {} in the url like page={} not page=1
url = "https://cms.studyinsweden.se/wp-json/wp/v2/posts?_embed=true&page={}&per_page=12"
output_file = os.path.join(file_paths['studyinsweden'], 'studyinsweden.jsonl')

studyinsweden = Crawler()
studyinsweden.extract_json(base_url = url, output_file = output_file)
studyinsweden.write_visited_urls(os.path.join(file_paths['studyinsweden'], 'studyinsweden.txt'))
