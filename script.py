#!/usr/bin/python3
from bs4 import BeautifulSoup
try:
    import urllib.request as urllib2
except ImportError:
    import urllib2
import requests
from retrying import retry
import sys
from urllib.request import urlretrieve

def download(fileName,url):
	print("Downloading",fileName,end="...")
	response = urllib2.urlopen(url)
	data = response.read()      # a `bytes` object
	with open(fileName,"wb") as f:
		f.write(data)
	print("OK")

url="http://www.et.gr/idocs-nph/search/fekForm.html"
payload={}
payload["keywords"]=""
payload["pagesCount"]="0"
payload["fekReleaseDateTo"]="31.12.2018"
payload["fekReleaseDateFrom"]="01.01.2017"
payload["search"]="ΑΝΑΖΗΤΗΣΗ"
payload["fekEffectiveDateTo"]="31.12.2017"
for i in range(20):
	payload["chbIssue_"+str(i)]="on"
payload["resultsCount"]="0"
payload["etshop"]="0"
payload["year"]="2016"
payload["fekNumberTo"]=""
payload["pageNumber"]="1"
payload["fekEffectiveDateFrom"]="01.01.2017"
payload["fekNumberFrom"]=""
r = requests.post(url, data=payload)
result=BeautifulSoup(r.text, "lxml")
tabla = result.find("table",id="result_table")
for tr in tabla.find_all("tr")[2:-1]:
	for td in tr.find_all("td"):
		trTexts = td.text.strip().split("\n")
		if(len(trTexts)>3):
			fileName=trTexts[3].strip()
		for a in td.find_all("a", href=True):
			coso=a["href"]

	misticUrl="http://www.et.gr"+coso
	#print("url to downoad",misticUrl)
	print("Name: ",fileName)
	r = requests.get(misticUrl)
	resultPdf=BeautifulSoup(r.text, "lxml")
	link=resultPdf.find("head").find("meta")["content"][6:]
	r = requests.get(link)
	resultPdf=BeautifulSoup(r.text, "lxml")
	link=resultPdf.find("head").find("meta")["content"][6:]

	download(fileName.strip()+".pdf",link)
