#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 11 12:18:35 2022

@author: tramle
"""



from bs4 import BeautifulSoup
import requests
import time
import numpy as np
import re
import pymongo
import json

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["mydb"]
mycol = mydb["hotels_prices"]
headers= {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36 Edg/88.0.705.56'}



## Get the rest of pages and update info
for i in np.arange(2,15,1):
    file= open("trip_advisor_search_pg" + str(i) + ".htm")
    content = file.read()
    soup = BeautifulSoup(content, 'html.parser')
    divs = soup.find_all("div",{'class':'listing_title'})
    
    for div in divs:
        hotel_name = div.a.text
        href = div.a.get('href')
        
        hotel_keys = re.findall('g[0-9]*-d[0-9]*',str(href))[0]
        try:
            url = 'https://data.xotelo.com/api/rates?hotel_key='+ str(hotel_keys) + '&chk_in=2022-05-28&chk_out=2022-05-30'
            print(url)
            res = requests.get(url)
            time.sleep(1)
            doc = BeautifulSoup(res.content, 'html.parser')
            time.sleep(1)
            json_object = json.loads(str(doc)) 
            
            hotel_url = json_object['result']['hotel_url'][0]
            print(hotel_url)
            
            try: 
                rates_expedia = [rate for rate in json_object['result']['rates'] if rate['name'] == 'Expedia']
                price_expedia = rates_expedia[0]['rate']
            except: 
                price_expedia = None
            print(price_expedia)
            
            try: 
                rates_bookings = [rate for rate in json_object['result']['rates'] if rate['name'] == 'Booking.com']
                price_bookings = rates_expedia[0]['rate']
            except: price_bookings = None
            print(price_bookings)
            
            try: 
                rates_hotel_com = [rate for rate in json_object['result']['rates'] if rate['name'] == 'Hotels.com']
                price_hotel_com = rates_hotel_com[0]['rate']
            except: price_bookings = None
            print(price_hotel_com)
            try: 
                rates_agoda_com = [rate for rate in json_object['result']['rates'] if rate['name'] == 'Agoda.com']
                price_agoda_com = rates_agoda_com[0]['rate']
            except: price_agoda_com = None
            print(price_agoda_com)
            
           
        except:
            url = 'https://www.tripadvisor.com/Hotel_Review-' + str(hotel_keys)
        
            res = requests.get(url, headers = headers)
            time.sleep(3)
            tripadvisor = BeautifulSoup(res.content, 'html.parser')
                
            try:
                expedia = tripadvisor.find("img",{'alt':'Expedia.com'}).parent.nextSibling
                price_expedia = expedia.find('div',{'class':'vyNCd b Wi'}).text
            except: 
                try: 
                    expedia = tripadvisor.find("img",{'alt':'Expedia.com'}).parent.nextSibling
                    price_expedia = expedia.find('div',{'data-sizegroup':'hr_chevron_prices'}).text
                except: price_expedia = None
            print("ex:",price_expedia)
    
            try:
                    booking = tripadvisor.find("img",{'alt':'Booking.com'}).parent.nextSibling
                    price_bookings = booking.find('div',{'class':'vyNCd b Wi'}).text
            except: 
                try:
                    booking = tripadvisor.find("img",{'alt':'Booking.com'}).parent.nextSibling
                    price_bookings = booking.find('div',{'data-sizegroup':'hr_chevron_prices'}).text
                except: price_bookings = None
            
            
            print(price_bookings)
            try:
                    hotel = tripadvisor.find("img",{'alt':'Booking.com'}).parent.nextSibling
                    price_hotel_com = hotel.find('div',{'class':'vyNCd b Wi'}).text
            except: 
                try:
                    hotel = tripadvisor.find("img",{'alt':'Booking.com'}).parent.nextSibling
                    price_hotel_com = hotel.find('div',{'data-sizegroup':'hr_chevron_prices'}).text
                except: price_hotel_com = None
           
            
           
            print(price_hotel_com)
        
        
        
            try:
                    agoda = tripadvisor.find("img",{'alt':'Agoda.com'}).parent.nextSibling
                    price_agoda_com = agoda.find('div',{'class':'vyNCd b Wi'}).text
            except:
                try:
                    agoda = tripadvisor.find("img",{'alt':'Agoda.com'}).parent.nextSibling
                    price_agoda_com = agoda.find('div',{'data-sizegroup':'hr_chevron_prices'}).text
                    
                    
                except: price_agoda_com = None
                
                
            print(price_agoda_com)
            hotel_url = url
                
            

        dict = {'Hotel Name': hotel_name,'Expedia Rate':price_expedia, 'Bookings.com Rate':price_bookings, 'Hotels.com Rate':price_hotel_com,
                'Agoda.com Rate':price_agoda_com, 'Hotel URL':hotel_url }
        try:
            mydb.hotels_prices_2.insert_one(dict)
        except: continue
        time.sleep(3)
        
        


docs = list(mycol.find({"Address": {"$exists": True}},{"_id": 1,"Hotel URL":1}))
print(docs)
i = 1


for doc in docs:
    url = doc['Hotel URL']
    obid = doc['_id']
    
    print(i)
    res = requests.get(url, headers = headers)
    soup = BeautifulSoup(res.content, 'html.parser')
    city = re.compile(r'San Francisco, CA')
    address = soup.find("span", text = city).text
    print(address)
    
    try: 
        phone = soup.find("span",{'class':'eeFQx ceIOZ yYjkv'}).text
        print(phone)
    except: phone = str("")
    
    try:
        reviews = soup.find("span",{'class':'btQSs q Wi z Wc'}).text
        print(reviews)
    except: reviews = str("0 reviews")
    
    
    try:
        pattern = re.compile(r'for walkers')
        walkingscore = soup.find("span",text=pattern).parent.previousSibling.text
        print(walkingscore)
    except: 
        try:
            pattern = re.compile(r'Somewhat walkable')
            walkingscore = soup.find("span",text=pattern).parent.previousSibling.text
        except: walkingscore = str("No Score Available")
    try:
        pattern2 = re.compile(r'Restaurants')
        restaurantscore = soup.find("span",text=pattern2).parent.previousSibling.text
        print(restaurantscore)
    except: restaurantscore =  str("No Score Available")
    
    try:
        pattern3 = re.compile(r'Attractions')
        attractionscore = soup.find("span",text=pattern3).parent.previousSibling.text
        print(attractionscore)
    except: attractionscore =  str("No Score Available")
    
    
    mydb.hotels_prices.find_one_and_update({'_id': obid}, {"$set":{'Address':address}})
    mydb.hotels_prices.find_one_and_update({'_id': obid}, {"$set":{'Phone':phone}})
    mydb.hotels_prices.find_one_and_update({'_id': obid}, {"$set":{'Number of Review':reviews}})
    mydb.hotels_prices.find_one_and_update({'_id': obid}, {"$set":{'Great for walkers Score':walkingscore}})
    mydb.hotels_prices.find_one_and_update({'_id': obid}, {"$set":{'Restaurant Score':restaurantscore}})
    mydb.hotels_prices.find_one_and_update({'_id': obid}, {"$set":{'Attractions Score':attractionscore}})

    time.sleep(3)
    i = i + 1     
        
        