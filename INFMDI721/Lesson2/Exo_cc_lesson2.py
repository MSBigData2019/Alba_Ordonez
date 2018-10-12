import requests
from bs4 import BeautifulSoup
import json
import scrapy


def _handle_request_result_and_build_soup(request_result):
    if request_result.status_code == 200:
        soup = BeautifulSoup(request_result.content,"html.parser")
    return soup

def _convert_string_to_int(string):
        if "%" in string:
            return float(string.replace('%','').replace('-','').strip())*-1

webs = {"https://www.darty.com/nav/recherche/dell.html": "Dell",
        "https://www.darty.com/nav/recherche/acer.html": "Acer"}

for web in webs.keys():
    page = requests.get(web)
    soup = _handle_request_result_and_build_soup(page)

    rows = soup.find_all("div",class_="prd-name")

    all_names = []
    for row in rows:
        cols=row.findNext('a')['href']
        all_names.append(cols)

    totSold = []
    for url_name in all_names:
        webr = "https://www.darty.com/" + url_name
        page = requests.get(webr)
        soup = _handle_request_result_and_build_soup(page)
        n = 0
        if soup.find(class_="darty_prix_barre_remise darty_small separator_top") != None:
            res = soup.find("p", class_="darty_prix_barre_remise darty_small separator_top").text
            totSold.append(_convert_string_to_int(res))

    print(webs.get(web) + " total percentage of sold:" + str(sum(totSold)/len(totSold)))
