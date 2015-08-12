# -*- coding: utf-8 -*-
import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import (
    TakeFirst, MapCompose, Identity)


class AppleStoreLocationLoader(ItemLoader):
    default_input_processor = MapCompose(unicode.strip)
    default_output_processor = TakeFirst()

    address_out = Identity()
    hours_in = Identity()


class StoreItem(scrapy.Item):
    """ Location spiders extract information about every retailer store.

    Fields:
    + city: (string) City the store is located in
    + address: (string_list) All lines of the address block,
      one line per list entry
    + country: (string) Country name or abbreviation
    + hours: (dict) Store hours are stored according to the following format:
      { day­of­week: { open: time, close: time }, ... }.
      Only US store hours are necessary.
    + phone_number: (string) Store phone number
    + services: (string list) Store services
    + state: (string) State name or abbreviation
    + store_email: (string) Store Email
    + store_floor_plan_url: (string) URL of store floor plan map
    + store_id: (string) Store number or ID
    + store_image_url: (string) Picture of the store
    + store_name: (string) Name of the store
    + store_url: (string) URL to specific store information page
    + weekly_ad_url: (url) URL of weekly ad / circular
    + zipcode: (string) 5 digit zip code
    """

    city = scrapy.Field()
    address = scrapy.Field()
    country = scrapy.Field()
    hours = scrapy.Field()
    phone_number = scrapy.Field()
    services = scrapy.Field()
    state = scrapy.Field()
    store_email = scrapy.Field()
    store_floor_plan_url = scrapy.Field()
    store_id = scrapy.Field()
    store_image_url = scrapy.Field()
    store_name = scrapy.Field()
    store_url = scrapy.Field()
    weekly_ad_url = scrapy.Field()
    zipcode = scrapy.Field()

    created_at = scrapy.Field()
    updated_at = scrapy.Field()
