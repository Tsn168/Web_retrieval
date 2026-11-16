import hashlib
import re

import scrapy

RATINGS = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def __init__(self, max_pages=2, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.max_pages = max(1, int(max_pages))
        self.pages_seen = 0

    def parse(self, response):
        self.pages_seen += 1

        for href in response.css("article.product_pod h3 a::attr(href)").getall():
            yield response.follow(href, callback=self.parse_book)

        next_href = response.css("li.next a::attr(href)").get()
        if next_href and self.pages_seen < self.max_pages:
            yield response.follow(next_href, callback=self.parse)

    def parse_book(self, response):
        main = response.css("div.product_main")

        title = main.css("h1::text").get(default="").strip()

        description = (
            response.css("#product_description + p").xpath("normalize-space(.)").get()
            or ""
        )

        category = response.css(
            "ul.breadcrumb li:nth-child(3) a::text"
        ).get(default="").strip()

        price_text = main.css("p.price_color::text").get(default="")
        price_match = re.search(r"[\d.]+", price_text)
        price_gbp = float(price_match.group()) if price_match else None

        rating_class = main.css("p.star-rating::attr(class)").get(default="")
        rating = next(
            (value for name, value in RATINGS.items() if name in rating_class.split()),
            None,
        )

        availability = (
            main.css("p.availability").xpath("normalize-space(.)").get() or None
        )

        yield {
            "doc_id": hashlib.sha1(response.url.encode("utf-8")).hexdigest()[:12],
            "title": title,
            "text": f"{title}. {description}".strip(),
            "description": description,
            "url": response.url,
            "category": category,
            "price_gbp": price_gbp,
            "rating": rating,
            "availability": availability,
            "source": "books.toscrape.com",
        }
