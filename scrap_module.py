# [[file:../../../journal.org::*\[2023-12-16 sam. 14:44\] Scraping modules][[2023-12-16 sam. 14:44] Scraping modules:1]]
#============================
# Title: Web Scraping Module
# Author: Quentin Nicoud
# Creation Date: 2023-12-16
#============================

# Import modules
from pathlib import Path
import scrapy, datetime, os, re
from scrapy.crawler import CrawlerProcess
from bs4 import BeautifulSoup
from decimal import Decimal
from datetime import datetime

# Define custom scrapy classes for scanning required URLs
class SpiderWrapper:
    def __init__(self, headers = None):
        if not headers:
            self.headers = {"User-Agent":"Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148"}
            self.headers = {"Content-Type": "text/plain;charset=UTF-8",
                            "Referer": "https://www.amazon.fr/",
                            "Sec-Ch-Ua": '"Not_A Brand";v="8", "Chromium";v="120", "Brave";v="120"',
                            "Sec-Ch-Ua-Mobile": "?0",
                            "Sec-Ch-Ua-Platform": "Linux",
                            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
        else:
            self.headers = headers

        self.process = CrawlerProcess(
            settings={
                "FEEDS": {
                    "items.json": {"format": "json"},
                },
            }
        )

    def set_crawler(self, urls, name_format):
        self.process.crawl(MyGenericSpider,
                      urls = urls,
                      headers = self.headers,
                      name_format = name_format)

    def run(self):
        self.process.start()


class MyGenericSpider(scrapy.Spider):
    name = "MyGenericSpider"
    def __init__(self, urls, headers, name_format, *args, **kwargs):
        assert type(urls)			is list
        assert type(headers)		is dict

        # self.urls should be a list of urls to be parsed
        self.urls = urls
        # self.headers should be a dictionnary containing header variables
        self.headers = headers

        assert type(name_format) is str
        path_output = "/".join(name_format.split("/")[0:-1])
        assert os.path.isdir(path_output)
        assert re.search("{page}", name_format)
        self.name_format = name_format

    def start_requests(self):
        for url in self.urls:
            yield scrapy.Request(url=url,
                                 #meta={'dont_redirect': True,"handle_httpstatus_list": [302]},
                                 dont_filter=True,
                                 headers=self.headers,
                                 callback=self.parse)
    # This method formats the output files gathered by the spider
    def parse(self, response):
        if re.search("/www.", response.url):
            page = response.url.split('.')[1]
        else:
            page = response.url.split('.')[0]
            page = page.split('/')[2]
        filename = re.sub("{page}", page, self.name_format)
        Path(filename).write_bytes(response.body)
        self.log(f"Saved file {filename}")
        print(f"Saved file {filename}")

# Define custom class for beautiful soup html page parsing
class HtmlParser:
    def  __init__(self, file_class_list, item_list, path, currency = "€", debug = False):
        assert type(debug)				is bool
        assert type(currency)			is str
        assert type(path)				is str
        assert type(file_class_list)	is dict

        self.curr = currency
        self.file_class_list = file_class_list
        self.item_list = item_list
        self.path = path
        self.debug = debug

    def curr_string_converter(self, raw_price):
        price = raw_price
        if re.search(f"[0-9{self.curr},.]+ [0-9{self.curr},.]+", price):
            pass
            #print("ok")
            #price = re.sub("([0-9€,.]+) ([0-9€,.]+)", "\1\2", price)

        price = re.search(f"[0-9{self.curr},.]+", raw_price)[0]

        if price[0] == self.curr or price[-1] == self.curr:
            price = re.sub(self.curr, '', price)
        if '€' in price:
            price = re.sub(self.curr,'.', price)
        if ',' in price:
            price = re.sub(',', '.', price)
        return price

    def find_price(self, pathname, class_name):
        with open(pathname, 'r') as html:
            html_doc = html.read()

        soup = BeautifulSoup(html_doc, "html.parser")

        for elem in soup.find_all(["span", "div", "p"]):
            my_regex = re.compile(class_name)

            if "class" in elem.attrs:
                if my_regex.search(" ".join(elem.attrs["class"])):
                    price = self.curr_string_converter(elem.text)
                    return price.split('.')[0]

        # In case no price is found, yield None
        print(f"Price not found:\t{pathname}")
        return "#NA"

    def price_parser(self):
        for file in self.file_class_list:
            for item in self.item_list:
                file_name = f"{self.path}/{file}_{item}.html"
                if os.path.isfile(file_name):
                    yield self.find_price(file_name, self.file_class_list[file])
                else:
                    print(f"Not found:\t{file_name}")
                    yield "#NA"

    def format_table_row(self, price_values):
        today = datetime.today()
        date_str = today.strftime('[%Y-%m-%d %a.]').lower()
        # Create the proper output
        price_values.insert(0, date_str)
        return "| " +  " | ".join(price_values) + " |"

    def gen_row(self):
        price_vals = [ val for val in self.price_parser()]
        return self.format_table_row(price_vals)
# [2023-12-16 sam. 14:44] Scraping modules:1 ends here
