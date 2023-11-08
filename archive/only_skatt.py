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


#! Example in skatteverket
skatteverket = Crawler()
output_file = os.path.join(file_paths['skatterverket'], 'skatteverket.jsonl')

# Extract all links from the website
skatteverket.crawl_links(url = urls['skatterverket'], depth=max_depth, lang = ['sv', 'en'])
# Export to .txt file if needed
skatteverket.write_visited_urls(os.path.join(file_paths['skatterverket'], 'skatteverket.txt'))
skatteverket.extract_web_element(output_file, tags = ['p', 'h1', 'h2', 'h3', 'ul'], special_tags = 'ul', class_name = 'normal')

