from googleplaces.places import collect_from_google


__API_KEY = None


def load_api_key(path):
    with open(path, mode='r') as f:
        global __API_KEY
        __API_KEY = f.read()


if __name__ == '__main__':
    # Load API Key
    load_api_key('../apikey')

    # Collect data
    collect_from_google(tabelog_path="../tabelog/tmp/tabelog_sapporo_201903231930.xlsx", key=__API_KEY)
