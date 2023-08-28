# imports
import requests as rs
import pandas as pd
import math
from bs4 import BeautifulSoup as bs
import urllib3
from tqdm import tqdm
urllib3.disable_warnings()



from utils import *

class Download:
	def __init__(
		self, url, recent_str = 'recent-submissions?offset=', prefix_url = None, split_url = '/repositorio',
		metadata_show = '?show=full', download_dir = 'thesis_download', replace_dshome = True
		):
		if prefix_url is None and split_url is not None:
			prefix_url, _ = url.split(split_url)

		self.url_collection = url
		self.prefix_url = prefix_url
		self.metadata_show = metadata_show
		self.download_dir = download_dir
		self.recent_str = recent_str
		self.replace_str = replace_dshome
	def read_html(self, url):
		html_rq = rs.get(url, verify=False).content
		html = bs(html_rq, 'html.parser')
		return html
	# 'hola'.t

	def get_pages_url(self, n = 0, css = 'pagination-info'):

		url_main = f'{self.url_collection}/{self.recent_str}{n}'
		# url_html = rs.get(url_main, verify=False).content
		# html = bs(url_html, 'html.parser')
		html = self.read_html(url_main)

		total_text = html.find(class_=css).text
		left, total = total_text.split(' of ')
		_, thesis_page = left.split('-')

		total = int(total)
		page_break = int(thesis_page)

		total_pages = math.ceil(total / page_break) 
		n_pages = [x for x in range(total_pages)]
		links_pages = [
			f'{self.url_collection}/{self.recent_str}{n1 * 20}' 
			for n1 in n_pages
		]
		self.pages_with_tesis = links_pages
		self.total_tesis = total
		self.page_break_thesis = page_break

		return self
	def get_tesis_from_page(self, page_url) -> []:
		page_html = self.read_html(page_url)
		thesis_items = page_html.find_all('h4', class_='artifact-title')
		thesis_hrefs = [t.find('a')['href'] for t in thesis_items]
		thesis_urls = [f'{self.prefix_url}{thesis_href}{self.metadata_show}' for thesis_href in thesis_hrefs]
		return thesis_urls
	def get_dict_page(self, n_pages: int = None):
		pages_with_tesis = self.pages_with_tesis
		prefix = self.prefix_url
		total = self.total_tesis
		if n_pages is None:
			n_pages = len(pages_with_tesis)

		ns = [n * 20 for n in range(n_pages)]
		off_set = [f'off_set_{n}' for n in ns]

		thesis_dict = {}
		for page in tqdm(range(n_pages)):
			thesis_dict[off_set[page]] = self.get_tesis_from_page(pages_with_tesis[page])
		self.thesis_dict = thesis_dict
		return self
	def url_to_dir_path(self, html, css = 'breadcrumb hidden-xs'):
		info = html.find('ul', class_=css)
		info = info.find_all('a')
		info = [a.text for a in info]
		if self.replace_str:
			info[0] = self.download_dir
		return info
	def get_metadata(self, url):
		thesis_html = self.read_html(url)
		metadata = str(thesis_html.find('table'))
		dir_ = self.url_to_dir_path(thesis_html)
		# df = pd.read_html(metadata)[0][[0, 1]]
		# df.columns = ['column', 'info']
		return dir_
		

	# def 
# /html/body/div[1]/div/div/div/ul


url_collection = 'https://tesis.pucp.edu.pe/repositorio/handle/20.500.12404/6'
# a = url_collection.split('/repositorio')
a = Download(url_collection)
b = a.get_pages_url().get_dict_page(1)
pag_n = list(b.thesis_dict.keys())

thesi_dict = b.thesis_dict
c = thesi_dict[pag_n[0]][0]

d = b.get_metadata(c)
print(d)

# print(c)

# thesis_dict = {}
# thesis_dict['a'] = [12, 3]
# thesis_dict['b'] = [12, 3]
# thesis_dict['c'] = [12, 1]
# b = pd.DataFrame(thesis_dict)
# print(b)
# print(a.get_tesis_from_page(page[1]))

# print(a.prefix_url)
# a
# print(a)
	# print(get_pages_url(url_collection))
