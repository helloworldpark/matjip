from utils.url import URL
from utils.http import get_html
from bs4 import BeautifulSoup


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


class TabelogInfo:

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


def collect_info_sapporo(page):
    url_sapporo = TabelogURL(ken='hokkaido', city='札幌市', page=page)
    print(url_sapporo.url())
    body, ok = get_html(url=url_sapporo.url())
    if not ok:
        print("Not OK")
        return False, page

    # start parsing
    soup = BeautifulSoup(body, features="html.parser")

    shops = soup.select(
        '#column-main > ul > li'
    )

    for shop in shops:
        print('---------')
        name_soup = shop.select('div.list-rst__header > div > div > div > a')
        if not name_soup:
            continue
        rating_soup = shop.select('div.list-rst__body > div.list-rst__contents > div.list-rst__rst-data > div.list-rst__rate > p.c-rating.c-rating--xl.c-rating--val30.list-rst__rating-total.cpy-total-score > span')
        review_soup = shop.select('div.list-rst__body > div.list-rst__contents > div.list-rst__rst-data > div.list-rst__rate > p.list-rst__rvw-count > a')
        price_night_soup = shop.select('div.list-rst__body > div.list-rst__contents > div.list-rst__rst-data > ul.list-rst__budget > li:nth-child(1) > span.c-rating__val.list-rst__budget-val.cpy-dinner-budget-val')
        price_noon_soup = shop.select('div.list-rst__body > div.list-rst__contents > div.list-rst__rst-data > ul.list-rst__budget > li:nth-child(2) > span.c-rating__val.list-rst__budget-val.cpy-lunch-budget-val')

        name = name_soup[0].text
        rating = rating_soup[0].text if rating_soup else '-'
        review = review_soup[0].text if review_soup else '0'
        price_night = price_night_soup[0].text if price_night_soup else '-'
        price_noon = price_noon_soup[0].text if price_noon_soup else '-'

        print("{:s}: {:s}({:s}), {:s} / {:s}".format(name, rating, review, price_night, price_noon))

    return True, page
