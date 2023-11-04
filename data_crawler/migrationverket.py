# %% 1️⃣ Loading packages
# load packages need for crawling data
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import json
from datetime import datetime

# Function to check if the url has been pre-crawled
def check(url):
    global URL_list
    return (url in URL_list.keys())

# Function to write data to a JSONL file
def write_to_jsonl(data, filename):
    with open(filename, 'a', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False)
        file.write('\n')

# %% 2️⃣ Extracting HTML from the website
def crawl(url, depth):
    # Check if the URL was already crawled and depth reaches 0
    if (depth == 0) or (check(url)): return
    global URL_list
    URL_list[url]=True
    data ={}

    # Send an HTTP GET request to the URL
    response = requests.get(url)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Parse the HTML content of the page
        soup = BeautifulSoup(response.text, 'html.parser')

        # Process the page as needed (e.g., extract data, save to a file, etc.)
        ''' For migrationsverket, contents are usually in p['normal'],h2['subheading'],ul['normal']
            The title is stored in h1['heading']'''
        
        '''Here is some draft codes:
        # Extract content from p.normal and h2.subheading classes, store it in p_normal and h2_substring lists
        # Example link: https://www.migrationsverket.se/Privatpersoner/Arbeta-i-Sverige/Nyhetsarkiv/2023-11-01-Nu-borjar-det-hojda-forsorjningskravet-for-arbetstillstand-att-galla.html'''
        if url=='https://www.migrationsverket.se/Privatpersoner/Arbeta-i-Sverige/Nyhetsarkiv/2023-11-01-Nu-borjar-det-hojda-forsorjningskravet-for-arbetstillstand-att-galla.html':
            #Extract date of update otherwise date = crawling date
            date_tag = soup.find('p', class_='ahjalpfunktioner')
            if date_tag: date = date_tag.get_text()
            else: date = datetime.now().strftime("%Y-%m-%d")

            # Extract data from p normal class or h2_subheading class
            p_normal = [p.get_text() for p in soup.find_all('p', class_='normal')]
            h2_subheading = [h2.get_text() for h2 in soup.find_all('h2', class_='subheading')]
            for count, content in enumerate(p_normal):
                data = {
                    "source": url,
                    "chunk-id": str(count),
                    "title": soup.title.string,
                    "chunk": content,
                    "updated": date
                }
                write_to_jsonl(data, jsonl_file)
        # Find all links on the page
        for link in soup.find_all('a'):
            href = link.get('href')
            if href == None or len(href)==0: continue
            if href[0]=='#': continue
            # Join relative URLs with the base URL
            absolute_url = urljoin(url, href)

            # Parse the absolute URL to extract the domain
            domain = urlparse(absolute_url).netloc
            original_domain = urlparse(url).netloc

            # Check if the link is within the same domain
            if domain == original_domain:
                # Recursively crawl the linked page
                crawl(absolute_url, depth - 1)

if __name__ == '__main__':
    start_url = 'https://www.migrationsverket.se/Privatpersoner/Arbeta-i-Sverige/Nyhetsarkiv/2023-11-01-Nu-borjar-det-hojda-forsorjningskravet-for-arbetstillstand-att-galla.html'
    max_depth = 10  # Set the maximum depth to control how many pages to crawl
    URL_list={}
    jsonl_file = 'migrationsverket.jsonl'
    
    # Clear existing content in the JSONL file
    with open(jsonl_file, 'w') as file:
        file.write('')

    crawl(start_url, max_depth)



# %%
