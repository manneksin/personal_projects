# -*- coding: utf-8 -*-
"""
Created on Sun Oct 16 15:15:03 2022
Finishes:_____________

@author: fabio

Performance improvement ideas:
    Nonetype Exception instead of If Statements
    SoupStrainer [list of multiple tags]
    Concurrency

https://beckernick.github.io/faster-web-scraping-python/
https://oxylabs.io/blog/how-to-make-web-scraping-faster


"""

import requests
from bs4 import BeautifulSoup , SoupStrainer
import time
from datetime import datetime
import pandas as pd
import json

headers = {"User-Agent": "Mozilla/5.0 (W96indows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36",
    "Referer" : "www.google.com",
    "DNT" : "1"
    }

payload = ""

#Try CSS selectors
#take products IDs
#Remove the last elif with list of filters, do a for with range as f string in sitemaps (if needed)

start_time = time.time()

sitemap = 'https://www.minipreco.pt/sitemap.xml'

dict_prices = {}

#def links_prices(chain, sitemap, filter_, tag_1, attr_1, tag_2, attr_2, attr_value_2, option):

with requests.Session() as session:

    resp = session.get(sitemap, data=payload, headers=headers)

    soup = BeautifulSoup(resp.text, 'lxml')
    
    for loc in soup.find_all('loc'):
        products_url = loc.get_text()
        
        if '/p/' in products_url:
            
            r = session.get(products_url, data=payload, headers=headers)
            print(r.status_code)
            
            only_tags = SoupStrainer(['span', 'h1'])
            
            bs = BeautifulSoup(r.text, 'lxml', parse_only=(only_tags))
            
            try: 
                price = bs.find('span', {'class':'big-price'})
                name = bs.find('h1', {'itemprop': 'name'})
                
                list_ = [price.get_text().strip(), name.get_text().strip()]
                
                dict_prices[products_url] = list_
            
            except AttributeError:
                pass

#with open(r'C:\Users\fabio\OneDrive\Ambiente de Trabalho\Projetos python Economista\{chain}', 'w') as fp:
    #json.dump(dict_prices, fp)
                        
print("----- Request and BS took: %s seconds -----" % (time.time() - start_time))

'''
with open('data.json', 'w') as fp:
    json.dump(lidl_prices, fp)

how to load data with json.
with open('data.json', 'r') as fp:
    data = json.load(fp)
'''

#categorias_2 = [] #2
categorias_1 = [] #1
tipos = [] #0
minipreco_x = []

for prods in dict_prices.keys():
    minipreco_x.append(prods[34:].split('/')[:-2])
    
for list_ in minipreco_x:
    for lines in list_:
        if lines==list_[0]:
            tipos.append(list_[0])
        elif lines==list_[1]:
            categorias_1.append(list_[1])
        #elif lines==list_[2]:
            #categorias_2.append(list_[2])

prices = []
nomes = []
for prods_prices in dict_prices.values():
    prices.append(prods_prices[0].replace(',', '.')[:-2])
    nomes.append(prods_prices[1])

chain = []
today = []
for n in range(len(dict_prices)):
    chain.append('Minipreco')
    today.append(datetime.today().strftime('%Y-%m-%d'))

table = {}
table['Supermercado'] = chain
table['Data_Upd'] = today
#table['Tipos'] = tipos
table['Categorias'] = categorias_1
#table['Categorias_2'] = categorias_2
table['Produtos'] = nomes
table['Preços'] = prices

df = pd.DataFrame(table)
df.to_csv(r'C:/Users/fabio/OneDrive/Ambiente de Trabalho/Projetos python/minipreco.csv', sep='\t', index= False)

#Quando abro no excel, aparecem os caracteres especiais!
'''
Ver este link

https://www.youtube.com/watch?v=qQDB6SE0a9c&ab_channel=codeRECODEwithUpendra

Apontamentos:

Como gravar uma nested list:
with open('minipreco_prod_names.txt', 'w') as file:
    for list_ in minipreco_prod_names:
            file.write(" ".join(map(str, list_)))
            file.write("\n")

Como abrir um ficheiro numa nested list:
yo =[]
with open('minipreco_prod_names.txt', 'r') as file:
    for line in file:
        line = file.read().split('\n')
        for x in line:
            yo.append(x.split(' '))

Saving Lists into txt
      
def saving_to_txt (filename, list_):
    with open(filename, 'wt') as file:
        for line in list_:
            file.write(line + ';')

saving_to_txt("aldi_prices.txt", aldi_prices)
saving_to_txt("aldi_prod_names.txt", aldi_prod_names)
saving_to_txt("lidl_prices.txt", lidl_prices)
saving_to_txt("lidl_prod_names.txt", lidl_prod_names)
'''
