import time
import requests

def test(url):
    t = requests.get(url)
    return len(t.text)
