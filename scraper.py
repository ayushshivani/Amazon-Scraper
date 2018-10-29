#!/usr/bin/env python
from lxml import html  
import csv,time,sys
import threading
import requests
from random import choice
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys


#get proxy list from txt file
def getProxyList():
  proxyList = []
  with open('./list.txt') as f:
    proxys = f.readlines()
  for i in proxys:
    if len(i) > 5:
      if i[:4] != 'http':
        proxyList.append('http://'+i.split('\n')[0])
      else:
        proxyList.append(i.split('\n')[0])
  proxyList = list(set(proxyList))
  return proxyList


proxy = getProxyList()


def AmzonParser(url):
    try:  
        rank = []
        BSR_name = []
        page = requests.get(url,headers = random_useragent(),proxies = {"http":"{}".format(choice(proxy))},timeout = 3)
        plain_text = page.text
        soup = BeautifulSoup(plain_text,"lxml")
        result_product = soup.findAll('div',{'id':'atfResults'})
        a_text = result_product[0]
        result_a = a_text.findAll('a',{'class':'a-link-normal s-access-detail-page  s-color-twister-title-link a-text-normal'})
        result_url = result_a[0].get('href')


        # print(choice(proxy))
        PROXY = choice(proxy)
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--proxy-server=%s' % PROXY)

        chrome = webdriver.Chrome(executable_path='./chromedriver')
        chrome.get(result_url)
        chrome.find_element_by_id("nav-global-location-slot").click()
        time.sleep(2)
        zipElement = chrome.find_element_by_id("GLUXZipUpdateInput")
        zipElement.send_keys('32818')
        time.sleep(1)
        zipElement.send_keys(Keys.ENTER);
        time.sleep(1)
        chrome.find_element_by_name('glowDoneButton').click()
        time.sleep(10)
        # print(chrome.page_source)
        detail_soup = BeautifulSoup(chrome.page_source,"lxml")
        # print(detail_soup)
        product_price = detail_soup.findAll('span',{'id':'price_inside_buybox'})
        price = product_price[0].text
        # print(price)
        
        prime_details = detail_soup.findAll('span',{'id':'price-shipping-message'})
        # print(prime_details)
        is_Prime = prime_details[0].find('i',{'class':'a-icon a-icon-prime'})

        product_table = detail_soup.findAll('table',{'id':'productDetails_detailBullets_sections1'})
        # print(product_table)
        rows = product_table[0].findAll('tr')
        # print(rows) 
        for row in rows:
            col = row.find('th')
            col_name = col.text.strip()
            # print(col_name.strip()) 
            if col_name == 'Shipping Weight':
                product_weight = row.find('td').text.strip()
                # print(product_weight)

            if col_name == 'Best Sellers Rank':
                product_BSR = row.find('td')
                # print(product_BSR)
                product_BSR_span = product_BSR.findAll('span')
                # print(product_BSR_span[0].text.strip())
                # print(product_BSR)
                for i in range(1):
                    for word in product_BSR_span[i].text.split():
                        # print(word)
                        if word[0] == '#':
                            rank.append(word)
                        elif word == 'in':
                            pass
                        else:
                            BSR_name.append(word)

        # print(rank)
        # print(BSR_name)

        nof_sellers = detail_soup.find('span',{'id':'mbc-upd-olp-link'})
        product_nof_sellers = nof_sellers.text.strip()
        product_nof_sellers = product_nof_sellers.split()
        product_nof_sellers = product_nof_sellers[1].replace('(','').replace(')','')
        # print(product_nof_sellers[1].replace('(','').replace(')',''))

        seller = detail_soup.find('div',{'id':'merchant-info'})
        seller_info  = seller.find('a').text.strip()
        print(seller_info)


 



    except requests.exceptions.RequestException as e:
        return AmzonParser(url)
    except:
        print ("Unexpected error:", sys.exc_info()[0])
        return AmzonParser(url)




#generate random user agent ,otherwise amazon will block you by this!
def random_useragent():
  UAS = []
  HEADERS = {
        'User-Agent': 'Mozilla/5.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'close',
        'DNT': '1'
      }
  #if you want more user agent ,just google and add !
  with open('./ua.txt') as f:
    ua = f.readlines()
    for i in ua:
      UAS.append(i.split('\n')[0])
  HEADERS['User-Agent'] = choice(UAS)
  return HEADERS


def main():
  #if you want it run more quickly ,please increase the range
  #spawn a pool of threads, and pass them queue instance
  url = "https://www.amazon.com/s?k=729220070227&ref=nb_sb_noss"
  for i in range(1):
    AmzonParser(url)

 
main()