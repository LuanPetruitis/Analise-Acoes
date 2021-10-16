# -*- encoding: utf-8 -*-

from pymongo import MongoClient
import datetime
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class EnviarEmail():
	def __init__(self):
		self.dados = []


	def pesquisa(self):
		date = datetime.datetime.now()
		date = date.date()
		date = "{:%d/%m/%Y}".format(date)

		client = MongoClient("CONECTAR NO SEU BANCO DO MONGO DB")

		db = client["acoes"]
		
		collection = db["setup_ativo"]

		self.dados = collection.find({"data": str(date)})


	def get_html(self):
		date_today = datetime.datetime.now()
		data = date_today.date()
		data_formatada = date_today.strftime('%d/%m/%Y')
		print(f"self.dados -> {self.dados}")
		if self.dados: 
			html = f"""
				<html>
				<head>
					<meta charset="UTF-8">
					<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
				</head>
				<body>
					<div style="width: 100%; display: flex; align-items: center; flex-direction: column;">
						<div style="max-width: 600px; width: 450px;">
							<div>
								<h1>Analise para o dia {data_formatada}</h1>
							</div>
			"""

			for dado in self.dados:
				html += f"""
					<table style='line-height: 2rem; font-size: large; width: 100%;'>
						<tr style='width: 100%; text-align: center;'>
							<td style='text-align: left; padding-right: 4px;'><a style='text-transform: uppercase;' href='{dado['url']}' target='_blank'>{dado['papel']}</a></td>
							<td><a style='text-transform: uppercase; padding-right: 4px;' href='{dado['url_setor']}' target='_blank'>{dado['setor']}</a></td>
							<td style='text-align: right;'>{dado['tempo_grafico']}</td>
						</tr>
						<tr>
							<td>Setup:</td>
							<td style='text-align: right;' colspan='2'>{dado['setup']}</td>
						</tr>
						<tr>
							<td colspan='2'>Dividendos:</td>
							<td style='text-align: right;'>{dado['divyield']} </td>
						</tr>
						<tr>
							<td colspan='2'>P/Ativ Circ Liq:</td>
							<td style='text-align: right;'>{dado['pativcircliq']} </td>
						</tr>
						<tr>
							<td colspan='2'>Cres. Rec (5a):</td>
							<td style='text-align: right;'>{dado['percentcrescrec5a']} </td>
						</tr>
						<tr>
							<td colspan='2'>Div Br/ Patrim:</td>
							<td style='text-align: right;'>{dado['divbrutpatrim']} </td>
						</tr>
						<tr>
							<td colspan='2'>ROE:</td>
							<td style='text-align: right;'>{dado['roe']} </td>
						</tr>
						<tr>
							<td colspan='2'>P/L:</td>
							<td style='text-align: right;'>{dado['pl']} </td>
						</tr>
						<tr>
							<td colspan='2'>P/VP:</td>
							<td style='text-align: right;'>{dado['pvp']} </td>
						</tr>
						<tr>
							<td colspan='2'>Marg. Líquida:</td>
							<td style='text-align: right;'>{dado['mrgliq']} </td>
						</tr>
					</table>
					<table style='border: gray 1px solid; text-align: center; margin: 2px; border-spacing: 0; line-height: 2rem; font-size: large; width: 100%;'>
						<thead style='background-color: rgb(184, 164, 164);'>
							<tr>
								<th>Entrada</th>
								<th>Stop</th>
								<th>Risco</th>
								<th>Possível alvo</th>
							</tr>
						</thead>
						<tbody>
							<tr>
								<td>{dado['Entrada']:.2f}</td>
								<td>{dado['Stop']:.2f}</td>
								<td>{dado['Risco']:.2f}</td>
								<td>{((float(dado['Risco'])* 2) + dado['Entrada']):.2f}</td>
							</tr>
						</tbody>
					</table>

					<div style='height:1px; margin: 30px 0; background-color: grey; width: 100%;'></div>

				"""

			html += """ 	
						</div>
					</div>
				</body>
				</html>
			"""

			return html
		
		return False

	
	def envia_email(self):
		print("Enviando email.")

		# is_diference = verifica_se_esta_igual_outro_dia()

		# if is_diference:
		sender_email = "luanpetruitis@gmail.com"
		receiver_emails = ["luanpetruitis@gmail.com","viniciusms1@hotmail.com","joaovictor.1314.jv@gmail.com"]
		# receiver_emails = ["luanpetruitis@gmail.com"]
		password = "futebol2011"
		# password = input("Type your password and press enter:")

		message = MIMEMultipart("alternative")
		date_today = datetime.datetime.now()
		dateFormated = date_today.strftime('%d/%m/%Y')
		message["Subject"] = "Melhores papeis em momentos favoráveis - %s" %(dateFormated)

		html = self.get_html()
		if html:
			message["From"] = sender_email
			for receiver_email in receiver_emails:
				message["To"] = receiver_email

				text = MIMEText(html, "html")
				message.attach(text)


				# Create secure connection with server and send email
				context = ssl.create_default_context()
				with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
					server.login(sender_email, password)
					server.sendmail(
						sender_email, receiver_email, message.as_string()
					)