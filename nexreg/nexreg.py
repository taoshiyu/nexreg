# coding=utf-8

import datetime
import time
from collections import deque

import matplotlib.pyplot as plt
import pymongo
import requests
from lxml import etree

url = 'https://apa.nexregreporting.com/Home/GetRequestedData?isin=&mic=&type=pre&currentDay=true&region=UK&pageIndex=1&pageSize=100'
url_ = 'https://apa.nexregreporting.com/Home/GetRequestedData?isin=&mic=&type=pre&currentDay=true&region=UK&pageIndex={}&pageSize={}'

headers = {
    'accept': 'text/html, */*; q=0.01',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'cache-control': 'no-cache',
    'cookie': '_ga=GA1.2.107827823.1565860863; _gid=GA1.2.981891061.1565860863; ASP.NET_SessionId=uo1h234nmhxvbz1iwprynp55',
    'referer': 'https://apa.nexregreporting.com/home/quotes',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.84 Safari/537.36',
    'x-requested-with': 'XMLHttpRequest',
}
thead = ['instrumentCode', 'quantity', 'searchTime', 'priceLevel', 'bidOfferStatus', 'price', 'priceNotation',
         'priceCurrency', 'venueExecution', 'publishTime']
mongo_client = pymongo.MongoClient(host='localhost', port=27017)
db = mongo_client['tradeWeb']

q1 = deque(maxlen=100)
q2 = deque(maxlen=100)
plt.ion()

start = datetime.datetime.now()
time_delta = datetime.timedelta(hours=6)
end = start + time_delta

now_point  =0
def search_and_plot():
    plt.figure(1)
    global now_point
    with requests.session() as s:
        s.headers = headers
        now_ = datetime.datetime.now()
        while now_ < end:
            now_str = now_.strftime('%m:%S')
            q1.append(now_str)
            try:
                r = s.get(url)
                r.raise_for_status()
            except Exception as e:
                print(e)
                continue
            print(r.status_code)
            tree = etree.HTML(r.text)
            trs = tree.xpath('//table[@id="apa-data"]/tbody/tr')
            # thd = tree.xpath('//table[@id="apa-data"]/thead/tr/th/text()')
            # thd = list(map((lambda x:x.strip()),thd))
            # assert thd == thead
            update_count = 0
            for tr in trs:
                td = tr.xpath('td/text()')
                doc = dict(zip(thead, td))
                del doc['searchTime']
                result = db['nexreg'].update_one(filter=doc, update={'$set': doc}, upsert=True)  # r.raise_for_status()
                if not result.matched_count:
                    update_count += 1
            q2.append(update_count)
            plt.plot(q1.copy(), q2.copy(), '-r')
            plt.pause(0.1)
            now_ = datetime.datetime.now()
        plt.savefig('figure-1.png')

def search():
    global now_point
    with requests.session() as s:
        s.headers = headers
        now_ = datetime.datetime.now()
        while now_ < end:
            now_str = now_.strftime('%m:%S')
            q1.append(now_str)
            try:
                r = s.get(url)
                r.raise_for_status()
            except Exception as e:
                print(e)
                continue
            print(r.status_code)
            tree = etree.HTML(r.text)
            trs = tree.xpath('//table[@id="apa-data"]/tbody/tr')
            update_count = 0
            for tr in trs:
                td = tr.xpath('td/text()')
                doc = dict(zip(thead, td))
                del doc['searchTime']
                result = db['nexreg'].update_one(filter=doc, update={'$set': doc}, upsert=True)  # r.raise_for_status()
                if not result.matched_count:
                    update_count += 1
            time.sleep(1)
            now_ = datetime.datetime.now()
        plt.savefig('figure-1.png')

def search_all():
    page_index = 1
    with requests.session() as s:
        s.headers = headers
        while True:
            url = url_.format(page_index,1000)
            r = s.get(url)
            if 'Access is temporarily' in r.text:
                break
            tree = etree.HTML(r.text)
            trs = tree.xpath('//table[@id="apa-data"]/tbody/tr')
            update_count = 0
            for tr in trs:
                td = tr.xpath('td/text()')
                doc = dict(zip(thead, td))
                del doc['searchTime']
                result = db['nexreg'].update_one(filter=doc, update={'$set': doc}, upsert=True)
                if not result.matched_count:
                    update_count += 1
            print(r.status_code,update_count)
            page_index+=1




def plot_():
    l1 = [1,2,1]
    l2 = [1,2,1]
    plt.plot(l1,l2,'-r')
    plt.pause(5)
if __name__ == '__main__':
    search_all()
