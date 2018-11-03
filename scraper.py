#!/usr/bin/env python
from lxml import html
import csv
import time
import datetime
import sys
import threading
import requests
from random import choice
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import xlrd
import xlwt
import numpy


workbook = xlwt.Workbook(encoding="ascii")
# get proxy list from txt file


def getProxyList():
    proxyList = []
    with open('./list.txt') as f:
        proxys = f.readlines()
    for i in proxys:
        if len(i) > 5:
            if i[:4] != 'http':
                proxyList.append('http://' + i.split('\n')[0])
            else:
                proxyList.append(i.split('\n')[0])
    proxyList = list(set(proxyList))
    return proxyList


proxy = getProxyList()


def AmzonParser(url):
    product = []
    rank = []
    BSR_name = [[],[]]
    page = requests.get(
        url, headers=random_useragent(), proxies={
            "http": "{}".format(
                choice(proxy))}, timeout=3)
    plain_text = page.text
    soup = BeautifulSoup(plain_text, "lxml")
    # print(soup)
    result_product = soup.findAll('div', {'id': 'atfResults'})
    # print(result_product)
    if len(result_product) is not 0:
        a_text = result_product[0]
        result_a = a_text.findAll(
            'a', {
                'class': 'a-link-normal s-access-detail-page  s-color-twister-title-link a-text-normal'})
        if result_a is not None:
            result_url = result_a[0].get('href')
            # if result_url is not None:

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
            zipElement.send_keys(Keys.ENTER)
            time.sleep(1)
            chrome.find_element_by_name('glowDoneButton').click()
            time.sleep(1)
            # print(chrome.page_source)
            detail_soup = BeautifulSoup(chrome.page_source, "lxml")
            chrome.quit()

            # print(detail_soup)
            product_price = detail_soup.findAll(
                'span', {'id': 'price_inside_buybox'})

            # print(price)

            prime_details = detail_soup.findAll('a', {'id': 'SSOFpopoverLink'})
            if len(prime_details) != 0:
                if len(product_price) == 0:
                    product.append("NULL")
                else:
                    price = product_price[0].text.strip()
                    product.append(price)
                product.append(0)
                product.append(0)
            else:
                product.append(0)
                if len(product_price) == 0:
                    product.append("NULL")
                else:
                    price = product_price[0].text.strip()
                    product.append(price)
                product_shipping = detail_soup.find(
                    'div', {'id': 'desktop_qualifiedBuyBox'})
                if product_shipping is not None:
                    product_shipping = product_shipping.find(
                        'span', {'class': 'a-size-base a-color-secondary'})
                    if product_shipping is not None:
                        product_shipping = product_shipping.text.strip()
                        product.append(product_shipping)

            nof_sellers = detail_soup.find('span', {'id': 'mbc-upd-olp-link'})
            if nof_sellers is not None:
                product_nof_sellers = nof_sellers.text.strip()
                product_nof_sellers = product_nof_sellers.split()
                # print(product_nof_sellers[1])
                product_nof_sellers = product_nof_sellers[1].replace(
                    '(', '').replace(')', '')
                product.append(product_nof_sellers)
            else:
                product.append("NULL")
            # print(product_nof_sellers)

            product_table = detail_soup.findAll(
                'table', {'id': 'productDetails_detailBullets_sections1'})
            # print(product_table)
            if len(product_table) !=0:
                rows = product_table[0].findAll('tr')
                # print(rows)
                for row in rows:
                    col = row.find('th')
                    if col is not None:
                        col_name = col.text.strip()
                        # print(col_name.strip())
                        if col_name == 'Shipping Weight':
                            product_weight = row.find('td')
                            
                            if product_weight is not None :
                            	print("213")
                            	product_weight = product_weight.text.strip()
                            	product_weight = int(product_weight[0])
                            else:
                                product_weight = "Null"

                        if col_name == 'Best Sellers Rank':
                            product_BSR = row.find('td')
                            # print(product_BSR)
                            if product_BSR is not None:
                                product_BSR_span = product_BSR.findAll('span')
                                if len(product_BSR) != 0:
                                    for i in range(2):
                                    	# BSR_name[i] = []
                                    	for word in product_BSR_span[i].text.split():
                                            # print(word)
                                            if word[0] == '#':
                                                rank.append(word)
                                            elif word == 'in':
                                                pass
                                            else:
                                                BSR_name[i].append(word)
                                        

            # print(rank)
            # print(BSR_name)
            
            # print(BSR_name[0],BSR_name[1])
            # for i in range(len(BSR_name)):
            # 	if BSR_name[i] == "-1":
            # 		z = i 
            # 		break
            # 	else:
            # 		BSR_name1 += BSR_name1 + BSR_name[i]
            # for i in range(z,len(BSR_name)):
            # 	if BSR_name[i] == "-1":
            # 		break
            # 	else:
            # 		BSR_name2 += BSR_name2 + BSR_name[i]
            product.append(rank[0])
            product.append(BSR_name[0][0]+" "+BSR_name[0][1] + " " + BSR_name[0][2])  # name of BSR
            product.append(rank[1])
            product.append(BSR_name[1][0]+" "+BSR_name[1][1] + " " + BSR_name[1][2])  # name of BSR

            seller = detail_soup.find('div', {'id': 'merchant-info'})
            if seller is not None:
                seller_info = seller.find('a')
                if seller_info is not None:
                    seller_info = seller_info.text.strip()
                else:
                    seller_info = "Null"
            else:
                seller_info = "Null"
            # print(product_weight,seller_info)
            product.append(product_weight)
            product.append(seller_info)

    return product


# generate random user agent ,otherwise amazon will block you by this!
def random_useragent():
    UAS = []
    HEADERS = {
        'User-Agent': 'Mozilla/5.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'close',
        'DNT': '1'}
    # if you want more user agent ,just google and add !
    with open('./ua.txt') as f:
        ua = f.readlines()
        for i in ua:
            UAS.append(i.split('\n')[0])
    HEADERS['User-Agent'] = choice(UAS)
    return HEADERS


def main():

    url_part1 = "https://www.amazon.com/s?k="
    url_part2 = "&ref=nb_sb_noss"
    excel_file = 'Input.xlsx'

    """Testing"""
    # product_id = "074427857097"
    # product_url = url_part1 + str(product_id) + url_part2
    # #     	# print(product_url)
    # AmzonParser(product_url)

    data = xlrd.open_workbook('Input.xlsx')
    for sheetno in range(3):
        sheet = data.sheet_by_index(sheetno)
        worksheet = workbook.add_sheet('Mysheet')
        # print(sheet.nrows)
        for i in range(1, sheet.nrows):
            product = []
            product_id = sheet.cell(i, 0).value

            if isinstance(product_id, float):
                product_id = str(int(product_id))
            # print((product_id))

            while(len(product_id) < 13):
                product_id = '0' + product_id

            product_url = url_part1 + product_id + url_part2
            # print(product_url)
            product = AmzonParser(product_url)
            print(product, product_id)
            date = datetime.datetime.now()
            current_date = str(date.month) + "/" + str(date.day) + "/" + str(date.year - 2000)
            
            worksheet.write(i, 0, current_date)
            worksheet.write(i, 1, product_id)

            for j in range(2, 12):
                worksheet.write(i, j, product[j - 2])
           
        break
    
    workbook.save("Output.xlsx")


main()
