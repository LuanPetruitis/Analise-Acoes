# -*- encoding: utf-8 -*-

import requests
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import Select
import json
import time
from pymongo import MongoClient
import datetime
from webdriver_manager.firefox import GeckoDriverManager

class Acoes():
    def __init__(self):
        self.url = "http://fundamentus.com.br/buscaavancada.php"

        self.setores = []

        # Configuração para abrir o navegador
        option = Options()
        option.headless = True
        
        self.driver = webdriver.Firefox(executable_path=GeckoDriverManager().install(), options=option)
        self.ranking = []
        self.teste = {}
        self.driver.get(self.url)
        time.sleep(0.5)

    def procura_setor(self):
        element = self.driver.find_element_by_xpath("//select")

        # Traz todo o html da parte que navegamos
        html_content = element.get_attribute('outerHTML')
        soup = BeautifulSoup(html_content, 'html.parser')
        setores_site = soup.get_text().split('\n')
        while '' in setores_site:
            setores_site.remove('')

        self.setores = setores_site

        print(setores_site)
        for index in range(len(self.setores)):
            # Encontra no html o caminho para ver onde vai clicar
            # Clicar em um input
            elem = Select(self.driver.find_element_by_name('setor'))
            elem.select_by_index(index+1)
            time.sleep(0.5)
            self.driver.find_element_by_xpath("//input[@class='buscar']").click()

            time.sleep(0.5)

            element = self.driver.find_element_by_xpath("//table")

            # Traz todo o html da parte que navegamos
            html_content = element.get_attribute('outerHTML')

            # Tratar os dados
            soup = BeautifulSoup(html_content, 'html.parser')
            table = soup.find(name='table')

            # Pandas trata o html
            # Traz um array e coloca o head para trazer todos registros
            df_full = pd.read_html(str(table))[0]

            # Organiza os dados para colocar em um dicionário
            df = df_full[['Papel', 'Cotação', 'P/L', 'P/VP', 'PSR', 'Div.Yield', 'P/Ativo', 'P/Cap.Giro', 'P/EBIT', 'P/Ativ Circ.Liq', 'EV/EBIT', 'EV/EBITDA', 'Mrg Ebit', 'Mrg. Líq.', 'Liq. Corr.', 'ROIC', 'ROE', 'Liq.2meses', 'Patrim. Líq', 'Dív.Brut/ Patrim.', 'Cresc. Rec.5a']]

            df.columns = ['papel','cotacao','pl','pvp','psr','divyield','pativo','pcapgiro','pebit','pativcircliq','evebit','evebitda','mrgebit','mrgliq','liqcorr','roic','roe','liq2meses','patrimliq','divbrutpatrim','percentcrescrec5a']

            # Monta o dicionário
            self.teste['acoes'] =  df.to_dict('records')
            
            self.formata_dados(self.teste['acoes'], self.setores[index], (index+1+1))

            # Volta para tela anterios
            self.driver.back()
            time.sleep(0.5)

    def formata_dados(self, teste, setor, codigo_setor):
        for acao in teste:
            acao['papel'] = acao['papel'].lower() 
            acao['psr'] = float(str(acao['psr']).replace('.','').replace(',','.')) / 1000 
            acao['pcapgiro'] = float(str(acao['pcapgiro']).replace('.','').replace(',','.')) / 100
            acao['pebit'] = float(str(acao['pebit']).replace('.','').replace(',','.')) / 100
            acao['evebit'] = float(str(acao['evebit']).replace('.','').replace(',','.')) / 100
            acao['evebitda'] = float(str(acao['evebitda']).replace('.','').replace(',','.')) / 100
            acao['liqcorr'] = float(acao['liqcorr']) / 100
            acao['liq2meses'] = float(str(acao['liq2meses']).replace('.', '').replace(',', '.').replace('%', ''))
            acao['divbrutpatrim'] = float(acao['divbrutpatrim']) / 100
            acao['divyield'] = float(acao['divyield'].replace(',', '.').replace('.', '').replace('%', '')) / 100
            acao['mrgebit'] = float(acao['mrgebit'].replace('.', '').replace(',', '.').replace('%', ''))
            acao['mrgliq'] = float(acao['mrgliq'].replace('.', '').replace(',', '.').replace('%', ''))
            acao['percentcrescrec5a'] = float(acao['percentcrescrec5a'].replace('.', '').replace(',', '.').replace('%', ''))
            acao['cotacao'] = float(acao['cotacao']) / 100
            acao['pl'] = float(str(acao['pl']).replace('.','').replace(',','.')) / 100 
            acao['patrimliq'] = float(str(acao['patrimliq']).replace('.','').replace(',','.')) / 100
            acao['roe'] = float(str(acao['roe']).replace('.', '').replace(',', '.').replace('%', ''))
            acao['roic'] = float(str(acao['roic']).replace('.', '').replace(',', '.').replace('%', ''))
            acao['pvp'] = float(str(acao['pvp']).replace('.', '')) / 100
            acao['pativo'] = float(str(acao['pativo']).replace('.', '')) / 1000
            acao['pativcircliq'] = float(str(acao['pativcircliq']).replace('.', '').replace(',', '.')) / 100
            acao['setor'] = setor 
            acao['url'] = "http://fundamentus.com.br/detalhes.php?papel=" + str(acao['papel'].upper())
            acao['data'] = str(datetime.date.today())
            acao['url_setor'] = "http://fundamentus.com.br/resultado.php?setor=" + str(codigo_setor)
            
            self.ranking.append(acao)

    def fecha_navegador(self):
            self.driver.quit() 

    def grava_banco(self):
        client = MongoClient("CONECTAR NO SEU BANCO DO MONGO DB")

        db = client["acoes"]
        
        collection = db["fundamentos"]

        collection.insert_many(self.ranking)

    def deleta_banco(self):
        myclient = MongoClient("CONECTAR NO SEU BANCO DO MONGO DB")
                                
        mydb = myclient["acoes"]
        mycol = mydb["fundamentos"]

        date_today = str(datetime.date.today())

        myquery = {"data": date_today}

        mycol.delete_many(myquery)