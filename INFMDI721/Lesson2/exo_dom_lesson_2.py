import requests
from bs4 import BeautifulSoup
import json
website_search = "https://www.reuters.com/finance/stocks/lookup?searchType=any&comSortBy=marketcap&sortBy=&dateRange=&search="
#pages = requests.get(website_search+queries)
web_prefix = "https://www.reuters.com/finance/stocks/financial-highlights/"
queries = ["DANO.PA","AIR.PA","LVMH.PA"]


def _handle_request_result_and_build_soup(request_result):
    if request_result.status_code == 200:
        soup = BeautifulSoup(request_result.content,"html.parser")
    return soup

def get_share_registry(url):
    page = requests.get(url)
    soup = _handle_request_result_and_build_soup(page)
    all_names = []
    rows = soup.find('table').find_all('tr')
    rows = rows[1:]
    for row in rows:
        cols=row.find_all('td')
        cols=[x.text.strip() for x in cols]
        all_names.append(cols[1])
    return all_names

def get_sales_results_Q4_2018(url):
    try:
        page = requests.get(url)
        soup = _handle_request_result_and_build_soup(page)
        text_specific = "Quarter Ending\xa0Dec-18"
        #text_specific = re.compile(r"Quarter Ending")
        numSalesQ4_2018 = soup.find("td", text=text_specific).findNext("td").text
        meanSalesQ4_2018 = soup.find("td", text=text_specific).findNext("td").findNext("td").text
        return {"Q4 2018 number sales (millions)": _convert_string_to_int(numSalesQ4_2018),
            "Q4 2018 mean sales (millions)": _convert_string_to_int(meanSalesQ4_2018)}
    except AttributeError:
        return {"Q4 2018 number sales (millions)": _convert_string_to_int('error'),
                "Q4 2018 mean sales (millions)": _convert_string_to_int('error')}

def get_share_price_PA(url):
    try:
        page = requests.get(url)
        soup = _handle_request_result_and_build_soup(page)
        class_specific = "sectionQuoteDetail"
        sharePrice = soup.find("div",class_=class_specific).findNext("span").findNext("span").text.strip()
        return {"Share price": _convert_string_to_int(sharePrice)}
    except AttributeError:
        return {"Share price": _convert_string_to_int('error')}

def get_change_share_price_PA(url):
    try:
        page = requests.get(url)
        soup = _handle_request_result_and_build_soup(page)
        class_specific = "valueContentPercent"
        percentChange = soup.find("span",class_=class_specific).findNext("span").text.strip()[1:-2]
        return {"Share price change": _convert_string_to_int(percentChange)}
    except AttributeError:
        return {"Share price change": _convert_string_to_int('error')}

def get_dividend_yied_info(url):
    try:
        page = requests.get(url)
        soup = _handle_request_result_and_build_soup(page)
        text_specific ="Dividend Yield"
        divYieldCompany = soup.find("td",text=text_specific).findNext("td").text
        divYieldIndustry = soup.find("td",text=text_specific).findNext("td").findNext("td").text
        divYieldSector = soup.find("td",text=text_specific).findNext("td").findNext("td").findNext("td").text
        return {"Dividend yied company": _convert_string_to_int(divYieldCompany),
            "Dividend yied industry": _convert_string_to_int(divYieldIndustry),
            "Dividend yied sector": _convert_string_to_int(divYieldSector)}
    except AttributeError:
        return {"Dividend yied company": _convert_string_to_int('error'),
                "Dividend yied industry": _convert_string_to_int('error'),
                "Dividend yied sector": _convert_string_to_int('error')}

def get_percent_shares_owned_instutional_holders(url):
    try:
        page = requests.get(url)
        soup = _handle_request_result_and_build_soup(page)
        text_specific = "% Shares Owned:"
        percentSharesOwnded = soup.find("td",text=text_specific).findNext("td").text[:-1]
        return {"Percent shares ownded by institutional holders": _convert_string_to_int(percentSharesOwnded)}
    except AttributeError:
        return {"Percent shares ownded by institutional holders": _convert_string_to_int('error')}

def get_currency(url):
    try:
        page = requests.get(url)
        soup = _handle_request_result_and_build_soup(page)
        class_specific ="sectionQuoteDetail"
        currency = soup.find("div",class_=class_specific).findNext("span").findNext("span").findNext("span").text
        return currency
    except AttributeError:
        pass

def get_timeEDT(url):
    try:
        page = requests.get(url)
        soup = _handle_request_result_and_build_soup(page)
        class_specific = "nasdaqChangeTime"
        timeEDT = soup.find("span",class_=class_specific).text
        return timeEDT
    except AttributeError:
        pass

def _convert_string_to_int(string):
    try:
        if "," in string:
            return float(string.replace(',',''))
        elif "." in string:
            return float(string.strip())
        else:
            return int(string.strip())
    except ValueError:
        pass

def get_all_results(url):
    try:
        res = {**get_sales_results_Q4_2018(url),
               **get_share_price_PA(url),
               **get_change_share_price_PA(url),
               **get_dividend_yied_info(url),
               **get_percent_shares_owned_instutional_holders(url)}
        return res
    except TypeError:
        pass

def main():
    for query in queries:
        #url = website_search + query
        #all_links = get_share_registry(url)
        #for link in all_links:
        try:
            print(query + "(" + get_timeEDT(web_prefix + query) + ")"
                  + " - Currency: " + get_currency(web_prefix + query))
        except TypeError:
            print(query)
        print(json.dumps(get_all_results(web_prefix + query),indent=1))


if __name__ == '__main__':
    main()