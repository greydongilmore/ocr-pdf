#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul  7 05:55:10 2021

@author: greydon
"""
import os
import glob
import pandas as pd
import re
import argparse
import subprocess
from pdfminer.pdfpage import PDFPage


def sorted_nicely(data, reverse = False):
	convert = lambda text: int(text) if text.isdigit() else text
	alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
	
	return sorted(data, key = alphanum_key, reverse=reverse)

def get_pdf_searchable_pages(fname):
	searchable_pages = []
	non_searchable_pages = []
	page_num = 0
	with open(fname, 'rb') as infile:
		for page in PDFPage.get_pages(infile):
			page_num += 1
			
			if 'Font' in page.resources.keys():
				searchable_pages.append(page_num)
			elif 'XObject' in page.resources.keys():
				if any("im" in x.lower() for x in list(page.resources.get("XObject", {}))):
					searchable_pages.append(page_num)
				else:
					non_searchable_pages.append(page_num)
			else:
				non_searchable_pages.append(page_num)
	
	return searchable_pages,non_searchable_pages

def run_command(cmdLineArguments):
	process = subprocess.Popen(cmdLineArguments, stdout=subprocess.PIPE, shell=True, stderr=subprocess.PIPE)
	stdout = process.communicate()[0]
	p_status = process.wait()

debug=False

if debug:
	class Namespace:
		def __init__(self, **kwargs):
			self.__dict__.update(kwargs)
	
	pdf_storage_path = r'/home/greydon/Zotero/storage'
	args = Namespace(pdf_storage_path=pdf_storage_path)

def main(args):
	
	file_info = {'title':[],'path':[],'searchable':[]}
	cnt=1
	num_files=len(glob.glob(os.path.join(args.pdf_storage_path, '**','*.pdf'), recursive = True))
	for ifile in glob.glob(os.path.join(args.pdf_storage_path, '**','*.pdf'), recursive = True):
		try:
			searchable,nonsearch=get_pdf_searchable_pages(ifile)
			
			file_info['title'].append(os.path.basename(ifile).split('.pdf')[0].strip())
			file_info['path'].append(ifile)
			file_info['searchable'].append(True if len(searchable) > len(nonsearch) else False)
		except Exception as e:
			print(e)
			file_info['title'].append(os.path.basename(ifile).split('.pdf')[0].strip())
			file_info['path'].append(ifile)
			file_info['searchable'].append(True)
		
		print(f"Finished scanning {cnt} of {num_files}")
		cnt+=1
	
	file_info=pd.DataFrame(file_info)
	
	print(f"\nFound {file_info[file_info['searchable']==False].shape[0]} PDF files to convert...\n")
	
	cnt=1
	for index,row in file_info[file_info['searchable']==False].iterrows():
		
		print(f"Converting {cnt} of {len(file_info[file_info['searchable']==False])}: {os.path.basename(row['path'])}")
		
		ocr_cmd=' '.join(['ocrmypdf',
					  f"'{row['path']}'",
					  f"'{row['path']}'"
					  ])
		
		run_command(ocr_cmd)
		
		cnt+=1
	
	print('Finished converting all PDF files in directory.')

if __name__ == "__main__":
	# Input arguments
	parser = argparse.ArgumentParser()
	parser.add_argument('-i', '--pdf_storage_path', help='Path to where Zotero stores PDF files.', required=True)
	args = parser.parse_args()

	main(args)
	