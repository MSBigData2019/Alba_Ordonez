import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
import re
import pyjq
from multiprocessing import Pool
import time

request_headers = {
    "Accept-Language": "en-US,en;q=0.5",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Referer": "http://thewebsite.com",
    "Connection": "keep-alive"
}

def _handle_request_result_and_build_soup(request_result):
    if request_result.status_code == 200:
        soup = BeautifulSoup(request_result.content,"html.parser")
    return soup

def get_add_links_for_regions(regions, prefix):
    for regionID in regions:
        p = 1
        while True:
            url = prefix + f"/listing?makesModelsCommercialNames=RENAULT%3AZOE&options=&page={p}&regions={regionID}"
            page = requests.get(url)
            soup = _handle_request_result_and_build_soup(page)
            elems = soup.select("a[class^=link]")
            if len(elems) != 0:
                print(p)
                for elem in elems:
                    link = elem.attrs['href']
                    links.append(prefix + link)
                    region_IDs.append(regionID)
            else:
                break
            p += 1
    return pd.DataFrame({"Link": links,
                         "region": region_IDs})

def get_url_argus(url):
    page = requests.get(url, headers = request_headers)
    soup = _handle_request_result_and_build_soup(page)
    i=0
    while True:
        tmp = soup.findAll("a", class_="btnGrey clearPhone txtLPhone")[i].attrs['href']
        if "fiche_cote" in tmp:
            url_argus = prefix + tmp
            break
        else:
            i +=1
    return url_argus

def get_rating_argus(url, reg_num):
    try:
        page_argus = requests.get(get_url_argus(url), headers = request_headers)
        soup_argus = _handle_request_result_and_build_soup(page_argus)
        argus_rating = ''.join(reg_num.findall(soup_argus.find("span", class_="jsRefinedQuotBrute").text))
        return argus_rating
    except AttributeError:
        return 0

def get_dataframe_zoe(url):
    global df_links

    df = pd.DataFrame({'Region':[],
                       'Version': [],
                       'Year': [],
                       'Mileage': [],
                       'Owner\'s phone': [],
                       'Price': [],
                       'Argus rating': [],
                       'Benefit Buyer': []})


    try:
        page = requests.get(url, headers = request_headers)
        soup = _handle_request_result_and_build_soup(page)
        reg_json = re.compile(r"xtMultC:(.*),")
        reg_num = re.compile(r"(\d+)")
        reg_phone = re.compile(r"[0-9 ]{2,}")

        json_tab = json.loads(str(reg_json.findall(page.text))[3:-2])

        version = str(pyjq.one(".\"16\"",json_tab))[1:-1]
        mileage = str(pyjq.one(".\"33\"",json_tab))[1:-1]
        mileage = str(reg_num.findall(mileage))[2:-2]
        year = str(pyjq.one(".\"36\"",json_tab))[1:-1]
        year = str(reg_num.findall(year))[2:-2]
        price = str(pyjq.one(".\"32\"",json_tab))[1:-1]
        price = int(str(reg_num.findall(price))[2:-2])
        phone = soup.find("div", class_="phoneNumber1").text
        phone = ''.join(reg_phone.findall(phone)).strip('  ')


        rating_argus = int(get_rating_argus(url, reg_num))

        if rating_argus > 0:
            diff_price = rating_argus - price
        else:
            diff_price = 0

        df = df.append({'Region': df_links.set_index("Link")['region'].loc[(url)],
                        'Version': version,
                        'Year': year,
                        'Mileage': mileage,
                        'Owner\'s phone': phone,
                        'Price': price,
                        'Argus rating': rating_argus,
                        'Benefit Buyer': diff_price}, ignore_index=True)
    except UnboundLocalError:
        pass
    return df


prefix = "https://www.lacentrale.fr"
regions = ["FR-IDF", "FR-PAC", "FR-NAQ"]
links = []
region_IDs = []

# df_links = get_add_links_for_regions(regions, prefix)
# df_links.to_pickle("Links_regions")
df_links = pd.read_pickle("Links_regions")

urls = df_links['Link'][:]


start = time.time()

i = 0

p = Pool(5)
df = pd.concat(p.map(get_dataframe_zoe, urls), ignore_index=True)
df = df.sort_values(by=['Benefit Buyer'], ascending=False)

end = time.time()


print("Execution time " + str(end-start) + "s")

df.to_csv("Dataframe_zoe.csv")
