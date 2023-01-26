# -*- coding: utf-8 -*-
"""
Created on Wed Jan  4 21:15:30 2023

@author: fabio
"""

import requests
from bs4 import BeautifulSoup , SoupStrainer
import time
import json
import pandas as pd
from datetime import datetime

headers = {"User-Agent": "Mozilla/5.0 (W96indows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36",
    "Referer" : "www.google.com",
    "DNT" : "1"
    }

payload = ""

start = ['https://www.pingodoce.pt/product-sitemap1.xml',
         'https://www.pingodoce.pt/product-sitemap2.xml',
         'https://www.pingodoce.pt/product-sitemap3.xml']

start_time = time.time()

dict_prices = {}

for sitemap in start:
    
    with requests.Session() as session:
    
        resp = session.get(sitemap, data=payload, headers=headers)
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        for loc in soup.find_all('loc'):
            products_url = loc.get_text()
            
            if 'marca' in products_url:
                
                r = session.get(products_url, data=payload, headers=headers)
                
                only_tags = SoupStrainer(['span','h1'])
                bs = BeautifulSoup(r.text, 'html.parser', parse_only=(only_tags))
                
                try:
                    price = bs.find('span', {'class':'product-details_price'})
                    name = bs.find('h1', {'class': 'product-details__title'})
                    
                    list_ = [price.get_text().strip(), name.get_text().strip()]
                    
                    dict_prices[products_url] = list_
                
                except AttributeError:
                    pass

print("----- Request and BS: %s seconds -----" % (time.time() - start_time))

data = []
for x in range(1,4):
    with open(fr'C:\Users\fabio\OneDrive\Ambiente de Trabalho\Projetos python Economista\pingodoce_prices_{x}', 'r') as fp:
        data.append(json.load(fp))

#-----FIQUEI AQUI, tenho que converter a data[:3] em uma lista com um só dicionário
# search how to combine dictionaries

prices = []
nomes = []
for list_ in dict_prices.values():
    prices.append(list_[0][:list_[0].find('€')].replace(',','.'))
    nomes.append(list_[1])

chain = []
today = []
for n in range(len(dict_prices)):
    chain.append('PingoDoce')
    today.append(datetime.today().strftime('%Y-%m-%d'))

table = {}
table['Supermercado'] = chain
table['Data_Upd'] = today
#table['Tipos'] = tipos
#table['Categorias_1'] = categorias_1
#table['Categorias_2'] = categorias_2
table['Produtos'] = nomes
table['Preços'] = prices

df = pd.DataFrame(table)
df['Preços'] = df['Preços'].astype(float)
df.dropna(inplace = True)
#df['Data_Upd'] = df['Data_Upd'].dt.strftime('%Y-%m-%d')#dayfirst=True ,format=('%d-%m-%Y'))
print(df.info())

path = r'C:\Users\fabio\OneDrive\Ambiente de Trabalho\Projetos python Economista\pingodoce.csv'
df.to_csv(path, sep ='\t', index= False)

