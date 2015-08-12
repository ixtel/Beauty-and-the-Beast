# -*- coding: utf-8 -*-
import logging
from urlparse import urljoin
from scrapy import Request, Spider
from scrapy.exceptions import DropItem

from scrapy_project.items import (
    StoreItem, AppleStoreLocationLoader)


class AppleStoresSpider(Spider):
    name = "apple_stores"
    allowed_domains = ["apple.com"]
    start_urls = (
        'http://www.apple.com/',
    )

    name = 'apple_stores'
    allowed_domains = ['apple.com']
    # HINT: not type safe i.e. no validation
    # if it's an iterable collection or just a string
    start_urls = ('https://www.apple.com/retail/storelist/', )

    xpaths = {
        'country_nodes': '//div[@class="listing"]',
        'store_nodes': './/div[contains(@class, "column")]/ul',
    }

    countries_mapping = {
        'usstores': u'United States',
        'austores': u'Australia',
        'ukstores': u'United Kingdom',
        'jpstores': u'Japan',
        'castores': u'Canada',
        'itstores': u'Italy',
        'cnstores': u'China',
        'chstores': u'Switzerland',
        'destores': u'Germany',
        'frstores': u'France',
        'nlstores': u'Netherlands',
        'esstores': u'Spain',
        'hkstores': u'Hong Kong',
        'sestores': u'Sweden',
        'brstores': u'Brazil',
        'trstores': u'Turkey',
    }

    def parse(self, response):
        """ HINT: Scrapy contracts doesn't work if
        callback is defined inside the mixin
        """
        nodes = response.xpath(self.xpaths['country_nodes'])
        ids = nodes.xpath('./@id').extract()

        for node, country_id in zip(nodes, ids):
            country = self.countries_mapping[country_id]
            store_nodes = node.xpath(self.xpaths['store_nodes'])

            logging.info("Country: {}".format(country))
            for store_node in store_nodes:
                hrefs = store_node.xpath('./li/a/@href').extract()
                names = store_node.xpath('./li/a/text()').extract()
                cities = store_node.xpath('./li/text()').extract()

                for city, href, name in zip(cities, hrefs, names):
                    data = {
                        'city': city.strip(),
                        'store_name': name.strip(),
                        'country': country,
                        'store_url': urljoin(response.url, href)
                    }

                    yield Request(
                        data['store_url'],
                        callback=self.parse_retailer_details,
                        meta={'data': data}
                    )

    def parse_retailer_details(self, response):
        """ Get retailer details

        @url http://www.apple.com/retail/soho/
        @returns items 1 1
        @returns requests 0 0
        @scrapes address city country hours phone_number
        """
        logging.info("Retailers page scraped: {}".format(response.url))

        store_name = response.xpath(
            '//section/h1/text()').extract()
        image_url = response.xpath(
            '//div[@class="store-summary"]//img/@src').extract()
        address = response.xpath(
            '//address[1]/div[@class="street-address"]/text()').extract()
        locality = response.xpath(
            '//address[1]/span[@class="locality"]/text()').extract()
        region = response.xpath(
            '//address[1]/span[@class="region"]/text()').extract()
        postal_code = response.xpath(
            '//address[1]/span[@class="postal-code"]/text()').extract()
        phone_number = response.xpath(
            '//address[1]/div[@class="telephone-number"]/text()').extract()

        print store_name, image_url, address, locality

        services = response.xpath(
            '//nav[contains(@class, "hero-nav")]'
            '/div[contains(@class, "nav-buttons")]/a/img/@alt'
        ).extract()
        weekly_events = response.xpath(
            '//a[contains(@class, "reserve")]/@href').extract()
        if weekly_events:
            weekly_events = weekly_events[-1]

        # extract hours
        # hours: (dict) Store hours are stored according
        # to the following schema:
        # {
        #   day­of­week: {
        #     open: time,
        #     close: time
        #   },
        #   ...
        # }

        hours = response.xpath(
            '//td[contains(text(), "Store hours")]/../..//td/text()').extract()
        hours = hours[1:]  # skip "Store hours"
        if len(hours) % 2 != 0:
            logging.error(
                "Error scraping hours from url: {}".format(response.url))

        # >> In [1]: a = [1,2,3,4,5,6]
        # >> In [2]: a[::2]
        # >> Out[2]: [1, 3, 5]
        # >> In [3]: a[1::2]
        # >> Out[3]: [2, 4, 6]

        hours_dict = {}
        for key, value in zip(hours[::2], hours[1::2]):
            try:
                # usually value is similar to 'from 10:00p.m. - 18:00p.m.'
                open_time, close_time = map(unicode.strip, value.split(u'-'))
            except ValueError as ex:
                if u' to ' in value:
                    # could be like
                    # from 10:00p.m. to 18:00p.m.
                    open_time, close_time = map(
                        unicode.strip, value.split(u't')
                    )
                    close_time = close_time.strip(u'o')
                elif u'Closed' in value:
                    open_time, close_time = 'Closed', 'Closed'
                else:
                    logging.error(ex)
                    raise DropItem(
                        "Can't extract open_time "
                        "or close_time from: {}".format(value))
            else:
                hours_dict[key] = {
                    u'open': open_time,
                    u'close': close_time,
                }

        l = AppleStoreLocationLoader(item=StoreItem())
        l.add_value('city', response.meta['data']['city'])

        # form full address
        l.add_value('address', region)
        l.add_value('address', locality)
        l.add_value('address', address)
        l.add_value('address', postal_code)

        l.add_value('country', response.meta['data']['country'])
        l.add_value('hours', hours_dict)
        l.add_value('phone_number', phone_number)
        l.add_value('services', services)
        l.add_value('state', region)

        # store
        l.add_value('store_email', u'')
        l.add_value('store_id', store_name)
        l.add_value('store_image_url', image_url)
        l.add_value('store_name', store_name)
        l.add_value('store_url', unicode(response.url))
        l.add_value('weekly_ad_url', weekly_events)
        l.add_value('zipcode', postal_code)
        return l.load_item()
