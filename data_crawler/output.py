#%% 1.Import crawler module and libraries
from data_crawler import crawler
import jsonlines
import os

#%% 2.Set parameters
max_depth = 10

file_paths = {
    'chiaselund': os.path.join('data_crawler', 'crawled_data'),
    'migrationsverket': os.path.join('data_crawler', 'crawled_data'),
    'skatterverket': os.path.join('data_crawler', 'crawled_data'),
    'studyinsweden': os.path.join('data_crawler', 'crawled_data')
}

urls = {
    'chiaselund': 'https://www.chiaselund.com/',
    'migrationsverket': 'https://www.migrationsverket.se/',
    'skatterverket': 'https://www.skatteverket.se/',
    'studyinsweden': 'https://studyinsweden.se/',
}

merged_data = os.path.join('data_crawler', 'crawled_data', 'merged_data.jsonl')

#%% 3.Crawling data and write to a final jsonl file
migration = Crawler()
output_file = os.path.join(file_paths['migrationsverket'], 'migrationsverket.jsonl')

# Extract all links from the website
migration.crawl_links(urls['migrationsverket'], depth=max_depth, lang = ['sv', 'en'])
#! Export to .txt file if needed
migration.write_visited_urls(os.path.join(file_paths['migrationsverket'], 'migrationsverket.txt'))
migration.extract_web_element(output_file, web_element = ['p', 'h1', 'h2'])



#%% 4.Merge all results into a single jsonl file
with jsonlines.open(merged_data, mode='w') as writer:
    for fp in file_paths.values():
        with jsonlines.open(fp, mode='r') as reader:
            for obj in reader:
                writer.write(obj)