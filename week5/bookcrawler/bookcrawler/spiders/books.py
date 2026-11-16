import scrapy


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls
    page_seen = 0
    
    start_urls = ["https://books.toscrape.com"]

    def parse(self, response):
        pass

