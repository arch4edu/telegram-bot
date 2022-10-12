#!/bin/python3
from datetime import datetime, timedelta

import requests

url = "https://pkgstats.archlinux.de/api/packages/"
session = requests.session()


def search(package):
    # params = {"startMonth": 0, "endMonth": datetime.now().year * 100 + datetime.now().month}
    result = session.get(url + package).json()
    return result["count"], result["samples"]


if __name__ == "__main__":
    import sys

    count, samples = search(sys.argv[1])
    print("%d / %d = %.2f%%" % (count, samples, 100 * count / samples))
