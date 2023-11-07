#%% 1.Loading packages
import time                                                         # for time-related tasks
import requests                                                     # for making HTTP requests
from bs4 import BeautifulSoup                                       # for web scraping, parsing HTML
import datetime                                                     # for dealing with dates and times
import jsonlines                                                    # for handling JSONL format
from urllib.parse import urlparse, urljoin                          # for URL parsing and joining
from googletrans import Translator                                  # for text translation using Google Translate API
from langchain.text_splitter import RecursiveCharacterTextSplitter  # for splitting text into chunks with overlapping

#%% 2.Define function to crawl data from the website

class Crawler:
    """
    A Crawler class that crawls through websites and performs translation on the collected data.

    Attributes:
    visited_urls (set): A set to hold the URLs already visited by the crawler.
    translator (Translator): A Translator object to perform translations.
    """
    def __init__(self):
        """

        Initialize the object of the class.

        :param self: The object itself.
        :return: None

        This method initializes the object of the class by initializing the instance variables with appropriate values. It initializes the `visited_urls` set to store unique values. It also
        * initializes the `translator` object which is used for translation purposes. Additionally, it initializes the `splitter` object which is responsible for splitting texts into chunks
        *. Finally, it initializes the `data_buffer` list.

        Example usage:
            >>> obj = ClassName()
        """
        self.visited_urls = set() #! Set is a data structure that stores unique values
        self.translator = Translator()
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size = 1000,
            chunk_overlap = 200,
            length_function = len,
            is_separator_regex = False
        )
        self.data_buffer = []

    def chunk_text(self, input_text):
        return self.splitter.split_text(input_text)  # Return a list of strings with overlapping

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

    def write_visited_urls(self, crawled_urls_file):
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

    def crawl_links(self, url, depth = 10, lang = ['sv', 'en']):
        """
        :param url: The URL to crawl and extract links from.
        :type url: str
        :param depth: The maximum depth of recursion when crawling links. Default value is 5.
        :type depth: int
        :param lang: The list of supported languages. Only crawl links from pages written in one of these languages. Default value is ['sv', 'en'].
        :type lang: list[str]
        :return: None
        :rtype: None

        This method crawls the given URL and extracts links from the web page. It recursively crawls each of the links found on the page up to a maximum depth specified by the `depth` parameter
        *. The method also checks if the web page is written in a supported language specified by the `lang` parameter before crawling the links.

        If the depth parameter is 0 or the URL has already been visited, the method returns without crawling further.

        If the connection to the URL fails or the HTTP response status is not 200, an error message is printed.

        The method uses the `requests` library to make HTTP requests and the `BeautifulSoup` library to parse the HTML content of the web page.

        Example usage:

            crawl_links('https://www.example.com', depth=3, lang=['en', 'fr', 'es'])

        This will crawl the web page at 'https://www.example.com' and recursively crawl each link found on the page up to a depth of 3. Only links from pages written in English, French, or Spanish
        * will be crawled.
        """

        # ! Check if the depth is 0 or the url has been visited
        if (depth == 0) or (url in self.visited_urls):
            return
        try:
            # ! Check connection first
            response = requests.get(url)
            if not response.status_code == 200:
                print(f'Non success status for url {url}')
                return
            self.visited_urls.add(url)  # Add url to visited_urls set

            # ! Extract web elmements
            soup = BeautifulSoup(response.text, 'html.parser')

            paragraphs = soup.find_all(['p', 'h1', 'h2'])
            check_lang = "\n".join([p.get_text().strip() for p in paragraphs])
            check_lang = check_lang[:1000]  # take first 1000 characters to assess the language

            # Check if the website has supported languages
            detected = self.translator.detect(check_lang)
            if detected.lang not in lang:
                # print(f'Page at {url} is written in an unsupported language: {detected.lang}')
                return

            # ! Recursion
            # Find all links on the page
            links = soup.find_all('a')
            # Recursively crawl each of the links found on the page
            for link in links:
                href = link.get('href')
                if href == None or len(href) == 0 or href[0] == '#': continue
                if href.lower().endswith(('.xml', '.pdf')): continue
                if href and href.startswith('http'):
                    new_url = href
                else:
                    new_url = urljoin(url, href)
                if urlparse(new_url).netloc == urlparse(url).netloc and new_url not in self.visited_urls:
                    time.sleep(0.01)
                    self.crawl_links(new_url, depth = depth - 1)

        # ! Give error message when connection fails
        except requests.exceptions.RequestException as err:
            print(f"RequestException: {err}")
        except requests.exceptions.HTTPError as errh:
            print(f"HTTPError: {errh}")
        except requests.exceptions.ConnectionError as errc:
            print(f"ConnectionError: {errc}")
        except Exception as e:
            print(f"An error occurred while processing {url}: {str(e)}")

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
            with open(input_file, 'r') as f:
                urls = [line.strip() for line in f]
        else:
            urls = list(self.visited_urls)

        for url_extract in urls[start:end]:
            try:
                #! Check connection first
                response = requests.get(url_extract)
                if not response.status_code == 200:
                    print(f'Non success status for url {url_extract}')
                    return

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


            #! Give error message when connection fails
            except requests.exceptions.RequestException as err:
                print(f"RequestException: {err}")
            except requests.exceptions.HTTPError as errh:
                print(f"HTTPError: {errh}")
            except requests.exceptions.ConnectionError as errc:
                print(f"ConnectionError: {errc}")
            except Exception as e:
                print(f"An error occurred while processing {url_extract}: {str(e)}")
