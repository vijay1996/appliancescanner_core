import re
import requests
from bs4 import BeautifulSoup
import numpy as np
from constants import headers
import datetime
import threading

def logText(log):
    print(log)

def writeLogFile(log):
    file = open(f"log-{str(datetime.date.today())}-latest.txt","a")
    file.write(f"[{str(datetime.date.today())}] {log}\n")
    file.close()


def logger(log):
    formattedLog = f"[{str(datetime.datetime.now())}] {log}"
    t1 = threading.Thread(target=logText, args=(formattedLog,))
    t2 = threading.Thread(target=writeLogFile, args=(formattedLog,))

    t1.start()
    t2.start()

    t1.join()
    t2.join()

def searchUrl(data_source):
     return f"https://www.amazon.{data_source}/s?k="

def createUrlFromAsin(asin, data_source):
    return f"http://www.amazon.{data_source}/dp/product/{asin}/"

def getResponse(url):
    session = requests.Session()
    session.trust_env = False
    response = session.get(url, headers=headers, timeout= 10, allow_redirects=True)
    logger(url + " -> status: " + str(response.status_code))
    return response

def getAsins(searchKey, page, data_source):
    asins = []
    callUrl = searchUrl(data_source=data_source) + searchKey + "&page=" + page
    soup = BeautifulSoup(getResponse(callUrl).content, "html.parser")
    links = soup.find_all("div", {"data-asin" : re.compile(r".*")})
    for link in links:
        asins.append(link['data-asin'])
    logger(f"Extracted {len(asins)} asins")
    return asins

def getAdditionalInfo(soup):
    
    product_info = {}
    # Extract technical information table
    try:
        technical_info_table = soup.find('table', {'id': 'productDetails_techSpec_section_1'})
    except Exception as e:
        logger("could not find productDetails_techSpec_section_1")
        logger(str(e))
    if technical_info_table:
        try:
            for row in technical_info_table.find_all('tr'):
                cells = row.find_all('th')
                if len(cells) == 1:
                    key = cells[0].text.strip().lower()
                cells = row.find_all('td')
                if len(cells) == 1:
                    value = cells[0].text.strip()
                product_info[key] = value.encode('ascii', 'ignore').decode('utf-8')
        except Exception as e:
            logger("could not find rows in productDetails_techSpec_section_1")
            logger(str(e))
    
    # Extract additional information table
    try:
        additional_info_table = soup.find('table', {'id': 'productDetails_detailBullets_sections1'})
    except Exception as e:
        logger("could not find productDetails_detailBullets_sections1")
        logger(str(e))

    if additional_info_table:
        try:
            for row in additional_info_table.find_all('tr'):
                cells = row.find_all('th')
                if len(cells) == 1:
                    key = formatDictValues(cells[0].text).lower()
                cells = row.find_all('td')
                if len(cells) == 1:
                    value = formatDictValues(cells[0].text)
                product_info[key] = value
        except:
            logger("could not find rows in productDetails_detailBullets_sections1")

    return product_info

def getBriefInfo(soup):
    briefInfo = {}
    try:
        briefInfoDiv = soup.find('div', {'id': 'productOverview_feature_div'})
    except Exception as e:
        logger("could not find productOverview_feature_div")
        logger(str(e))
    
    try:
        briefInfoTable = briefInfoDiv.find('table')
    except Exception as e:
        logger("could not find table inside productOverview_feature_div")
        logger(str(e))
        briefInfoTable = None

    if briefInfoTable:
        try:
            for row in briefInfoTable.find_all('tr'):
                try:
                    cells = row.find_all('td')
                    key = formatDictValues(cells[0].find('span').text).lower()
                    value = formatDictValues(cells[1].find('span').text)
                    briefInfo[key] = value
                except Exception as e:
                    logger("could not find rows inside productOverview_feature_div")
                    logger(str(e))
        except Exception as e:
            logger("could not find rows in productOverview_feature_div")
            logger(str(e))
    return briefInfo

def quickInfoGet(soup, tag, attributeDict):
    try:
        return soup.find(tag, attributeDict)
    except Exception as e:
        logger(f"could not find attribute - {str(attributeDict)}")
        logger(str(e))
        return None

def formatDictValues(value):
    return value.strip().replace("\n","").encode('ascii', 'ignore').decode('utf-8')

def getBasicInfo(soup):
    basicInfo = {}
    try:
        name = formatDictValues(quickInfoGet(soup, "span", {"id": "productTitle"}).text)
    except:
        name = ""
    try:
        price = formatDictValues(quickInfoGet(soup, "span", {"class": "a-price-whole"}).text)
    except:
        price=""
    try:
        imageUrl = quickInfoGet(soup, "img", {"alt": name, "src": re.compile(r".*"), "class": "a-lazy-loaded", "data-src": re.compile(r".*")})['data-src']
    except:
        imageUrl = ""
    basicInfo["product name"] = name
    basicInfo["price"] = price
    basicInfo["image url"] = imageUrl
    return basicInfo