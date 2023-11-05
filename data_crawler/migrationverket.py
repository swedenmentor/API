#%% 1️⃣ Loading packages
import time                                         # for time-related tasks
import requests                                     # for making HTTP requests
from bs4 import BeautifulSoup                       # for web scraping, parsing HTML
import datetime                                     # for dealing with dates and times
import jsonlines                                    # for handling JSONL format
from urllib.parse import urlparse, urljoin          # for URL parsing and joining
from googletrans import Translator                  # for text translation using Google Translate API
from langchain.text_splitter import RecursiveCharacterTextSplitter

#from langdetect import detect, LangDetectException  # for language detection

#%% 2️⃣ Define function crawl data from the website
def word_count(text):
    return len(text.split())

def chunk_text(input_text):
    # This part is deposited for writing chunk_text from Langchain library
    '''# With text_splitter = RecursiveCharacterTextSplitter(
        chunk_size = 1000,
        chunk_overlap  = 200,
        length_function = len,
        is_separator_regex = False
    )'''
    return text_splitter.split_text(input_text) # Return a list of strings with overlapping


def check(url):
    global URL_list
    return (url in URL_list.keys())

def neareast_next_full_stop(text):
    pos = text.rfind('.')
    if pos != -1:
        return pos+1
    else:
        return len(text)


class Crawler:
    """
    A Crawler class that crawls through websites and performs translation on the collected data.

    Attributes:
    visited_urls (set): A set to hold the URLs already visited by the crawler.
    translator (Translator): A Translator object to perform translations.
    """
    def __init__(self):
        self.translator = Translator()
        self.data_buffer = []

    def write_to_file(self, output_file):
        if self.data_buffer:
            with jsonlines.open(output_file, mode = 'a') as file:
                for entry in self.data_buffer:
                    file.write(entry)
                self.data_buffer = []

    
        return
    def translate_text(self, text):
        '''chunks = []
        words = text.split(" ")
        temp = ""
        for word in words:
            temp += word + " "
            if len(temp.split()) >= 300:
                temp = temp.rsplit(' ', 1)[0]
                chunks.append(temp)
                temp = word + " "
        if temp.strip():
            chunks.append(temp.strip())

        output = []
        for chunk in chunks:
            detected = self.translator.detect(chunk)
            if detected.lang != 'en':
                translated_chunk = self.translator.translate(chunk, src = detected.lang, dest = 'en').text
                output.append(translated_chunk)
            else:
                output.append(chunk)
        return ' '.join(output)'''
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
        if (depth == 0) or (check(url)): return
        global URL_list
        URL_list[url]=True
        try:
            response = requests.get(url)
            if not response.status_code == 200:
                print(f'Non success status for url {url}')
                return
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

            entry = {
                "source": url,
                "title": title,
                "chunk": chunks,
                # "chunk_en": chunk_en,
                "updated": date
            }
            self.data_buffer.append(entry)
            self.write_to_file(output_file)

            links = soup.find_all('a')
            for link in links:
                href = link.get('href')
                if href and href.startswith('http'):
                    new_url = href
                else:
                    new_url = urljoin(url, href)
                if new_url not in self.visited_urls:
                    time.sleep(1)
                    self.crawl_website(new_url, output_file, depth=depth - 1)

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
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size = 1000, chunk_overlap  = 200,
        length_function = len, is_separator_regex = False)
    url = 'https://www.migrationsverket.se/Privatpersoner/Arbeta-i-Sverige/Nyhetsarkiv/2023-11-01-Nu-borjar-det-hojda-forsorjningskravet-for-arbetstillstand-att-galla.html'
    output_file = 'migrationverket.jsonl'
    URL_list={}
    # Crawling
    crawler.crawl_website(url, output_file=output_file, depth=2)

    # # make sure to write remaining data to file
    # if crawler.data_buffer:
    #     crawler.write_to_file(output_file)