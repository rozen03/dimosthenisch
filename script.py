 q#!/usr/bin/python3
from bs4 import BeautifulSoup
try:
    import urllib.request as urllib2
except ImportError:
    import urllib2
import requests
from retrying import retry
import sys
import threading
import os
from urllib.request import urlretrieve
from pony.orm import *
from retrying import retry
db = Database()
class File(db.Entity):
	fileName= Required(str)
db.bind('sqlite', 'files.sqlite3' , create_db=True)
db.generate_mapping(create_tables=True)
def config(year, page):
	payload={}
	payload["keywords"]=""
	payload["pagesCount"]="0"
	payload["fekReleaseDateTo"]="31.12.2018"
	payload["fekReleaseDateFrom"]="01.01."+str(year)
	payload["search"]="ΑΝΑΖΗΤΗΣΗ"
	payload["fekEffectiveDateTo"]="31.12."+str(year)
	for i in range(20):
		payload["chbIssue_"+str(i)]="on"
	payload["resultsCount"]="0"
	payload["etshop"]="0"
	payload["year"]=str(year)
	payload["fekNumberTo"]=""
	payload["pageNumber"]=str(page)
	payload["fekEffectiveDateFrom"]="01.01."+str(year)
	payload["fekNumberFrom"]=""
	return payload
class DownloadThread(threading.Thread):
	def __init__(self,fileName,url,year):
		threading.Thread.__init__(self)
		self.url=url
		self.year=str(year)
		self.fileName=self.year+"/"+fileName
	@retry(Exception, tries=100000)
	def run(self):
		with db_session:
			if File.get(fileName=self.fileName):
				return
		r = requests.get(self.url)
		resultPdf=BeautifulSoup(r.text, "lxml")
		link=resultPdf.find("head").find("meta")["content"][6:]
		r = requests.get(link)
		resultPdf=BeautifulSoup(r.text, "lxml")
		link=resultPdf.find("head").find("meta")["content"][6:]
		if not os.path.exists(str(self.year)):
			os.makedirs(str(self.year))
		response = urllib2.urlopen(link)
		data = response.read()      # a `bytes` object
		with open(self.fileName,"wb") as f:
			f.write(data)
		print("Downloaded: ",self.fileName)
		with db_session:
			file= File(fileName=self.fileName)
def scrapYear(year,page):
	tabla =True
	try:
		payload= config(year,page)
		r = requests.post(url, data=payload)
		result=BeautifulSoup(r.text, "lxml")
		tabla = result.find("table",id="result_table")
		for tr in tabla.find_all("tr"):
			try:
				trClass = tr["class"][0]
			except:
				continue
			if trClass !=  "even" and  trClass !="odd":
				continue
			for td in tr.find_all("td"):
				span=td.find("span")
				if span:
					spanb=span.find("b")
					fileName=str.join(" ",spanb.text.split())
				for a in td.find_all("a", href=True):
					coso=a["href"]

			misticUrl="http://www.et.gr"+coso
			DownloadThread(fileName.strip()+".pdf",misticUrl,year).start()
		return True
	except Exception as e:
		print(type(e))
		print(e)
		print("En el anio",year,"pagina",page,"exploto")
		return False

url="http://www.et.gr/idocs-nph/search/fekForm.html"
for year in range(1833,2018):
#for year in range(2000,2018):
	print("Downloading Year: ",year)
	newPages=True
	count=1
	while (newPages):
		newPages=scrapYear(year,count)
		count+=1
