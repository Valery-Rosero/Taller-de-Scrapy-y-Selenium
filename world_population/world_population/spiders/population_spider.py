import scrapy
from scrapy.exporters import CsvItemExporter

class PopulationItem(scrapy.Item):
    year = scrapy.Field()
    population = scrapy.Field()
    yearly_change = scrapy.Field()
    net_change = scrapy.Field()
    density = scrapy.Field()
    urban_pop = scrapy.Field()
    world_share = scrapy.Field()

class PopulationSpider(scrapy.Spider):
    name = 'population_spider'
    allowed_domains = ['worldometers.info']
    start_urls = ['https://www.worldometers.info/world-population/world-population-by-year/']

    def parse(self, response):
        # Extraer datos de la tabla
        rows = response.xpath('//table[@id="example2"]/tbody/tr')
        
        for row in rows:
            item = PopulationItem()
            item['year'] = row.xpath('.//td[1]/text()').get()
            item['population'] = row.xpath('.//td[2]/text()').get()
            item['yearly_change'] = row.xpath('.//td[3]/text()').get()
            item['net_change'] = row.xpath('.//td[4]/text()').get()
            item['density'] = row.xpath('.//td[5]/text()').get()
            item['urban_pop'] = row.xpath('.//td[6]/text()').get()
            item['world_share'] = row.xpath('.//td[7]/text()').get()
            
            yield item

    def closed(self, reason):
        # Esto asegura que el archivo se cierre correctamente
        self.logger.info('Spider closed: %s', reason)