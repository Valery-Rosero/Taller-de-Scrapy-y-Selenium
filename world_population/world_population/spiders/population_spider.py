import scrapy


class PopulationSpiderSpider(scrapy.Spider):
    name = "population_spider"
    allowed_domains = ["worldometers.info"]
    start_urls = ["https://worldometers.info"]

    def parse(self, response):
        pass
