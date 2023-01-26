# -*- coding: utf-8 -*-
"""
Created on Thu Dec  8 17:33:21 2022

@author: fabio
"""

import requests
from bs4 import BeautifulSoup, SoupStrainer
import time
from datetime import datetime
import pandas as pd
import json
import ast

headers = {"User-Agent": "Mozilla/5.0 (W96indows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36",
    "Referer" : "www.google.com",
    "DNT" : "1"
    }

payload = ""

#https://www.continente.pt/sitemap_{N}-product.xml
#N = range(0,6) - 0 to 5

start_time = time.time()

# Selection of scraping sample

categories = ['mercearia', 'bio-e-escolhas-alimentares', 'laticinios-e-ovos', 
              'peixaria-e-talho', 'frutas-e-legumes', 'charcutaria-e-queijos',
              'padaria-e-pastelaria', 'congelados', 'bebidas-e-garrafeira', 
              'beleza-e-higiene/marcas', 'limpeza']

#--- Handling pagination/size of each page ---
n_pages = []

with requests.Session() as session:
    
    for each in categories:
    
        url = f'https://www.continente.pt/{each}/?pmin=0.01&start=0&sz=36'

        resp = session.get(url, data=payload, headers=headers)
        print(resp.status_code)
        
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        try:
            size = soup.find('div', {'class':'search-results-products-counter d-flex justify-content-center'}).get_text()
            n_pages.append(size[size.find('de')+2 : size.find('produtos')].strip())
            
        except AttributeError: #just in case, typically i dont have problems here
            print(f'There is an error with {url}')

#--- Scraping product data ---

#request = []
all_products = {}

#1) Saving request

#I think i have to add a control for the servers response
#Sometimes i dont get the whole html document:
    #subtraction of N till it reaches 1000 or less
with requests.Session() as session:
    for n, each in enumerate(categories):
        url = f'https://www.continente.pt/{each}/?pmin=0.01&start=0&sz={n_pages[n]}'
        #print(url)
        
        start_time_2 = time.time()

        resp = session.get(url, data=payload, headers=headers)
        #request.append(resp.text)
        
        print(f'----- {categories[n]}: requests took %s seconds -----' % (time.time() - start_time_2))

#2) Parsing the response
    
        start_time_3 = time.time()
        ids_list = []
        
        tag = SoupStrainer('div')
        soup = BeautifulSoup(resp.text, 'html.parser', parse_only=tag)
        
        for products in soup.find_all('div', {'class':'product'}):
            ids_list.append(products.attrs['data-pid'])
        
        for ids in ids_list:
            
            try:
                #products_data
                prod_data = soup.find('div',{'class':f'product-tile pid-{ids} ct-product-tile'})
                prod = prod_data.get('data-product-tile-impression')
                
                #products image and name
                prod_name = soup.find('div', {'class':'ct-image-container col-4 col-sm'})
                name = prod_name.get('data-confirmation-image')
                
                all_products[ids] = [name, prod]
                #print(f'At {ids}')
                
            except AttributeError:
                pass
                
        print(f'----- {categories[n]}: BS parsing took %s seconds -----' % (time.time() - start_time_3))

#--- Saving to json ---

#with open(r'C:\Users\fabio\OneDrive\Ambiente de Trabalho\Projetos python Economista\continente', 'w') as fp:
    #json.dump(all_products, fp)
        
#print("----- Continente: %s seconds -----" % (time.time() - start_time))


#Converting dictionary string to dictionary
#final_dict = {}   

for key in all_products.keys():
    test = []
    
    for elem in all_products[key]:
        string_dict = ast.literal_eval(elem)
        test.append(string_dict)
        
    all_products[key] = test


#IM HERE NOW, from now on i use final dict and not all_products
#all_products

prices = []
nomes = []
categories_table = []
#brand = []
for list_ in all_products.values():
    #print(len(list_[0]))
    prices.append(list_[1]['price'])
    categories_table.append(list_[1]['category'])
    #brand.append(list_[1]['brand'])
    nomes.append(list_[0]['title'])

chain = []
today = []
for n in range(len(all_products)):
    chain.append('Continente')
    today.append(datetime.today().strftime('%Y-%m-%d'))

table = {}
table['Supermercado'] = chain
table['Data_Upd'] = today
#table['Tipos'] = tipos
table['Categorias'] = categories_table
#table['Categorias_2'] = categorias_2
table['Produtos'] = nomes
table['Preços'] = prices

df = pd.DataFrame(table)
#df['Preços'] = df['Preços'].astype(float) -> ValueError: could not convert string to float: '1.398.00'
df.dropna(inplace = True)
#df['Data_Upd'] = df['Data_Upd'].dt.strftime('%Y-%m-%d')#dayfirst=True ,format=('%d-%m-%Y'))
print(df.info())

path = r'C:\Users\fabio\OneDrive\Ambiente de Trabalho\Projetos python Economista\continente.csv'
df.to_csv(path, sep ='\t', index= False)


'''
Web-Scraping lessons:
    1) find the page where all the products are listed with pagination, to minimize number of requests
    2) find attributes with dictionaries that have all the data

Total - +/- 10 mins
'''