# imports
import requests as rs
import math
from bs4 import BeautifulSoup as bs
import urllib3
from unidecode import unidecode
urllib3.disable_warnings()


def first_lether(string:str) -> str:
	"""
	input: Alonson Fernando Gonzales del Rio 
	output: afgdr
	"""
	words_ = string.strip().split(" ")
	fl = ''.join(word[0].lower() for word in words_)
	return fl

def tidy_text(text : str) -> str:
	tt = text.lower().strip()
	unico
	print(tt)

tidy_text("hola mundO, sóy jññhon")