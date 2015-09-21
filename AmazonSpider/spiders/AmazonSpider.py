__author__ = 'sandeep kulkarni'

import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.selector import HtmlXPathSelector
from decimal import Decimal
from urlparse import urlparse
import re
import os

class AmazonSpider(CrawlSpider):
    #Name of my spider is 'amazon.com'
    name = 'amazon.com'
    #Domain allowed to crawl is 'amazon.com'
    allowed_domains = ['amazon.com']

    #Seed URL : Wrist Watches of Daniel Wellington or Casio in price range : $50 to $100
    start_urls = ['http://www.amazon.com/s/ref=sr_nr_p_89_3?fst=as%3Aoff&rh=n%3A7141123011%2Cn%3A7147441011%2Cn%3A6358539011%2Cn%3A6358540011%2Cp_36%3A2661614011%2Cp_89%3ADaniel+Wellington%7CCasio&bbn=6358540011&ie=UTF8&qid=1441437557&rnid=2528832011']

    rules = [
        #Rule 1 : Extracts the links matching below regex i.e which contain "Casio" in url as we search for all Casio watches with price in range $50 to $100
        Rule(LinkExtractor(allow=[re.compile(r'.*Casio.*/dp/.*', re.IGNORECASE)]), follow=False, callback='parse_item'),
        #Rule 2 : Crawls the "Next page link" and then crawls the webpages as per Rule 1
        Rule(LinkExtractor(restrict_xpaths=('//a[@id="pagnNextLink"]')), follow=True, callback='parse_item')
    ]

    #Function parse_item which is a callback function for above Rules
    def parse_item(self, response):
        item = scrapy.Item()
        hxs = HtmlXPathSelector(response)

        #default initialize price to 0 as we can have some null/empty prices too
        itemPrice = '$0.0'
        for value in hxs.select('//span[@id="priceblock_ourprice"]/text()').extract():
            itemPrice = value

        #for very rare cases price is also present in priceblock_saleprice
        if itemPrice == '$0.0':
            for value in hxs.select('//span[@id="priceblock_saleprice"]/text()').extract():
                itemPrice = value

        #strip the $ sign
        itemPrice = itemPrice.replace('$','')

        if Decimal(itemPrice) >= 50 and Decimal(itemPrice) <= 100:
            #self.logger.info('Item in price range - %s', Decimal(itemPrice))

            #Write html files to "webpages" folder in project
            fileUrl = urlparse(response.url)
            fileName = fileUrl.path[1:].replace('/dp/','_')
            filePath = os.path.join("webpages", fileName + ".html")
            file = open(filePath, "w")
            file.write(response.body)
            file.close()

        else:
            self.logger.info('Item NOT in price range  - %s', Decimal(itemPrice))

        return item