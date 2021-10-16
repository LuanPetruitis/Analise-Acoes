# -*- encoding: utf-8 -*-

import requests
import time
from pymongo import MongoClient
import requests
from datetime import datetime, date, timedelta

from zipfile import ZipFile
import os.path
import re


class Precos():
    def __init__(self):
        self.precos = []

    def grava_precos(self):
        for day in range(1, 8):
            date = datetime.now()
            date = date.date() - timedelta(days=day)
            if (date.weekday() < 5): 
                date = "{:%d/%m/%Y}".format(date)
                date_sem_barra = str(date).replace('/', '')
                url = f"http://bvmf.bmfbovespa.com.br/InstDados/SerHist/COTAHIST_D{date_sem_barra}.ZIP"
                preco = requests.get(url)
                date = str(date).replace('/', '_')
                file = open(f"historico/preco{date}.zip", "wb+")
                file.write(preco.content)
    
    def leitura_documento(self):
        for day in range(1, 8):
            date = datetime.now()
            date = date.date() - timedelta(days=day)
            if (date.weekday() < 5): 
                date_save = str(date)
                date = "{:%d/%m/%Y}".format(date)
                date = str(date).replace('/', '_')
                	
                if os.path.exists(f"historico/preco{date}.zip"):

                    try:
                        documento = ZipFile(f"historico/preco{date}.zip")
                        documento.extractall()
                        # time.sleep(1)
                        date = str(date).replace('_', '')
                        file = open("COTAHIST_D"+str(date)+".TXT", "r")
                        file.seek(0,0)

                        for linha in file.readlines():
                            if linha.find('COTAHIST') < 0:
                                self.extrair_dados(linha, date_save)
                    except: 
                        pass


    def extrair_dados(self, linha_acao, date_save):
        x = re.match("^01(\d{8})(.{2})(.{12})(.{3})(.{12})(.{10})(.{3})(.{4})(\d{13})(\d{13})(\d{13})(\d{13})(\d{13})(\d{13})(\d{13})(\d{5})(\d{18})(\d{18})(\d{13})(\d{1})(\d{8})(\d{7})(\d{13})(.{12})(\d{3})", linha_acao)
        papel = {
            'papel': x.group(3).rstrip().lower(),
            'abertura': float(x.group(9)) / 100,
            'fechamento': float(x.group(13)) / 100,
            'maxima': float(x.group(10)) / 100,
            'minima': float(x.group(11)) / 100,
            'volume': float(x.group(17)) / 1000,
            'data': date_save
        }
        self.precos.append(papel)

    def grava_banco(self):
        client = MongoClient("CONECTAR NO SEU BANCO DO MONGO DB")

        db = client["acoes"]
        
        collection = db["candles"]

        collection.insert_many(self.precos)

    def deleta_banco(self):
        myclient = MongoClient("CONECTAR NO SEU BANCO DO MONGO DB")
        mydb = myclient["acoes"]
        mycol = mydb["candles"]

        for day in range(1, 8):
            date = datetime.now()
            date = date.date() - timedelta(days=day)
            if (date.weekday() < 5):

                myquery = {"data": str(date)}

                mycol.delete_many(myquery)


# Fundamentos
# {"data": "2021-05-15", "pl":{$gte:5, $lte:15}, "liq2meses": {$gte: 1000000}, "roe": {$gte: 10}}