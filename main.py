from bs4 import BeautifulSoup
from util.functions import createUrlFromAsin, getAsins, getBriefInfo, getResponse, getAdditionalInfo, logger, getBasicInfo
from constants import maxPage, searchKeys, data_source_array
import numpy as np
import pandas as pd
import datetime

def main():
    startTime = datetime.datetime.now()
    masterDataDictList = []
    searchKeyIndex = 1
    for data_source in data_source_array:
        for searchKey in searchKeys:
            asins = []
            for page in range(1, maxPage + 1):
                asins += getAsins(searchKey, str(page), data_source=data_source)

            asins = np.unique(asins).tolist();
            logger("total unique asins: " + str(len(asins)))
            logger("")
            for asin in asins:
                if asin != "":
                    logger(f"(Keyword number {searchKeyIndex} out of {len(searchKeys) * len(data_source_array)}) {searchKey}")
                    url = createUrlFromAsin(asin, data_source)
                    productSoup = BeautifulSoup(getResponse(url, data_source).text, 'html.parser')
                    masterDataDict = {}
                    masterDataDict = getBasicInfo(productSoup) | {"category": searchKeys[searchKey], "dataSource": data_source} | getBriefInfo(productSoup) | getAdditionalInfo(productSoup) 
                    masterDataDictList.append(masterDataDict)
                    currentIndex = asins.index(asin)
                    progress = f"progress: {str(100 - (100 *((len(asins) - (currentIndex + 1)) / len(asins))))}%  (time lapsed: {datetime.datetime.now() - startTime})"
                    logger(progress)
                    logger("")
            searchKeyIndex += 1
    masterDataFrame = pd.DataFrame(masterDataDictList);
    masterDataFrame.to_csv('master_data.csv')
    endTime = datetime.datetime.now()
    difference = endTime - startTime
    logger(f"process took {difference} to complete")

main()
