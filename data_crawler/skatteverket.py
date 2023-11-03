# %% 1️⃣ Loading packages
# load packages need for crawling data
import requests
from bs4 import BeautifulSoup


# %% 2️⃣ Crawling the web
# define the url to crawl
url = "https://www.skatteverket.se/"
# get the html from the url
html = requests.get(url).text
# parse the html
soup = BeautifulSoup(html, 'html.parser')


