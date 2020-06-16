#import bibliotek
import requests
from bs4 import BeautifulSoup
import pprint
import json

#funkcja do ekstrakcji składowyc opinii
def extract_feature(opinion,selector,attribute=None):
    try:
        if attribute:
            return opinion.select(selector).pop()[attribute].strip()
        else:
            return opinion.select(selector).pop().text.strip()
    except IndexError:
        return None

#słownik z atrybutami opinii i ich selektorami
selectors = {
    "author":["div.reviewer-name-line"],
    "recommendation":["div.product-review-summary > em"],
    "stars":["span.review-score-count"],
    "content":["p.product-review-body"],
    "cons":["div.cons-cell > ul"],
    "pros":["div.pros-cell > ul"],
    "useful":["button.vote-yes > span"],
    "useless":["button.vote-no > span"],
    "opinion_date":["span.review-time > time:nth-child(1)", "datetime"],
    "purchase_date":["span.review-time > time:nth-child(2)", "datetime"]
}

#adres url pierwszej strony z opiniami o produkcie
url_prefix = "https://www.ceneo.pl"
product_id = input("Podaj identyfikator produktu: ")
url_postfix = "#tab=reviews"
url = url_prefix+"/"+product_id+url_postfix

#pusta lista na opinie konsumentów 
all_opinions = []

while url:
    #pobranie kodu pojedynczej strony z opiniami o produkcie
    respons = requests.get(url)
    page_dom = BeautifulSoup(respons.text, "html.parser")

    #wydobycie z kodu strony fragmentów odpowiadających opiom konsumentów
    opinions = page_dom.select("li.js_product-review")

    #dla wszystkich opinii z danej strony wydobycie ich składowych
    for opinion in opinions:
        features = {key:extract_feature(opinion, *args)
                    for key, args in selectors.items()}
        features["opinion_id"] = int(opinion["data-entry-id"])
        features["useful"] = int(features["useful"])
        features["useless"] = int(features["useless"])   
        features["stars"] =  float(features["stars"].split("/")[0].replace(",", "."))
        features["content"] = features["content"].replace("\n", " ").replace("\r", " ")
        try:
            features["pros"] = features["pros"].replace("\n", ", ").replace("\r", ", ")
        except AttributeError:
            pass
        try:
            features["cons"] = features["cons"].replace("\n", ", ").replace("\r", ", ")
        except AttributeError:
            pass    
        all_opinions.append(features)
    try:
        url = url_prefix+page_dom.select("a.pagination__next").pop()["href"]
    except IndexError:
        url = None
    print(len(all_opinions))
    print(url)

with open("opinions_json/"+product_id+".json", "w", encoding="UTF-8") as fp:
    json.dump(all_opinions, fp, indent=4, ensure_ascii=False)

# pprint.pprint(all_opinions)