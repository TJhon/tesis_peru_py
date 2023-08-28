# imports
import requests as rs
import pandas as pd
import math
from bs4 import BeautifulSoup as bs
import urllib3
from tqdm import tqdm
import os
import re

urllib3.disable_warnings()



from utils import *

class ThesisPeru:
	def __init__(
		self, url, recent_str = 'recent-submissions?offset=', prefix_url = None, split_url = '/repositorio',
		metadata_show = '?show=full', download_dir = 'thesis_download', replace_dshome = True, force_download = False
		):

		if prefix_url is None and split_url is not None:
			prefix_url, _ = url.split(split_url)

		self.url_collection = url
		self.prefix_url = prefix_url
		self.metadata_show = metadata_show
		self.download_dir = download_dir
		self.recent_str = recent_str
		self.replace_str = replace_dshome
		self.force_download = force_download
	def read_html(self, url):
		"""
		read_html(url) | DRYS
		"""
		html_rq = rs.get(url, verify=False).content
		html = bs(html_rq, 'html.parser')
		return html
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
		info = [tidy_text(a.text) for a in info]
		info = [t.replace(' ', '_').replace('.', '_') for t in info]
		info = [t.replace('__', '_').replace('_(', '_') for t in info]
		info = [t.replace('_)', '') for t in info]
		if self.replace_str:
			info[0] = self.download_dir
		
		if not os.path.exists(info[0]):
			os.makedirs(info[0])
		
		full_dir = '/'.join(info)
		if not os.path.exists(full_dir):
			os.makedirs(full_dir)

		return full_dir
	def pdf_avaible(self, html, css = 'file-link') -> []:
		links = html.find_all('div', class_=css)
		links = [link.find('a')['href'] for link in links]

		pdf_options = [re.search(r'=1|=3|=4|=5|=10|=9', item) is not None for item in links]
		pdf_valid = [re.search(r'Allowed=y', item) is not None for item in links]
		pdf_exists = [re.search(r'pdf', item) is not None for item in links]
		pdf_resid = [
			item 
			for item, opt, val, ext in 
			zip(links, pdf_options, pdf_valid, pdf_exists) 
			if opt and val and ext
		]

		return pdf_resid
	def download_pdf(self, links, to_dir, author_year):

		def download_here(from_url, filename):
			if self.force_download or not os.path.exists(filename):
				# print('s')
				try:
					pdf = rs.get(from_url).content
					with open(filename, 'wb') as f:
						f.write(pdf)
				except: pass
		
		ext = 'pdf'

		pdf_avaible = False
		link_show = None
		n_link = len(links)

		file_name = ''

		if n_link > 1:
			pdf_avaible = True
			link_show = '\n'.join(links)
			for i in range(n_link):
				file_name_i = f'{to_dir}/{author_year}_{i}.{ext}'
				file_name += file_name_i + '\n'
				download_here(links[i], file_name)
		elif n_link > 0:
			pdf_avaible = True
			link_show = links[0]
			file_name = f'{to_dir}/{author_year}.{ext}'
			download_here(link_show, file_name)

		return pdf_avaible, link_show, file_name

	def get_names_year(self, df):
		try:
			columns = ['dc.contributor.author', 'dc.date.created']
			author, year = df[columns].to_numpy()[0]
			# author_year = df[columns].to_numpy()[0]
			author_name = first_2lether(author)
			author_year = f'{author_name}_{year}'
		except:
			print('random_author')
			author_year = random_author()
		return author_year
	def get_metadata(self, url):
		thesis_html = self.read_html(url)

		metadata = str(thesis_html.find('table'))

		# make dir recursive
		directory = self.url_to_dir_path(thesis_html)
		links = self.pdf_avaible(thesis_html)
		links = [self.prefix_url + link for link in links]


		df : pd.DataFrame= pd.read_html(str(metadata))[0][[0, 1]] 
		df = df.groupby(0, as_index=False).agg("\n".join)
		df = df.set_index(0).T.reset_index().drop(columns=["index"])

		author_year = self.get_names_year(df)

		pdf_avaible, link_show, local_file = self.download_pdf(links, directory, author_year)
		df = df.assign(pdf_avaible = pdf_avaible, pdf_online = link_show, local_file = local_file, url_thesis = url)

		return  df
	def save_metadata(self, data: pd.DataFrame, name: str, fail = False):
		dir_main = self.download_dir
		dir_metadata = f'{dir_main}/00metadata'
		if fail:
			dir_metadata += '/fail'
		else:
			dir_metadata += '/success'

		if not os.path.exists(dir_metadata):
			os.makedirs(dir_metadata)
		data.to_json(f'{dir_metadata}/{name}.json')
	def get_metadata_page(self, page = None):
		thesis_dict = self.thesis_dict	
		pages_n = list(thesis_dict.keys())
		n_page = len(pages_n)
		if page is not None:
			n_page = page

		all_metadata = pd.DataFrame()
		all_errors = {}

		for page in tqdm(range(n_page)):
			all_metadata_in_page = pd.DataFrame()

			all_errors_in_page = []
			a_error = all_errors_in_page.append
			thesis_in_page = thesis_dict[pages_n[page]]
			for thesis in tqdm(thesis_in_page):
				try:
					metadata = self.get_metadata(thesis)
					all_metadata_in_page = pd.concat([all_metadata_in_page , metadata])
				except:
					a_error(thesis)
				

			self.save_metadata(all_metadata_in_page.reset_index(), str(pages_n[page]))

			try:
				all_metadata = pd.concat([all_metadata, all_metadata_in_page])
			except: 
				all_errors[pages_n[page]] = all_errors_in_page
			
		try:
			self.save_metadata(all_metadata.reset_index(), '00_all_pages_metadata')
		except:
			try:
				errors_df = pd.DataFrame(all_errors)
				self.save_metadata(errors_df, '00_all_pages_fail', True)
			except:
				pass
			
		return all_metadata, all_errors



# url_collection = 'https://tesis.pucp.edu.pe/repositorio/handle/20.500.12404/6'
# # a = url_collection.split('/repositorio')
# a = ThesisPeru(url_collection)
# b = a.get_pages_url().get_dict_page(2)

# print('download files')
# all_, error = b.get_metadata_page()
