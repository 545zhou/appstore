import scrapy
import re
from scrapy.selector import Selector
from appstore.items import AppstoreItem
from scrapy.contrib.spiders import CrawlSpider, Rule

class HuaweiSpider(scrapy.Spider):
  name = "huawei"
  allowed_domains = ["huawei.com"]

  start_urls = [
     "http://appstore.huawei.com/more/all/1"
  ]
  

  def parse(self, response):
    page = Selector(response)

    hrefs = page.xpath('//h4[@class="title"]/a/@href')

    if hrefs == []:
      raise ValueError('last page!')

    for href in hrefs:
      url = href.extract()
      print('going')
      yield scrapy.Request(url, self.parse_item, meta = {
        'splash': {
            'endpoint': 'render.html',
            'args': {'wait': 0.5}
        }
      })
      print('finish')

    url = response.url
    page_num_str = url.split('/')[-1]
    page_num = int(page_num_str) + 1

    next_page_url = url[:-len(page_num_str)] + str(page_num)

    print(next_page_url)

    try:
      yield scrapy.Request(next_page_url, self.parse)
    except ValueError:
      return # finish

  def parse_item(self, response):
    print('Arrive at detail page')
    page = Selector(response)
    item = AppstoreItem()

    item['title'] = page.xpath('//ul[@class="app-info-ul nofloat"]/li/p/span[@class="title"]/text()'). \
        extract_first().encode('utf-8')
    
    item['url'] = response.url
    item['appid'] = re.match(r'http://.*/(.*)', item['url']).group(1)
    item['intro'] = page.xpath('//meta[@name="description"]/@content'). \
        extract_first().encode('utf-8')

    divs = page.xpath('//div[@class="open-info"]')
    recomm = ""
    for div in divs:
      url = div.xpath('./p[@class="name"]/a/@href').extract_first()
      recommended_appid = re.match(r'http://.*/(.*)', url).group(1)
      name = div.xpath('./p[@class="name"]/a/text()').extract_first().encode('utf-8')
      recomm += "{0}:{1},".format(recommended_appid, name)

    item['recommended'] = recomm
    yield item
