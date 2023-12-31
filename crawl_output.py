#%% 1.Import crawler module and libraries
from data_crawler.crawler import Crawler
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
#! Example in migrationsverket
migration = Crawler()
output_file = os.path.join(file_paths['migrationsverket'], 'migrationsverket.jsonl')
# input_file = os.path.join(file_paths['migrationsverket'], 'migrationsverket.txt')

# Extract all links from the website
migration.crawl_links(url = urls['migrationsverket'], depth=max_depth, lang = ['sv', 'en'])
# Export to .txt file if needed
migration.write_visited_urls(os.path.join(file_paths['migrationsverket'], 'migrationsverket.txt'))
migration.extract_web_element(input_file = input_file, output_file = output_file, tags = ['p', 'h1', 'h2', 'h3', 'ul'], special_tags = 'ul', class_name = 'normal')


#! Example in skatteverket
skatteverket = Crawler()
output_file = os.path.join(file_paths['skatterverket'], 'skatteverket.jsonl')

# Extract all links from the website
skatteverket.crawl_links(url = urls['skatterverket'], depth=max_depth, lang = ['sv', 'en'])
# Export to .txt file if needed
skatteverket.write_visited_urls(os.path.join(file_paths['skatterverket'], 'skatteverket.txt'))
skatteverket.extract_web_element(output_file, tags = ['p', 'h1', 'h2', 'h3', 'ul'], special_tags = 'ul', class_name = 'normal')



#! Example in studyinsweden

# NOTE: page should be written as {} in the url like page={} not page=1
url = "https://cms.studyinsweden.se/wp-json/wp/v2/posts?_embed=true&page={}&per_page=12"
output_file = os.path.join(file_paths['studyinsweden'], 'studyinsweden.jsonl')

studyinsweden = Crawler()
studyinsweden.extract_json(base_url = url, output_file = output_file)
studyinsweden.write_visited_urls(os.path.join(file_paths['studyinsweden'], 'studyinsweden.txt'))

#%% 4.Merge all results into a single jsonl file
with jsonlines.open(merged_data, mode='w') as writer:
    for fp in file_paths.values():
        with jsonlines.open(fp, mode='r') as reader:
            for obj in reader:
                writer.write(obj)


if __name__ == "__main__":
    main()