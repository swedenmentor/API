#%% 1️⃣ Loading packages
import time                                         # for time-related tasks
import requests                                     # for making HTTP requests
from bs4 import BeautifulSoup                       # for web scraping, parsing HTML
import datetime                                     # for dealing with dates and times
import jsonlines                                    # for handling JSONL format
from urllib.parse import urljoin                    # for URL parsing and joining
from googletrans import Translator                  # for text translation using Google Translate API
from langchain.text_splitter import RecursiveCharacterTextSplitter


#%% 2️⃣ Define function to crawl data from the website

def chunk_text(input_text):
    """
    Split a text into chunks of a specific size with overlapping.

    :param input_text: The input text to be chunked.
    :type input_text: str
    :return: A list of strings containing the chunks of the input text with overlapping.
    :rtype: list[str]
    """
    # This part is deposited for writing chunk_text from Langchain library
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size = 1000,
        chunk_overlap  = 200,
        length_function = len,
        is_separator_regex = False
    )
    return text_splitter.split_text(input_text) # Return a list of strings with overlapping

class Crawler:
    """
    A Crawler class that crawls through websites and performs translation on the collected data.

    Attributes:
    visited_urls (set): A set to hold the URLs already visited by the crawler.
    translator (Translator): A Translator object to perform translations.
    """
    def __init__(self):
        self.visited_urls = set() #! Set is a data structure that stores unique values
        self.translator = Translator()
        self.data_buffer = []

    def write_to_file(self, output_file):
        """
        Write data from data buffer to a file.

        :param output_file: The path to the file where the data will be written.
        :type output_file: str
        :return: None
        :rtype: None
        """
        if self.data_buffer:
            with jsonlines.open(output_file, mode = 'a') as file:
                for entry in self.data_buffer:
                    file.write(entry)
                self.data_buffer = []
        return
    def translate_text(self, text):
        """
        Translate Text

        Translate the given text into English using a translator object.

        :param text: The text to be translated.
        :type text: str
        :return: The translated text.
        :rtype: list[str]

        """
        output = []
        for chunk in chunk_text(text):
            detected = self.translator.detect(chunk)
            if detected.lang != 'en':
                translated_chunk = self.translator.translate(chunk, src = detected.lang, dest = 'en').text
                output.append(translated_chunk)
            else:
                output.append(chunk)
        return output


    def crawl_website(self, url, output_file, depth=5):
        """
        Crawls a website starting from a specified URL and extracts information,
        creating an entry for each visited webpage and writing the information to a file.
        The crawl depth is restricted to a configurable maximum depth.

        If exceptions occur during the requests, they get handled and
        an error message is printed to the console.

        :param url (str): The starting URL to crawl from.
        :param output_file (str): The path of the file to which extracted information
                            will be written.
        :param depth (int): The remaining allowing depth for recursion of crawling

        :return: None

        :raises:
            requests.exceptions.RequestException: When a request exception occurs.
            requests.exceptions.HTTPError: When an HTTP error occurs.
            requests.exceptions.ConnectionError: When a connection error occurs.
            Exception: For any other unhandled exceptions.
        """

        #! Check if the depth is 0 or the url has been visited
        if (depth == 0) or (url in self.visited_urls):
            return

        try:
            #! Check connection first
            response = requests.get(url)
            if not response.status_code == 200:
                print(f'Non success status for url {url}')
                return
            self.visited_urls.add(url) # Add url to visited_urls set

            #! Extract web elmements
            soup = BeautifulSoup(response.text, 'html.parser')
            date_tag = soup.find('p', class_='ahjalpfunktioner')
            if date_tag:
                time_tag = date_tag.find('time')
                date = time_tag.get_text() if time_tag else datetime.datetime.now().strftime("%Y-%m-%d")
            else:
                date = datetime.datetime.now().strftime("%Y-%m-%d")

            title = soup.title.text.strip()
            title = self.translate_text(title)
            paragraphs = soup.find_all(['p', 'h1', 'h2'])

            text = "\n".join([p.get_text().strip() for p in paragraphs])
            chunks = self.translate_text(text)

            entries = {}
            for idx, chunk in enumerate(chunks):
                entries[str(idx)] = {
                    "chunk-id": str(idx),
                    "source": url,
                    "title": title,
                    "chunk": chunk,
                    "updated": date,
                }
            for key in entries:
                self.data_buffer.append(entries[key])
            self.write_to_file(output_file)

            #! Recursion
            # Find all links on the page
            links = soup.find_all('a')
            # Recursively crawl each of the links found on the page
            for link in links:
                href = link.get('href')
                if href and href.startswith('http'):
                    new_url = href
                else:
                    new_url = urljoin(url, href)
                if new_url not in self.visited_urls:
                    time.sleep(1)
                    self.crawl_website(new_url, output_file, depth=depth - 1)

        #! Give error message when connection fails
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
    # Initialize models and variables
    crawler = Crawler()
    max_depth = 5
    url = 'https://www.migrationsverket.se/Privatpersoner/Arbeta-i-Sverige/Nyhetsarkiv/2023-11-01-Nu-borjar-det-hojda-forsorjningskravet-for-arbetstillstand-att-galla.html'
    output_file = 'migrationverket.jsonl'



    # Crawling
    crawler.crawl_website(url, output_file=output_file, depth=max_depth)
