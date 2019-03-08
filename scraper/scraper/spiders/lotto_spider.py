import scrapy
import re
from scrapy import Item, Field
from scrapy.selector import HtmlXPathSelector


class LottoData(Item):
    lottery_nr = Field()
    date = Field()
    winning = Field()
    degree = Field()
    number = Field()
    amount = Field()


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

        lottery_numbers = response.css("ul li.nr_in_list::text").extract()
        dates = response.css("ul li.date_in_list::text").extract()
        winning_numbers = self.parse_winning_numbers(response.css("ul li.numbers_in_list::text").re("\d+"))

        hxs = HtmlXPathSelector(response)

        if hxs.select('//div[@class="list_of_last_drawings lotto_list_of_last_drawings"]/div['
                      '@class="lista_ostatnich_losowan"]/ul/a/@href').extract():
            detailed_info_urls = hxs.select('//div[@class="list_of_last_drawings lotto_list_of_last_drawings"]/div['
                                            '@class="lista_ostatnich_losowan"]/ul/a/@href').extract()
            for l, d, w, u in zip(lottery_numbers, dates, winning_numbers, detailed_info_urls):
                lotto_data = LottoData()
                lotto_data['lottery_nr'] = re.sub('\\.', '', l)
                lotto_data['date'] = d
                lotto_data['winning'] = w
                lotto_data['degree'] = ''
                lotto_data['number'] = ''
                lotto_data['amount'] = ''
                request = scrapy.Request(u, callback=self.parse_detailed_info)
                request.meta['lotto_data'] = lotto_data

                yield request
        else:
            for l, d, w in zip(lottery_numbers, dates, winning_numbers):
                lotto_data = LottoData()
                lotto_data['lottery_nr'] = re.sub('\\.', '', l)
                lotto_data['date'] = d
                lotto_data['winning'] = w
                lotto_data['degree'] = ''
                lotto_data['number'] = ''
                lotto_data['amount'] = ''

                yield lotto_data

    def parse_winning_numbers(self, all_numbers):
        result = []
        for index in range(0, len(all_numbers) - 5, 6):
            single_draw_result = all_numbers[index:index + 6]
            result.append(",".join(single_draw_result))
        return result

    def parse_detailed_info(self, response):
        lotto_data = response.meta['lotto_data']

        date = self.normalize_whitespace(
            u''.join(response.css('h2[class="archiwalne-wygrane archiwalne-wygrane-lotto"]::text').extract()))
        date = re.sub('\\s*[a-zA-Z]*', '', date)

        degree_list = []
        num_list = []
        amount_list = []

        for tr in response.xpath('//*[@class="dl_wygrane_table"]//tr'):

            degree = tr.xpath('string(./td[1])').extract_first()
            number = tr.xpath('string(./td[2])').extract_first()
            amount = tr.xpath('string(./td[3])').extract_first()

            if number:
                number = number.strip()
                num_list.append(number)

            if amount:
                amount = re.sub('\\s+', '', amount)
                amount_list.append(amount)

            if degree:
                degree = degree.strip()
                degree = degree.replace(":", "")
                degree_list.append(degree)

        if date == lotto_data['date']:
            for j in range(len(num_list)):
                lotto_data['degree'] = degree_list[j]
                lotto_data['number'] = num_list[j]
                lotto_data['amount'] = amount_list[j]
                yield lotto_data

    def normalize_whitespace(self, str):
        import re
        str = str.strip()
        str = re.sub(r'\s+', ' ', str)
        return str
