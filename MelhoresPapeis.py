from pymongo import MongoClient
import json
import datetime

class MelhoresPapeis():
    def __init__(self):
        self.client = MongoClient("CONECTAR NO SEU BANCO DO MONGO DB")

        self.todos_candles = {}
        self.acoes_fundamentos = []
        self.papeis_bons_fundamentos_precos = []


    def buscaFundamentos(self):
        db = self.client["acoes"]

        collection = db["fundamentos"]

        # papeis = collection.find({"data": "2021-05-15", "pl":{'$gte':5, '$lte':15}, "liq2meses": {'$gte': 1000000}, "roe": {'$gte': 10}}).limit(10).sort("papel")
        # papeis = collection.find({"data": str(datetime.date.today()), "pl":{'$gte':5, '$lte':15}, "liq2meses": {'$gte': 1000000}, "roe": {'$gte': 10}})
        
        # OFICIAL
        self.papeis = collection.find({"data": str(datetime.datetime.now().date()), "pl":{'$gte':5, '$lte':15}, "liq2meses": {'$gte': 1000000}, "roe": {'$gte': 10}})
        

    def pegaCandles(self):
        db = self.client["acoes"]

        collection = db["candles"]

        datas = collection.aggregate([{ '$group' : { '_id' : "$data" }}, {'$sort': {'_id': -1}}, {'$limit': 3}])
        # print(datas)

        data_query = ""
        for data in datas:
            print(data)
            data_query = data['_id']

        for papel in self.papeis:
            candles_papel = collection.find({"data": {'$gte': data_query}, "papel": papel['papel']})
            for candle_papel in candles_papel:
                if papel['papel'] not in self.todos_candles:
                    self.todos_candles[papel['papel']] = list()

                dados_formatados_candles = {
                    'papel': candle_papel['papel'],
                    'abertura': candle_papel['abertura'],
                    'fechamento': candle_papel['fechamento'],
                    'maxima': candle_papel['maxima'],
                    'minima': candle_papel['minima'],
                    'volume': candle_papel['volume'],
                    'data': candle_papel['data'],
                    'url': papel['url'],
                    'url_setor': papel['url_setor'],
                    'setor': papel['setor'],
                    'divyield': papel['divyield'],
                    'pativcircliq': papel['pativcircliq'],
                    'percentcrescrec5a': papel['percentcrescrec5a'],
                    'divbrutpatrim': papel['divbrutpatrim'],
                    'roe': papel['roe'],
                    'pl': papel['pl'],
                    'pvp': papel['pvp'],
                    'mrgliq': papel['mrgliq']
                }
                self.todos_candles[papel['papel']].append(dados_formatados_candles)
				
            dados_formatados_fundamentos = {
                'papel': papel['papel'],
                'cotacao': papel['cotacao'],
                'pl': papel['pl'],
                'pvp': papel['pvp'],
                'psr': papel['psr'],
                'divyield': papel['divyield'],
                'pativo': papel['pativo'],
                'pcapgiro': papel['pcapgiro'],
                'pebit': papel['pebit'],
                'pativcircliq': papel['pativcircliq'],
                'evebit': papel['evebit'],
                'evebitda': papel['evebitda'],
                'mrgebit': papel['mrgebit'],
                'mrgliq': papel['mrgliq'],
                'liqcorr': papel['liqcorr'],
                'roic': papel['roic'],
                'roe': papel['roe'],
                'liq2meses': papel['liq2meses'],
                'patrimliq': papel['patrimliq'],
                'divbrutpatrim': papel['roe'],
                'percentcrescrec5a': papel['percentcrescrec5a'],
                'setor': papel['setor'],
                'data': papel['data'],
            } 

            self.acoes_fundamentos.append(dados_formatados_fundamentos)
        		

        print(json.dumps(self.acoes_fundamentos, indent=4, sort_keys=True))
        print(json.dumps(self.todos_candles, indent=4, sort_keys=True))

    def analisar_precos(self):
        for papel_candles in self.todos_candles:
            self.ponto_fechamento_reversao(self.todos_candles[papel_candles])
            self.gap_trap(self.todos_candles[papel_candles])
        
        self.deleta_banco()
        self.grava_banco()

    def ponto_fechamento_reversao(self, papel_candles):
        if len(papel_candles) >= 3:
            if papel_candles[0]['minima'] < papel_candles[1]['minima'] and papel_candles[0]['minima'] < papel_candles[2]['minima']:
                if papel_candles[0]['fechamento'] > papel_candles[1]['fechamento']:
                    date = datetime.datetime.now()
                    date = date.date()
                    date = "{:%d/%m/%Y}".format(date)
                    print(papel_candles[0]['papel'])
                    informacoes = {
                        "papel": papel_candles[0]['papel'],
                        "tempo_grafico": 'Diario',
                        "setup": "Ponto fechamento e reversão",
                        "data": date,
                        "url": papel_candles[0]['url'],
                        "url_setor": papel_candles[0]['url_setor'],
                        "setor": papel_candles[0]['setor'],
                        "divyield": papel_candles[0]['divyield'],
                        "Entrada": papel_candles[0]['maxima'] + 0.01,
                        "Stop": papel_candles[0]['minima'] - 0.01,
                        "Risco": papel_candles[0]['maxima'] - papel_candles[0]['minima'],
                        "pativcircliq": papel_candles[0]['pativcircliq'],
                        "percentcrescrec5a": papel_candles[0]['percentcrescrec5a'],
                        "divbrutpatrim": papel_candles[0]['divbrutpatrim'],
                        "roe": papel_candles[0]['roe'],
                        "pl": papel_candles[0]['pl'],
                        "pvp": papel_candles[0]['pvp'],
                        "mrgliq": papel_candles[0]['mrgliq']
                    }
                    self.papeis_bons_fundamentos_precos.append(informacoes)
                return False
            return False
        return False
            
    def gap_trap(self, papel_candles):
        if len(papel_candles) >= 3:
            if papel_candles[0]['maxima'] < papel_candles[1]['minima'] or papel_candles[0]['minima'] > papel_candles[1]['maxima']:
                date = datetime.datetime.now()
                date = date.date()
                date = "{:%d/%m/%Y}".format(date)
                print(papel_candles[0]['papel'])
                informacoes = {
                    "papel": papel_candles[0]['papel'],
                    "tempo_grafico": 'Diario',
                    "setup": "Gap Trap",
                    "data": date,
                    "url": papel_candles[0]['url'],
                    "url_setor": papel_candles[0]['url_setor'],
                    "setor": papel_candles[0]['setor'],
                    "divyield": papel_candles[0]['divyield'],
                    "Entrada": papel_candles[0]['maxima'] + 0.01,
                    "Stop": papel_candles[0]['minima'] - 0.01,
                    "Risco": papel_candles[0]['maxima'] - papel_candles[0]['minima'],
                    "pativcircliq": papel_candles[0]['pativcircliq'],
                    "percentcrescrec5a": papel_candles[0]['percentcrescrec5a'],
                    "divbrutpatrim": papel_candles[0]['divbrutpatrim'],
                    "roe": papel_candles[0]['roe'],
                    "pl": papel_candles[0]['pl'],
                    "pvp": papel_candles[0]['pvp'],
                    "mrgliq": papel_candles[0]['mrgliq']
                }
                self.papeis_bons_fundamentos_precos.append(informacoes)
            return False
        return False


    def grava_banco(self):
        client = MongoClient("CONECTAR NO SEU BANCO DO MONGO DB")

        db = client["acoes"]
        
        collection = db["setup_ativo"]
        print(self.papeis_bons_fundamentos_precos)
        if self.papeis_bons_fundamentos_precos:
            collection.insert_many(self.papeis_bons_fundamentos_precos)
        
    def deleta_banco(self):
        myclient = MongoClient("CONECTAR NO SEU BANCO DO MONGO DB")
        mydb = myclient["acoes"]
        mycol = mydb["setup_ativo"]

        date_today = datetime.datetime.now()
        date = date_today.date()
        date = "{:%d/%m/%Y}".format(date)

        myquery = {"data": str(date)}

        mycol.delete_many(myquery)
