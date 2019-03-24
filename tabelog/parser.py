from utils.url import URL
from utils.http import get_html
from utils.excel import ExcelConvertible, to_excel
from bs4 import BeautifulSoup
from time import sleep
import re
from multiprocessing import Process, Queue


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
            review = reformat_str(review).rstrip("件")
            review = int(review)
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


def create_task(pages):
    return range(pages)


def collect_worker(task, done):
    for page in iter(task.get, 'STOP'):
        ok, info = collect_info_sapporo(page=page)
        done.put((info, page))
        if ok:
            print("OK   {}".format(page))
        else:
            print("FAIL {}".format(page))

        sleep(2)


def collect_info_sapporo_all(total_pages, pools=4):

    # https://docs.python.org/ko/3/library/multiprocessing.html#multiprocessing-examples

    # Distribute pages to crawl
    tasks = create_task(total_pages)

    # Create queues
    queue_task = Queue()
    queue_done = Queue()

    # Submit tasks
    for task in tasks:
        queue_task.put(task)

    # Start worker process
    for _ in range(pools):
        Process(target=collect_worker, args=(queue_task, queue_done)).start()

    print("Started!")

    # Collect unordered results
    tabelog_info_list = []
    success_once = set()
    failed_once = set()
    while len(success_once) + len(failed_once) != total_pages or not queue_task.empty():
        try:
            result = queue_done.get()
        except:
            continue

        if result[0]:
            success_once.add(result[1])
            for i in result[0]:
                tabelog_info_list.append(i)
        else:
            if result[1] not in failed_once:
                failed_once.add(result[1])
                queue_task.put(result[1])

    # Stop
    for _ in range(pools):
        queue_task.put('STOP')

    for page_fail in failed_once:
        print("Failed {}".format(page_fail))

    print("Stopped all")

    # Save to excel
    to_excel(convertible=tabelog_info_list, filename='tabelog_sapporo_201903231930.xlsx')
    print("Saved to excel")

