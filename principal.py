from acoes import Acoes
from preco import Precos
from MelhoresPapeis import MelhoresPapeis
from enviarEmail import EnviarEmail

try:
	acoes = Acoes()
	acoes.procura_setor()
	acoes.deleta_banco()
	acoes.grava_banco()
	precos = Precos()
	precos.grava_precos()
	precos.leitura_documento()
	precos.deleta_banco()
	precos.grava_banco()
finally:
	acoes.fecha_navegador()

melhores_papeis = MelhoresPapeis()
melhores_papeis.buscaFundamentos()
melhores_papeis.pegaCandles()
melhores_papeis.analisar_precos()

enviar_email = EnviarEmail()
enviar_email.pesquisa()
enviar_email.envia_email()