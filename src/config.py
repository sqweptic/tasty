# -*- coding: utf-8 -*-
from os import path
from parsers import empty_parse, empty2_parse

MYSQL_CONNECTION = 'mysql://spice_user:123pass@192.168.2.2'
MYSQL_DBNAME = 'yummy'

BASE_TMP_DIR = '_TMP_'
BASE_INDEX_PAGES_DIR = path.join(BASE_TMP_DIR, 'INDEX_PAGES')
BASE_CONTENT_PAGES_DIR = path.join(BASE_TMP_DIR, 'CONTENT_PAGES')

MAX_CONTENT_PAGES = 500

MAX_WORKING_THREADS = 7

USER_AGENTS = ['Mozilla/5.0 (Windows NT 6.1; WOW64; rv:24.0) Gecko/20100101 Firefox/24.0',
               'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.154 Safari/537.36',]


SITES_FOR_PARSE: = [empty_parse, empty2_parse]

for site in SITES_FOR_PARSE:
	if not site.site_url:
		print('empty site_url in {0} parser'.format(empty_parse.__name__))
		exit()