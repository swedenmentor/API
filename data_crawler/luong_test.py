import time
import requests
from bs4 import BeautifulSoup
import datetime
import jsonlines
from urllib.parse import urlparse, urljoin

def crawl_website(url, output_file, visited_urls=None, depth=1, max_depth=3):
    """
    Crawls a website and extracts information from each page.

    :param url: The URL of the website to crawl.
    :type url: str
    :param output_file: The file path where the extracted information will be saved.
    :type output_file: str
    :param visited_urls: A set of visited URLs to avoid duplicate crawling.
    :type visited_urls: set, optional
    :param depth: The current depth of the crawling process.
    :type depth: int, optional
    :param max_depth: The maximum depth for crawling. Default value is 3.
    :type max_depth: int, optional
    :return: None
    :rtype: None
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


if __name__ == '__main__':
    url = 'https://www.migrationsverket.se/Privatpersoner/Arbeta-i-Sverige/Nyhetsarkiv/2023-11-01-Nu-borjar-det-hojda-forsorjningskravet-for-arbetstillstand-att-galla.html'
    output_file = 'data_crawler/example-data-chunked/data1.jsonl'
    crawl_website(url, output_file, max_depth=3)



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

