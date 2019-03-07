import scrapy


class LottoSpider(scrapy.Spider):
    name = "lotto"

    def start_requests(self):
        urls = [
            'http://megalotto.pl/wyniki/lotto'
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        years_url_list = response.xpath(
            "//div[@class='list_of_last_drawings lotto_list_of_last_drawings']/p[@class='lista_lat']/a/@href").extract()
        for url in years_url_list:
            print url
