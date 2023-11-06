#%% 1️⃣ Import crawler module and libraries
from data_crawler import crawler
import jsonlines
import os

#%% 2️⃣ Set parameters
max_depth = 5

file_paths = {
    'chiaselund': os.path.join('data_crawler', 'crawled_data', 'chiaselund.jsonl'),
    'migrationverket': os.path.join('data_crawler', 'crawled_data', 'migrationverket.jsonl'),
    'skatterverket': os.path.join('data_crawler', 'crawled_data', 'skatterverket.jsonl'),
    'studyinsweden': os.path.join('data_crawler', 'crawled_data', 'studyinsweden.jsonl'),
}

urls = {
    'chiaselund': 'https://www.chiaselund.com/',
    'migrationverket': 'https://www.migrationsverket.se/',
    'skatterverket': 'https://www.skatteverket.se/',
    'studyinsweden': 'https://studyinsweden.se/',
}

merged_data = os.path.join('data_crawler', 'crawled_data', 'merged_data.jsonl')

#%% 3️⃣ Crawling data and write to a final jsonl file
for name, url in urls.items():
    output_file = file_paths[name]
    crawler.Crawler().crawl_website(url, output_file=output_file, depth=max_depth)

#%% 4️⃣ Merge all results into a single jsonl file
with jsonlines.open(merged_data, mode='w') as writer:
    for fp in file_paths.values():
        with jsonlines.open(fp, mode='r') as reader:
            for obj in reader:
                writer.write(obj)