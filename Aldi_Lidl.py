# -*- coding: utf-8 -*-
"""
Created on Mon Dec 26 10:15:49 2022

@author: fabio
"""
import requests
from bs4 import BeautifulSoup , SoupStrainer
import time
import json
from datetime import datetime
import pandas as pd

headers = {
    "User-Agent": "Mozilla/5.0 (W96indows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36",
    "Referer" : "www.google.com",
    "DNT" : "1"
    }

payload = ""

#Aldi - class mod mod-article-intro ... get(data-article)
start_time_aldi = time.time()
products_aldi = {}
response_text = []

with requests.Session() as session:
    
    #for some reason the request is null
    aldi = session.get('https://www.aldi.pt/.aldi-nord-sitemap-pages.xml', data=payload, headers=headers)
    print(aldi.status_code)
    soup = BeautifulSoup(aldi.text, 'html.parser')
    
    for loc in soup.find_all('loc'):
        url_aldi = loc.get_text()
        
        if '/produtos/' in url_aldi:
            
            r_aldi = session.get(url_aldi, data=payload, headers=headers)
            response_text.append(r_aldi.text)

            try:
                tag = SoupStrainer('div')
                bs = BeautifulSoup(r_aldi.text, 'html.parser', parse_only=tag)
                
                products_data = bs.find('div', {'data-t-name':'ArticleIntro'})
                
                products_aldi[url_aldi] = products_data.get('data-article')
            
            except AttributeError:
                pass

print('----- Aldi: requests and parsing took %s seconds -----' % (time.time() - start_time_aldi))

#Alternative way to ast to transforme dictionary strings into actual strings
for keys, values in products_aldi.items():
    json_acceptable_string = values.replace("'", "\"")
    products_aldi[keys] = json.loads(json_acceptable_string)

prices = []
nomes = []
categories = []
#link = []
#brand = []
for dict_ in products_aldi.values():
    prices.append(dict_['productInfo']['priceWithTax'])
    nomes.append(dict_['productInfo']['productName'])
    categories.append(dict_['productCategory']['primaryCategory'])
    #link.append(dict_['id'])

chain = []
today = []
for n in range(len(products_aldi)):
    chain.append('Aldi')
    today.append(datetime.today().strftime('%Y-%m-%d'))

table = {}
table['Supermercado'] = chain
table['Data_Upd'] = today
#table['Tipos'] = tipos
table['Categoria'] = categories
#table['link'] = link
#table['Categorias_2'] = categorias_2
table['Produtos'] = nomes
table['Preços'] = prices

df = pd.DataFrame(table)
#df['Preços'] = df['Preços'].astype(float) -> ValueError: could not convert string to float: '1.398.00'
df.dropna(inplace = True)
#df['Data_Upd'] = df['Data_Upd'].dt.strftime('%Y-%m-%d')#dayfirst=True ,format=('%d-%m-%Y'))
print(df.info())

path = r'C:\Users\fabio\OneDrive\Ambiente de Trabalho\Projetos python Economista\aldi.csv'
df.to_csv(path, sep ='\t', index= False)


#-----LIDL-----

start_time_lidl = time.time()
products_lidl = {}


with requests.Session() as session:

    lidl = session.get('https://www.lidl.pt/sitemap.xml', data=payload, headers=headers)

    soup = BeautifulSoup(lidl.text, 'html.parser')
    
    for loc in soup.find_all('loc'):
        url_lidl = loc.get_text()
        
        if '/p/' in url_lidl:
            
            r_lidl = session.get(url_lidl, data=payload, headers=headers)
            
            try:
                tag = SoupStrainer('div')
                bs = BeautifulSoup(r_lidl.text, 'html.parser', parse_only=tag)
                
                products_data_2 = bs.find('div', {'data-controller':'productbox/right'})
                
                products_lidl[url_lidl] = products_data_2.div.attrs
            
            except AttributeError:
                pass

print('----- Lidl: requests and parsing took %s seconds -----' % (time.time() - start_time_lidl))
            
#Lidl - div {data-controller - productbox/right}... para o próximo div get all the attributes

prices_lidl = []
nomes_lidl = []
categories_lidl = []
link_lidl = []
#brand = []
for keys, dict_ in products_lidl.items():
    prices_lidl.append(dict_['data-price'])
    nomes_lidl.append(dict_['data-name'])
    categories_lidl.append(dict_['data-list'])
    link_lidl.append(keys)

chain_lidl = []
today_lidl = []
for n in range(len(products_lidl)):
    chain_lidl.append('Lidl')
    today_lidl.append(datetime.today().strftime('%Y-%m-%d'))

table_lidl = {}
table_lidl['Supermercado'] = chain_lidl
table_lidl['Data_Upd'] = today_lidl
#table['Tipos'] = tipos
table_lidl['Categoria'] = categories_lidl
table_lidl['link'] = link_lidl
#table['Categorias_2'] = categorias_2
table_lidl['Produtos'] = nomes_lidl
table_lidl['Preços'] = prices_lidl

df_lidl = pd.DataFrame(table_lidl)
#df['Preços'] = df['Preços'].astype(float) -> ValueError: could not convert string to float: '1.398.00'
df_lidl.dropna(inplace = True)
#df['Data_Upd'] = df['Data_Upd'].dt.strftime('%Y-%m-%d')#dayfirst=True ,format=('%d-%m-%Y'))
print(df_lidl.info())

path = r'C:\Users\fabio\OneDrive\Ambiente de Trabalho\Projetos python Economista\lidl.csv'
df_lidl.to_csv(path, sep ='\t', index= False)
