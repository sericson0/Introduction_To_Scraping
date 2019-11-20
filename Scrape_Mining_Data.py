#We want to scrape some bitcoin mining data to save for later. 
#We go to the mining pool BTC.com https://pool.btc.com/
#At the bottom we see that they have an API. Horray!!!
#Reading the docs we see some of how to use the api https://docs.pool.btc.com/#/
# The link https://us-pool.api.btc.com/v1/pool/multi-coin-stats?dimension=1h gives a JSON file with current pool information
#We need to download this and save it in a usable format
#We also want to keep track of the price of bitcoin when we scrape, so we us the coindesk api

#This code sends requests to mining pool api data to get mining pool use data
#Import packages we use
import pandas as pd
import requests
import sys
import os
import datetime
import time
#############
#Where the relevant mining data will be saved
os.chdir(os.path.dirname(os.path.abspath(__file__))) #This little fancy line sets the working directory to wherever the file is saved
outputFolder = "../Bitcoin Data" 
if not os.path.exists(outputFolder): os.mkdir(outputFolder)
timeSeq = 60*5 #frequency of requests in seconds (60*5 = 5 minutes)

btc_api_url = "https://us-pool.api.btc.com/v1/pool/multi-coin-stats?dimension=1h"
coindesk_api_url = "https://api.coindesk.com/v1/bpi/currentprice.json"
#____________________________________________________________________________________________________________________________
#____________________________________________________________________________________________________________________________
#____________________________________________________________________________________________________________________________
#returns a string time
def getTime():
    currentTime = str(datetime.datetime.now().strftime("%Y%m%d%H%M%S"))
    return currentTime
##
def getBTCdata(url):
    #To download data from the internet we use the python package requests.
    #requests.get(url) gets data from a webpage
    #requests.get(url).text saves the text
    #requests.get(url).json() returns the json data as a list of lists. 
    json_data = requests.get(url).json()
    btcData = json_data["data"]["btc"]
#
    stats = btcData["stats"]
    return [stats["workers"], stats["users"], stats["shares"]["shares_1m"], stats["shares"]["shares_15m"], stats["shares"]["shares_1h"], stats["shares"]["shares_unit"]]


def getPriceData(url):
    priceData = requests.get(url).json()
    pricesUSD = priceData["bpi"]["USD"]["rate_float"]
    priceTime = priceData["time"]["updated"].replace(",", "")
    return {"pricesUSD":pricesUSD, "priceTime":priceTime}
##
def writeBTCdata(outputFolder, currentTime, prices, btc_url):
    try:
        btcData = getBTCdata(btc_url)
        with open(outputFolder + "/btc mining data_" + currentTime + ".txt", "w") as f:
            f.write("time, price, price_time, workers, users, hashrate_1m, hashrate_15m, hashrate_1h, unit \n")
            f.write("%s, %s, %s, %s, %s, %s, %s, %s, %s" %(currentTime, prices["pricesUSD"], prices["priceTime"], btcData[0], btcData[1], btcData[2], btcData[3], btcData[4], btcData[5]) )
    except:
        print("BTC data failed")

#This will result in a continuous scraper which pings every 5 minutes.
while True:
    currentTime = getTime()
    BTC_price = getPriceData(coindesk_api_url)
    writeBTCdata(outputFolder, currentTime, BTC_price, btc_api_url)
    time.sleep(timeSeq)


