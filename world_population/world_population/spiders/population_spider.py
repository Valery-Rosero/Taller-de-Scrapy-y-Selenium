import scrapy

class PopulationSpider(scrapy.Spider):
    name = "population_spider"
    start_urls = ["https://www.worldometers.info/world-population/world-population-by-year/"]

    def start_requests(self):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36",
            "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
        }
        for url in self.start_urls:
            yield scrapy.Request(url, headers=headers, callback=self.parse)

    def parse(self, response):
        for fila in response.css("table tbody tr"):
            yield {
                "year": fila.css("td:nth-child(1)::text").get(),
                "population": fila.css("td:nth-child(2)::text").get(),
                "yearly_change": fila.css("td:nth-child(3)::text").get(),
                "net_change": fila.css("td:nth-child(4)::text").get(),
            }
