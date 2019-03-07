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
        years_url_list = response.css("p.lista_lat a::attr(href)").extract()
        for url in years_url_list:
            yield scrapy.Request(url=url, callback=self.parse_years_page)

    def parse_years_page(self, response):
        lottery_numbers = response.css("ul li.nr_in_list::text").re("\d+")
        dates = response.css("ul li.date_in_list::text").extract()
        winning_numbers = self.parse_winning_numbers(response.css("ul li.numbers_in_list::text").re("\d+"))
        for i in xrange(len(lottery_numbers)):
            yield {
                'lottery_nr': lottery_numbers[i],
                'date': dates[i],
                'winning': winning_numbers[i]
            }

    def parse_winning_numbers(self, all_numbers):
        result = []
        for index in xrange(0, len(all_numbers) - 6, 6):
            single_draw_result = all_numbers[index:index + 6]
            result.append(",".join(single_draw_result))
        return result
