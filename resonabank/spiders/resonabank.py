import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from resonabank.items import Article


class resonabankSpider(scrapy.Spider):
    name = 'resonabank'
    start_urls = ['https://www.resonabank.co.jp/about/newsrelease/index.html']

    def parse(self, response):
        links = response.xpath('//dd/a/@href').getall()
        yield from response.follow_all(links, self.parse_article)

        next_page = response.xpath('//a[@class="next page-numbers"]/@href').get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_article(self, response):
        if 'pdf' in response.url.lower():
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h1/span/text()').get()
        if title:
            title = title.strip()

        date = response.xpath('//p[@class="tRight mb10"]/text()').get()
        if date:
            date = " ".join(date.split())
        else:
            return

        content = response.xpath('//main//text()').getall()
        content = [text.strip() for text in content if text.strip() and '{' not in text]
        content = " ".join(content).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
