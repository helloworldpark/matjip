from utils.url import URL
from utils.http import get_json
from utils.excel import from_excel, to_excel, ExcelConvertible
from typing import List
from functools import reduce
from utils.pool import distribute_work


class PlaceSearchURL(URL):

    def __init__(self, name, key):
        self.name = name
        self.key = key

    def url(self):
        url = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json?"
        url += "key={:s}&input={:s}&inputtype=textquery".format(self.key, self.name)
        url += "&fields=name,place_id&locationbias=point:43.075680,141.349305"
        return url


class PlaceDetailURL(URL):

    def __init__(self, name, place_id, key):
        self.name = name
        self.place_id = place_id
        self.key = key

    def url(self):
        url = "https://maps.googleapis.com/maps/api/place/details/json?"
        url += "key={:s}&place_id={:s}".format(self.key, self.place_id)
        url += "&fields=name,place_id,user_ratings_total,rating,review"
        return url


class Review:
    language: str
    rating: int

    def __init__(self, language, rating):
        """

        :param language:
        :param rating:
        """
        self.language = language
        self.rating = rating

    def __repr__(self):
        return "Review lan: {:s} rating: {:d}".format(self.language, self.rating)


class Places:

    name: str
    place_id: str
    _user_ratings_total: int
    _rating: int
    _reviews: List[Review]

    def __init__(self, name, place_id):
        self.name = name
        self.place_id = place_id
        self._user_ratings_total = -1
        self._rating = -1
        self._reviews = []

    def __repr__(self):
        return "Places name: {:s} id: {:s} user ratings total: {:d} rating: {:.2f} reviews: {}".format(
            self.name, self.place_id, self._user_ratings_total, self._rating, self._reviews
        )

    @property
    def user_ratings_total(self):
        return self._user_ratings_total

    @user_ratings_total.setter
    def user_ratings_total(self, value):
        self._user_ratings_total = value

    @property
    def rating(self):
        return self._rating

    @rating.setter
    def rating(self, value):
        self._rating = value

    @property
    def reviews(self) -> List[Review]:
        return self._reviews

    @reviews.setter
    def reviews(self, value: List[Review]):
        self._reviews = value


class GoogleInfo(ExcelConvertible):

    def __init__(self, name, rating, reviews, price_night, price_noon,
                 google_place_id, google_rating, google_user_ratings_total, google_review_en):
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
        :param google_place_id:
        :type google_place_id: str
        :param google_rating:
        :type google_rating: float
        :param google_user_ratings_total:
        :type google_user_ratings_total: int
        :param google_review_en:
        :type google_review_en: int
        """
        self.name = name
        self.rating = rating
        self.reviews = reviews
        self.price_night = price_night
        self.price_noon = price_noon
        self.google_place_id = google_place_id
        self.google_rating = google_rating
        self.google_user_ratings_total = google_user_ratings_total
        self.google_review_en = google_review_en

    def column_names(self):
        return ['name', 'rating', 'reviews', 'price_night', 'price_noon',
                'google_place_id', 'google_rating', 'google_user_ratings_total',
                'google_review_en']


def get_place(name, key):
    response = get_json(PlaceSearchURL(name=name, key=key).url())
    if not response[1]:
        return None, False

    if response[0]['status'] != 'OK':
        return None, False

    candidates = response[0]['candidates']

    if len(candidates) == 1:
        return Places(name=candidates[0]['name'], place_id=candidates[0]['place_id']), True

    name_trimmed = str(name).replace(' ', '').strip(' ')
    for candidate in candidates:
        if str(candidate['name']).replace(' ', '').strip() == name_trimmed:
            return Places(name=name, place_id=candidate['place_id']), True

    return None, True


def get_place_detail(place, key):
    if not place:
        return None, False

    response = get_json(PlaceDetailURL(name=place.name, place_id=place.place_id, key=key).url())
    if not response[1]:
        return None, False

    if response[0]['status'] != 'OK':
        return None, False

    result = response[0]['result']

    if not result:
        return None, True

    place.rating = result.get('rating', -1)
    place.user_ratings_total = result.get('user_ratings_total', 0)
    place.reviews = [Review(language=r.get('language', ''), rating=r.get('rating', -1)) for r in result.get('reviews', [])]

    return place, True


def collect_from_google(tabelog_path, key):

    # Load Tabelog
    tabelog = from_excel(file_path=tabelog_path)

    # Define task
    def task_generator():
        return range(tabelog.shape[0])

    # Define work: update dataframe
    def work(idx):
        place, status = get_place(name=tabelog.loc[idx, 'name'], key=key)
        if not status:
            return False, None
        if not place:
            return True, None

        place, status = get_place_detail(place=place, key=key)
        if place:
            google = GoogleInfo(name=tabelog.loc[idx, 'name'],
                                rating=tabelog.loc[idx, 'rating'],
                                reviews=tabelog.loc[idx, 'reviews'],
                                price_noon=tabelog.loc[idx, 'price_noon'],
                                price_night=tabelog.loc[idx, 'price_night'],
                                google_rating=place.rating,
                                google_place_id=place.place_id,
                                google_user_ratings_total=place.user_ratings_total,
                                google_review_en=reduce(lambda v, x: v + (1 if x.language == "en" else 0),
                                                        place.reviews, 0))
            return status, google
        return status, None

    # Pool API calls
    google_list = distribute_work(task_generator=task_generator, func_work=work, time_sleep=0.3)

    # Save to excel file
    to_excel(google_list, filename='google_tabelog_sapporo.xlsx')
