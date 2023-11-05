#%% 1️⃣ Loading packages
import time
import requests
from bs4 import BeautifulSoup
import datetime
import jsonlines
from urllib.parse import urlparse, urljoin

#%% 2️⃣ Define function crawl data from the website
def crawl_website(url, output_file, visited_urls=None, depth=1, max_depth=5):
    """
    Crawls a specified website for all of its linked pages up to a maximum depth and stores the extracted
    information into a file. It uses a set of visited URLs to avoid repeating the crawling process for the same page.
    It crawls the website using a depth-first search mechanism.

    Parameters:
        url (str): The URL of the website to be crawled.
        output_file (str): The path of the output file where the extracted information will be saved.
        visited_urls (set, optional): A set of URLs that the crawler has already visited. Defaults to None.
        depth (int, optional): The current depth of the crawl. Defaults to 1.
        max_depth (int, optional): The maximum depth to crawl the website. Defaults to 5.

    Returns:
        None

    Raises:
        RequestException: If there was an ambiguous exception while handling the request.
        HTTPError: If an HTTP error occurred.
        ConnectionError: If a network problem occurred.

    Note:
        - Crawling is done using the requests and BeautifulSoup libraries.
        - For each visited page, it extracts the title, combined text content of all paragraphs
          ('p', 'h1', 'h2' tags), the page url, and the date of the page (current date used as fallback).
        - Extracted information is stored as a single entry of a jsonlines file at `output_file`.
        - It enforces a 1-second delay between requests to avoid overloading the server.
    """
    try:
        if visited_urls is None:
            visited_urls = set()
        if depth > max_depth:
            return
        if url in visited_urls:
            return
        response = requests.get(url)
        if not response.status_code == 200:
            print(f'Non success status for url {url}')
            return
        visited_urls.add(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        date_tag = soup.find('p', class_ = 'ahjalpfunktioner').find('time')
        if date_tag:
            date = date_tag.get_text()
        else:
            date = datetime.now().strftime("%Y-%m-%d")
        title = soup.title.text.strip()
        paragraphs = soup.find_all(['p', 'h1', 'h2'])
        # Combine all paragraphs, h1 and h2 contents into a single chunk
        chunks = " ".join([p.get_text().strip() for p in paragraphs])

        entry = {
            "source": url,
            "title": title,
            "chunk": chunks,
            # "updated": datetime.date.today().strftime('%Y-%m-%d')
            "updated": date
        }
        with jsonlines.open(output_file, mode='a') as writer:
            writer.write(entry)
        links = soup.find_all('a')
        for link in links:
            href = link.get('href')
            if href and href.startswith('http'):
                new_url = href
            else:
                new_url = urljoin(url, href)
            crawl_website(new_url, output_file, visited_urls=visited_urls, depth=depth+1, max_depth=max_depth)
            # Making sure the requests to the server are not going too fast
            time.sleep(1)
    except requests.exceptions.RequestException as err:
        print (f"RequestException: {err}")
    except requests.exceptions.HTTPError as errh:
        print (f"HTTPError: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print (f"ConnectionError: {errc}")
    except Exception as e:
        print(f"An error occurred while processing {url}: {str(e)}")


#%% 3️⃣ Crawl data and save to jsonl file

if __name__ == '__main__':
    url = 'https://www.migrationsverket.se/Privatpersoner/Arbeta-i-Sverige/Nyhetsarkiv/2023-11-01-Nu-borjar-det-hojda-forsorjningskravet-for-arbetstillstand-att-galla.html'
    output_file = 'data_crawler/example-data-chunked/migrationverket.jsonl'
    crawl_website(url, output_file, max_depth=5)




#%% 4️⃣ Archive code
# Break each paragraph into a chunk

# import time
# import requests
# from bs4 import BeautifulSoup
# import datetime
# import jsonlines
# from urllib.parse import urlparse, urljoin
#
# def crawl_website(url, output_file, visited_urls=None, depth=1, max_depth=3):
#     try:
#         if visited_urls is None:
#             visited_urls = set()
#
#         if depth > max_depth:
#             return
#         if url in visited_urls:
#             return
#
#         response = requests.get(url)
#
#         if not response.status_code == 200:
#             print(f'Non success status for url {url}')
#             return
#
#         visited_urls.add(url)
#         soup = BeautifulSoup(response.text, 'html.parser')
#
#         title = soup.title.text.strip()
#         paragraphs = soup.find_all(['p', 'h1', 'h2'])
#         chunks = [p.get_text().strip() for p in paragraphs]
#
#         entries = []
#         for chunk_id, chunk in enumerate(chunks):
#             entry = {
#                 "source": url,
#                 "chunk-id": str(chunk_id),
#                 "title": title,
#                 "chunk": chunk,
#                 "updated": datetime.date.today().strftime('%Y-%m-%d')
#             }
#             entries.append(entry)
#
#         with jsonlines.open(output_file, mode='a') as writer:
#             for entry in entries:
#                 writer.write(entry)
#
#         links = soup.find_all('a')
#
#         for link in links:
#             href = link.get('href')
#
#             if href and href.startswith('http'):
#                 new_url = href
#             else:
#                 new_url = urljoin(url, href)
#
#             crawl_website(new_url, output_file, visited_urls=visited_urls, depth=depth+1, max_depth=max_depth)
#
#             # Making sure the requests to the server are not going too fast
#             time.sleep(1)
#
#     except requests.exceptions.RequestException as err:
#         print (f"RequestException: {err}")
#     except requests.exceptions.HTTPError as errh:
#         print (f"HTTPError: {errh}")
#     except requests.exceptions.ConnectionError as errc:
#         print (f"ConnectionError: {errc}")
#     except Exception as e:
#         print(f"An error occurred while processing {url}: {str(e)}")
#
#
# output_file = 'data_crawler/example-data-chunked/data1.jsonl'
# crawl_website('https://www.migrationsverket.se/Privatpersoner/Arbeta-i-Sverige/Nyhetsarkiv/2023-11-01-Nu-borjar-det-hojda-forsorjningskravet-for-arbetstillstand-att-galla.html', output_file, max_depth=3)

