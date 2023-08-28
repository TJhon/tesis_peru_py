# imports
import requests as rs
import math
from bs4 import BeautifulSoup as bs
import urllib3
import random, string
# from unidecode import unidecode
urllib3.disable_warnings()


def first_2lether(string:str) -> str:
	"""
	input: Alonson Fernando Gonzales del Rio 
	output: afgdr
	"""
	words_ = string.strip().split(" ")
	try:
		fl = ''.join(word[0:2].lower() for word in words_)
	except:
		fl = ''.join(word[0:1].lower() for word in words_)
	return fl

def tidy_text(text : str) -> str:
	tt = text.lower().strip()
	return tt

def random_author(n = 6, year = [1980, 2023]) -> str:
	random_string = ''.join(random.choice(string.ascii_letters) for _ in range(n)).lower()
	year_random = random.randint(year[0], year[1])
	random_author = f'{random_string}_{year_random}'
	return random_author

# print(first_2lether('ohoasldf a weoiruasjdfl'))
# print(random_author())