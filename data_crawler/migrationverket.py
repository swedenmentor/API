# %% 1️⃣ Loading packages
# load packages need for crawling data
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin

# %% 2️⃣ Extracting HTML from the website

def crawl(url, depth):
    if depth == 0:
        return

    # Send an HTTP GET request to the URL
    response = requests.get(url)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Parse the HTML content of the page
        soup = BeautifulSoup(response.text, 'html.parser')

        # Process the page as needed (e.g., extract data, save to a file, etc.)

        # Find all links on the page
        for link in soup.find_all('a'):
            href = link.get('href')

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
    start_url = 'https://www.migrationverket.se/'
    max_depth = 10  # Set the maximum depth to control how many pages to crawl

    crawl(start_url, max_depth)


