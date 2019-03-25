from googleplaces.places import PlaceDetailURL, PlaceSearchURL, get_place, get_place_detail
from utils.excel import to_excel, from_excel
from utils.http import get_json


__API_KEY = None


def load_api_key(path):
    with open(path, mode='r') as f:
        global __API_KEY
        __API_KEY = f.read()


if __name__ == '__main__':
    load_api_key('../apikey')

    test_place = get_place(name="焼肉屋 かねちゃん 至粋亭", key=__API_KEY)
    test_place = get_place_detail(place=test_place, key=__API_KEY)
    print(test_place)
