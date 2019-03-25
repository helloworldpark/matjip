from utils.url import URL
from utils.http import get_html
from utils.excel import ExcelConvertible, to_excel
from utils.pool import distribute_work
from bs4 import BeautifulSoup
from time import sleep
import re


class TabelogURL(URL):

    def __init__(self, ken, city, page):
        """
        :param ken:
        :type ken: str
        :param city:
        :type city: str
        :param page:
        :type page: int
        """
        self.ken = ken
        self.city = city
        self.page = page

    def url(self):
        return "https://tabelog.com/{:s}/C1100/rstLst/{:d}/?vs=2&sa={:s}&sk=&lid=hd_search1&vac_net=&svd=20190323&svt=1930&svps=1&hfc=1&sw=".format(
            self.ken, self.page, self.city
        )


class TabelogInfo(ExcelConvertible):

    def __init__(self, name, rating, reviews, price_night, price_noon):
        """
        :param name:
        :type name: str
        :param rating:
        :type rating: float
        :param reviews:
        :type reviews: int
        :param price_night:
        :type price_night: float
        :param price_noon:
        :type price_noon: float
        """
        self.name = name
        self.rating = rating
        self.reviews = reviews
        self.price_night = price_night
        self.price_noon = price_noon

    def column_names(self):
        return ['name', 'rating', 'reviews', 'price_night', 'price_noon']


def collect_info_sapporo(page):
    url_sapporo = TabelogURL(ken='hokkaido', city='札幌市', page=page)
    body, ok = get_html(url=url_sapporo.url())
    if not ok:
        return False, []

    # start parsing
    soup = BeautifulSoup(body, features="lxml")
    shops = soup.select('#column-main > ul > li')

    info_list = []
    for shop in shops:
        name_soup = shop.select('div.list-rst__header > div > div > div > a')
        if not name_soup:
            continue

        rate_soup = shop.select('div.list-rst__body > div.list-rst__contents > div.list-rst__rst-data > div.list-rst__rate')[0]

        rating_soup = rate_soup.find_all('p', class_=re.compile("^c-rating"))
        review_soup = rate_soup.select('p.list-rst__rvw-count > a')
        price_night_soup = shop.select('div.list-rst__body > div.list-rst__contents > div.list-rst__rst-data > ul.list-rst__budget > li:nth-child(1) > span.c-rating__val.list-rst__budget-val.cpy-dinner-budget-val')
        price_noon_soup = shop.select('div.list-rst__body > div.list-rst__contents > div.list-rst__rst-data > ul.list-rst__budget > li:nth-child(2) > span.c-rating__val.list-rst__budget-val.cpy-lunch-budget-val')

        name = name_soup[0].text
        rating = rating_soup[0].text if rating_soup else '-1'
        review = review_soup[0].text if review_soup else '0件'
        price_night = price_night_soup[0].text if price_night_soup else '-'
        price_noon = price_noon_soup[0].text if price_noon_soup else '-'

        def reformat_str(s):
            return str(s).lstrip().rstrip()

        name = reformat_str(name)
        try:
            rating = float(reformat_str(rating))
        except:
            rating = -1

        try:
            review = int(reformat_str(review).rstrip("件"))
        except:
            review = 0

        if price_night == '-':
            price_night = -1
        else:
            price_night = reformat_str(price_night)
            price_night = price_night.split(sep='～')
            price_night = price_night[-1].lstrip('￥')
            price_night = price_night.replace(',', '')
            try:
                price_night = int(price_night)
            except:
                price_night = -1

        if price_noon == '-':
            price_noon = -1
        else:
            price_noon = reformat_str(price_noon)
            price_noon = price_noon.split(sep='～')
            price_noon = price_noon[-1].lstrip('￥')
            price_noon = price_noon.replace(',', '')
            try:
                price_noon = int(price_noon)
            except:
                price_noon = -1

        info = TabelogInfo(name=name, rating=rating, reviews=review, price_night=price_night, price_noon=price_noon)
        info_list.append(info)

    return True, info_list


def collect_info_sapporo_all(total_pages, pools=4):
    def task_generator():
        return range(total_pages), total_pages

    tabelog_info_list = distribute_work(task_generator=task_generator,
                                        func_work=collect_info_sapporo,
                                        time_sleep=0.5,
                                        pools=pools)

    # Save to excel
    to_excel(convertible=tabelog_info_list, filename='tabelog_sapporo_201903231930.xlsx')
    print("Saved to excel")

