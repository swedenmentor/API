"""Crawler for universityadmission.se
"""

#%%
from crawler import Crawler, WriteMode
from pathlib import Path


ua_crawler = Crawler()
project_dir = Path(__file__).parent
urls_file = project_dir / "data/target_urls.txt"


urls = [
    "https://www.universityadmissions.se/en/key-dates-and-deadlines/spring-semester-dates/",
    "https://www.universityadmissions.se/en/fees-scholarships-residence-permit/",
]

base_url = "https://www.universityadmissions.se"

for url in urls:
    ua_crawler.crawl_links(url, 5, base_url, exclude_urls=['https://www.universityadmissions.se/intl/search'])
ua_crawler.write_urls(ua_crawler.target_urls, urls_file)

#%%
urls_file = project_dir / "data/target_urls.txt"
output_full_text_file = project_dir / "data/universityadmissions_full_text.jsonl"

ua_crawler.extract_web_element(
    input_file=urls_file,
    output_file=output_full_text_file,
    scope_selector="body > main",
    target_tags=["p", "h1", "h2", "h3", "div", "a", "ul", "ol", "table"],
    base_url=base_url,
    write_mode=WriteMode.OVERWRITE
)
#%%

output_chunk_file = project_dir / "data/universityadmissions_chunked_text.jsonl"

ua_crawler.write_chunk_text(
    input_file=output_full_text_file,
    output_file=output_chunk_file,
    chunk_size=1000,
    chunk_overlap=200,
    write_mode=WriteMode.OVERWRITE
)

# %%
