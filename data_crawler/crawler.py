#%% 1.Loading packages
import time                                                         # for time-related tasks
import requests                                                     # for making HTTP requests
from requests.adapters import HTTPAdapter
from requests.exceptions import HTTPError, RequestException, ConnectionError
import urllib3
from bs4 import BeautifulSoup                                       # for web scraping, parsing HTML
import datetime                                                     # for dealing with dates and times
import jsonlines                                                    # for handling JSONL format
from urllib.parse import urlparse, urljoin                          # for URL parsing and joining
from googletrans import Translator                                  # for text translation using Google Translate API
from langchain.text_splitter import RecursiveCharacterTextSplitter  # for splitting text into chunks with overlapping
from utils.custom_logger import CustomLogger
import random
import re
from bs4.element import Tag


SUPPORTED_LANGUAGES = ['sv', 'en']


#%% 2.Define function to crawl data from the website

class Crawler:
    """Master Crawler class
    """
    def __init__(
            self, 
            total_retries: int = 3, 
            backoff_factor: float = 0.1, 
            status_forcelist: list[int] = [500, 502, 503, 504, 429],
            logger: CustomLogger = None
    ):
        
        self.target_urls = set()    # Set of URLs to be crawled
        self.visited_urls = set()   # Set of URLs visited
        self.translator = Translator()
        # self.splitter = RecursiveCharacterTextSplitter(
        #     chunk_size=1000,
        #     chunk_overlap=200,
        #     length_function=len,
        #     is_separator_regex=False
        # )
        self.data_buffer = []
        self.logger = logger or CustomLogger(name=self.__class__.__name__, write_local=False) 
        
        self.total_retries = total_retries
        self.backoff_factor = backoff_factor
        self.status_forcelist = status_forcelist
        self.session = self.get_session()
    
    def get_session(self):
        """Generate a session object with retry settings.

        Parameters
        ----------
        total_retries : int
            Total number of retries allowed
        backoff_factor : float
            This parameter affects how long the process waits before retrying a request.
            wait_time = {backoff factor} * (2 ** ({number of total retries} - 1))
            For example, if the backoff_factor is 0.1, the process will sleep for [0.1s, 0.2s, 0.4s, ...] between retries.
        status_forcelist : list[int]
            List of status codes that will trigger a retry.
        """
        retries = urllib3.Retry(
            total=self.total_retries, 
            backoff_factor=self.backoff_factor, 
            status_forcelist=self.status_forcelist
        )
        adapter = HTTPAdapter(max_retries=retries)
        session = requests.Session()
        session.mount('http://', adapter)

        return session
        
    def get_url(self, url: str): 
        """Get the response from a URL.

        Parameters
        ----------
        url : str
            The URL to get the response from.
        """
        
        response = self.session.get(url)
        try:
            response.raise_for_status()
        except (HTTPError, RequestException, ConnectionError) as err:
            self.logger.error(f'Error when connecting: {err}')
        else:
            return response

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
        for chunk in self.splitter.split_text(text):
            retry_count = 0
            while retry_count < 3:  # retry up to 3 times
                try:
                    detected = self.translator.detect(chunk)
                    if detected.lang != 'en':
                        translated_chunk = self.translator.translate(chunk, src=detected.lang, dest='en').text
                        output.append(translated_chunk)
                    else:
                        output.append(chunk)
                    break  # if translation is successful, break the retry loop
                except AttributeError as e:
                    retry_count += 1
                    self.logger.warning(f'An error occurred during translation ({str(e)}), attempt {retry_count}, retrying in 2 seconds...')
                    time.sleep(2)
                    continue
                except Exception as e:  # catch other exceptions that could occur
                    self.logger.error(f'An unexpected error occurred during translation: {str(e)}')
                    raise e

        return output

    def write_visited_urls(self, crawled_urls_file: str):
        '''
        Write visited urls to a file.
        :param file: The path to the .txt file where the urls will be written.
        :type file: str
        :return: None
        :rtype: None
        '''
        with open(crawled_urls_file, 'w', encoding='utf-8') as f:
            for url in self.visited_urls:
                f.write(f'{url}\n')


    def page_language_supported(self, soup: BeautifulSoup) -> bool:
        """Check if the page is written in a supported language (Defined by the SUPPORTED_LANGUAGE variable)

        Parameters
        ----------
        soup : BeautifulSoup
            A BeautifulSoup object representing the text content

        Returns
        -------
        bool
        """
        paragraphs = soup.find_all(['p', 'h1', 'h2', 'h3'])
        check_lang = "\n".join([p.get_text().strip() for p in paragraphs])[:1000]

        detected = self.translator.detect(check_lang)
        
        if detected.lang not in SUPPORTED_LANGUAGES:
            self.logger.warning(f'The page is written in an unsupported language: {detected.lang}')
            return False
        else:
            return True


    def crawl_links(self, url: str, depth: int = 10, base_url: str = ''):
        """Recursively crawl links in a web site, and return a list of URLs.

        Parameters
        ----------
        url : str
        depth : int, optional
            The depth that we want to go, by default 10 pages.
        base_url : str, optional
            The base url to be used if the href attributes are relative path instead of full URL.
        """


        # ! Check if the depth is 0 or the url has been visited
        if url in self.target_urls:
            self.logger.info("URL existed - skip.")
            return
        if depth == 0:
            self.logger.info("No depth to travel.")
            return
        
        self.logger.info(f'Visiting: {url}')
        response = requests.get(url, timeout=300)
        try:
            # Check if the url is valid
            response.raise_for_status()
        except (HTTPError, RequestException, ConnectionError) as err:
            self.logger.error(f'Error when connecting: {err}')
            return
        else:
            self.target_urls.add(url)  # Add the URL to the result set if it is valid

        
        # Check if the website has supported languages
        self.logger.info("Parsing response...")
        soup = BeautifulSoup(response.text, 'html.parser')

        if self.page_language_supported(soup) is False:
            return

        # Use recursion to find all links
        links = soup.find_all('a')

        for link in links:
            href = link.get('href')

            if (href is None) or (len(href)==0) or ('#' in href): 
                continue

            exc_patterns = ('.xml', '.pdf', '.jpg', '.png', '.zip', '.printable', '.contenttype=text/xml;charset=UTF-8')
            if href.lower().endswith(exc_patterns): 
                continue

            if href and href.startswith('http'):
                new_url = href
            else:
                new_url = urljoin(base_url, href)
            
            if urlparse(new_url).netloc == urlparse(url).netloc and new_url not in self.visited_urls:
                time.sleep(random.randint(0, 10) / 100)  
                self.crawl_links(new_url, depth=depth - 1)


    def write_web_element(self, output_file):
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

    def extract_json(self, base_url, output_file):
        """
        :param base_url: The base URL used to make requests and retrieve JSON data.
        :type base_url: str
        :param output_file: The name of the file to which the extracted JSON data will be written.
        :type output_file: str
        :return: None
        :rtype: None

        The `extract_json` method is used to extract JSON data from a given URL and write it to a specified output file. It uses a loop to iterate through the pages of the API, making requests
        * and extracting the necessary data.

        Within the loop, it checks if the URL has been visited by checking the response status code. If the code is 200, it proceeds to extract the JSON data from the response using the `json
        *()` method. It then iterates through each item in the JSON data and creates a new dictionary to hold the required fields.

        To extract the necessary fields, it checks if the 'content' key is present in the item and if it contains a 'rendered' key. If so, it retrieves the text by parsing the HTML with BeautifulSoup
        *. It then splits the text into chunks using a splitter method and adds each chunk to the dictionary.

        Other fields such as 'source', 'title', 'updated', and 'chunk-id' are also added to the dictionary. The dictionary is then appended to a result list, which is stored in a data buffer
        *.

        After iterating through all the items on the page, the `write_web_element` method is called to write the data from the data buffer to the specified output file.

        The page number is increased for the next iteration, and the loop continues until the response status code is not 200.

        Note: The requests library and BeautifulSoup library are used in this method, so make sure to import them before using this method.
        """
        page = 1
        while True:
            url = base_url.format(page)
            response = requests.get(url)

            # Check if the url has been visited
            if response.status_code == 200:
                # Extract the JSON data from the response
                soup = response.json()

                for item in soup:
                    # Create a new dictionary to hold the required fields
                    temp_dict = {}
                    input_text = item['content']['rendered'] if 'content' in item and 'rendered' in item[
                        'content'] else None
                    sub_url = item['link']
                    print(f'Successful extract and add the url: {sub_url}')
                    self.visited_urls.add(sub_url)
                    input_text = BeautifulSoup(input_text, 'html.parser').get_text(separator = '').replace('\n', ' ').replace('\r', '').strip()
                    chunks = self.splitter.split_text(input_text)

                    for idx, chunk in enumerate(chunks):
                        temp_dict[str(idx)] = {
                            "chunk-id": str(idx),
                            "source": item['link'],
                            "title": item['title']['rendered'] if 'title' in item and 'rendered' in item[
                                'title'] else None,
                            "chunk": chunk,
                            "updated": datetime.datetime.strptime(item['date'], "%Y-%m-%dT%H:%M:%S").strftime(
                                "%Y-%m-%d") if 'date' in item else None,
                        }
                    # Append the new dictionary to the result list
                    self.data_buffer.append(temp_dict)

                self.write_web_element(output_file)
                # Increase the page number for the next iteration
                page += 1
            else:
                # If the response status code is not 200, break the loop
                break


    def extract_web_element(self, output_file, input_file = None, tags = ['p', 'h1', 'h2'], start=0, end=None, special_tags=None, class_name=None):
        """
        Crawls a website starting from a specified URL and extracts information,
        creating an entry for each visited webpage and writing the information to a file.
        The crawl depth is restricted to a configurable maximum depth.
        If exceptions occur during the requests, they get handled and
        an error message is printed to the console.
        :param start (int): The starting line or element to read from.
        :param end (int): The ending line or element to read to. If None, read to the end.
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
        urls = []
        if input_file is not None:
            with open(input_file, 'r', encoding='utf-8') as f:
                urls = [line.strip() for line in f]
        else:
            urls = list(self.visited_urls)

        for url_extract in urls[start:end]:
            self.logger.info(f'Visiting: {url_extract}')
            response = requests.get(url_extract)
            try:
                #! Check connection first
                response.raise_for_status()
                
            except (RequestException, HTTPError, ConnectionError) as err:
                self.logger.error(f'Error when connecting: {err}')
                return

            # TODO: Add more detailed error handling. Should not try to do do 
            # too many things in one try block

            self.logger.info("Parsing response...")
            
            #! Extract web elmements
            soup = BeautifulSoup(response.text, 'html.parser')
            if special_tags is not None and class_name is not None:
                paragraphs = [tag for tag in soup.find_all(tags) if
                                not (tag.name in special_tags and tag.get('class') != [class_name])]
            else:
                paragraphs = soup.find_all(tags)
            text = " ".join([p.get_text().strip() for p in paragraphs])


            # TODO: Find all date tags for all websites
            date_tag = soup.find('p', class_ = 'ahjalpfunktioner')
            if date_tag:
                time_tag = date_tag.find('time')
                date = time_tag.get_text() if time_tag else datetime.datetime.now().strftime("%Y-%m-%d")
            else:
                date = datetime.datetime.now().strftime("%Y-%m-%d")

            title = soup.title.text.strip()
            title = self.translate_text(title)
            chunks = self.translate_text(text)
            
            try:

                entries = {}
                for idx, chunk in enumerate(chunks):
                    entries[str(idx)] = {
                        "chunk-id": str(idx),
                        "source": url_extract,
                        "title": title[0],
                        "chunk": chunk,
                        "updated": date,
                    }
                for key in entries:
                    self.data_buffer.append(entries[key])
                self.write_web_element(output_file)
                print(f"Successfully extracted web element from {url_extract}")

            except Exception as e:
                self.logger.error(f"An error occurred while processing {url_extract}: {str(e)}")
