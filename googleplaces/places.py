from utils.url import URL
from utils.http import get_json


class PlaceSearchURL(URL):

    def __init__(self, name, key):
        self.name = name
        self.key = key

    def url(self):
        url = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json?"
        url += "key={:s}&input={:s}&inputtype=textquery".format(self.key, self.name)
        url += "&fields=name,place_id"
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


class Places:

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
    def reviews(self):
        return self._reviews

    @reviews.setter
    def reviews(self, value):
        self._reviews = value


class Review:

    def __init__(self, language, rating):
        self.language = language
        self.rating = rating

    def __repr__(self):
        return "Review lan: {:s} rating: {:d}".format(self.language, self.rating)


def get_place(name, key):
    result = get_json(PlaceSearchURL(name=name, key=key).url())
    if not result[1]:
        return None

    if result[0]['status'] != 'OK':
        return None

    candidates = result[0]['candidates']
    name_trimmed = str(name).replace(' ', '').strip(' ')
    for candidate in candidates:
        if str(candidate['name']).replace(' ', '').strip() == name_trimmed:
            return Places(name=name, place_id=candidate['place_id'])

    return None


def get_place_detail(place, key):
    if not place:
        return None

    response = get_json(PlaceDetailURL(name=place.name, place_id=place.place_id, key=key).url())
    if not response[1]:
        return None

    if response[0]['status'] != 'OK':
        return None

    result = response[0]['result']

    if not result:
        return None

    place.rating = result['rating']
    place.user_ratings_total = result['user_ratings_total']
    place.reviews = [Review(language=r['language'], rating=r['rating']) for r in result['reviews']]

    return place
