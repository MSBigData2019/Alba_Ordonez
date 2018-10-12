import requests
from bs4 import BeautifulSoup
from statistics import mean
from multiprocessing import Pool
import time

web_prefix = "https://www.darty.com/"
web_prefix_research = "https://www.darty.com/nav/recherche/"

def _handle_request_result_and_build_soup(request_result):
    if request_result.status_code == 200:
        soup = BeautifulSoup(request_result.content,"html.parser")
    return soup

def _convert_string_to_float(string):
    if "%" in string:
        return float(string.replace('%','').replace('-','').strip())

def _convert_to_proper_url(name):
    return web_prefix_research + name + ".html"

def get_all_links_for_query(url):
    page = requests.get(url)
    soup = _handle_request_result_and_build_soup(page)
    specific_class = "prd-name"
    div_soup = soup.find_all("div",class_=specific_class)
    all_links = map(lambda i: div_soup[i].findNext('a')['href'], range(len(div_soup)))
    return all_links

def get_sold_value_for_page(url):
    page = requests.get(url)
    soup = _handle_request_result_and_build_soup(page)
    specific_class = "darty_prix_barre_remise darty_small separator_top"
    #sold_value = "0"
    if soup.find(class_=specific_class) != None:
        sold_value = soup.find("p", class_=specific_class).text
    else:
        sold_value = "0 %"
    return sold_value

def get_mean_sold_value_for_pages(name):
    url = _convert_to_proper_url(name)
    urls = get_all_links_for_query(url)
    res = []
    [res.append(_convert_string_to_float(get_sold_value_for_page(web_prefix + i))) for i in urls]
    res = filter(lambda v:v !=0, res)
    return "Mean of sale percentages for " + name + ": " + str(mean(res)) + "%"

#print(list(map(lambda name : get_mean_sold_value_for_pages(name) , ["dell","acer"])))

def f(name):
    return get_mean_sold_value_for_pages(name)

start = time.time()

if __name__ == '__main__':
    p = Pool(5)
    print(p.map(f, ["dell","acer"])) # Parallel
    #print(list(map(f, ["dell","acer"]))) # Sequential

end = time.time()
print("Exection time: " + str(end - start) + " s")