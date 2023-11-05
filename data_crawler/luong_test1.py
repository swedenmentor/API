#%% 1️⃣ Loading packages
import time                                         # for time-related tasks
import requests                                     # for making HTTP requests
from bs4 import BeautifulSoup                       # for web scraping, parsing HTML
import datetime                                     # for dealing with dates and times
import jsonlines                                    # for handling JSONL format
from urllib.parse import urlparse, urljoin          # for URL parsing and joining
from googletrans import Translator                  # for text translation using Google Translate API
from langdetect import detect, LangDetectException  # for language detection

#%% 2️⃣ Define function crawl data from the website

class Crawler:
    """
    A Crawler class that crawls through websites and performs translation on the collected data.

    Attributes:
    visited_urls (set): A set to hold the URLs already visited by the crawler.
    translator (Translator): A Translator object to perform translations.
    """
    def __init__(self):
        self.visited_urls = set()
        self.translator = Translator()
        self.data_buffer = []

    def write_to_file(self, output_file):
        if self.data_buffer:
            with jsonlines.open(output_file, mode = 'w' if not self.data_buffer else 'a') as writer:
                for entry in self.data_buffer:
                    if entry is not None:
                        writer.write(entry)
            self.data_buffer.clear()

    def translate_text(self, text):
        detected = self.translator.detect(text)
        if detected.lang != 'en':
            return self.translator.translate(text, src=detected.lang, dest='en').text
        return text

    def crawl_website(self, url, output_file, depth=1, max_depth=5):
        """
        Crawls a website starting from a specified URL and extracts information,
        creating an entry for each visited webpage and writing the information to a file.
        The crawl depth is restricted to a configurable maximum depth.

        If exceptions occur during the requests, they get handled and
        an error message is printed to the console.

        :param url: The starting URL to crawl from.
        :type url: str
        :param output_file: The path of the file to which extracted information
                            will be written.
        :type output_file: str
        :param depth: The current depth of the crawling (default is 1). This is
                      used to keep track of the recursive depth of the crawl.
        :type depth: int
        :param max_depth: The maximum depth the crawler will go to from the
                          starting page (default is 5).
        :type max_depth: int
        :return: None
        :rtype: None

        :raises:
            requests.exceptions.RequestException: When a request exception occurs.
            requests.exceptions.HTTPError: When an HTTP error occurs.
            requests.exceptions.ConnectionError: When a connection error occurs.
            Exception: For any other unhandled exceptions.
        """
        if depth > max_depth or url in self.visited_urls:
            return
        try:
            response = requests.get(url)
            if not response.status_code == 200:
                print(f'Non success status for url {url}')
                return
            self.visited_urls.add(url)

            soup = BeautifulSoup(response.text, 'html.parser')
            date_tag = soup.find('p', class_='ahjalpfunktioner')
            if date_tag:
                time_tag = date_tag.find('time')
                date = time_tag.get_text() if time_tag else datetime.datetime.now().strftime("%Y-%m-%d")
            else:
                date = datetime.datetime.now().strftime("%Y-%m-%d")

            title = soup.title.text.strip()
            paragraphs = soup.find_all(['p', 'h1', 'h2'])

            chunks = [p.get_text().strip() for p in paragraphs]
            chunks_en = self.translate_text(chunks)

            # chunks = "\n".join([p.get_text().strip() for p in paragraphs])
            # chunks_en = self.translate_text(chunks)

            # entry = {
            #     "source": url,
            #     "title": title,
            #     "chunk": chunks,
            #     "chunk_en": chunks_en,
            #     "updated": date
            # }

            for chunk_id, chunk in enumerate(chunks):
                entry = {
                    "source": url,
                    "chunk-id": str(chunk_id),
                    "title": title,
                    "chunk": chunk,
                    "chunk_en": chunks_en,
                    "updated": date
                    }
                self.data_buffer.append(entry)



            links = soup.find_all('a')
            for link in links:
                href = link.get('href')
                if href and href.startswith('http'):
                    new_url = href
                else:
                    new_url = urljoin(url, href)
                if new_url not in self.visited_urls:
                    time.sleep(1)
                    self.crawl_website(new_url, output_file, depth=depth + 1, max_depth=max_depth)

        except requests.exceptions.RequestException as err:
            print(f"RequestException: {err}")
        except requests.exceptions.HTTPError as errh:
            print(f"HTTPError: {errh}")
        except requests.exceptions.ConnectionError as errc:
            print(f"ConnectionError: {errc}")
        except Exception as e:
            print(f"An error occurred while processing {url}: {str(e)}")




#%% 3️⃣ Crawl data and save to jsonl file
if __name__ == '__main__':
    crawler = Crawler()

    url = 'https://www.migrationsverket.se/Privatpersoner/Arbeta-i-Sverige/Nyhetsarkiv/2023-11-01-Nu-borjar-det-hojda-forsorjningskravet-for-arbetstillstand-att-galla.html'
    output_file = 'data_crawler/example-data-chunked/migrationverket.jsonl'

    crawler.crawl_website(url, output_file=output_file, max_depth=5)

    # make sure to write remaining data to file
    if crawler.data_buffer:
        crawler.write_to_file(output_file)