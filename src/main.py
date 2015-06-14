# -*- coding: utf-8 -*-
import importlib
from os import path, mkdir, walk
from random import choice
import threading
from time import sleep
from datetime import datetime
from shutil import rmtree

from lxml import etree, html

from sqlalchemy import *
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

import requests


from models import Food, FoodText, FoodContent
from parsers import findfood
import config as cfg
from sqlalchemy.exc import DatabaseError        

def get_files_in_directory(dir):
    filenames = []
    for r, d, f in walk(dir):
        filenames = f
    return [path.join(dir, filename) for filename in filenames]

def spice_downloader(thread_id, work_name, urls, step, dir, headers = {}):
    index = thread_id
    if not path.exists(dir):
        mkdir(dir)
    while True:
        if len(urls) > index:
            filename = '{!s}_index_page-{!s}.html'.format(work_name ,index)
            tmp_file = open(path.join(dir, filename), 'w')
            
            resp = requests.get(urls[index], headers=headers)
            resp.encoding = 'UTF-8'
            if resp.status_code != 200:
                print('got {} status_code while downloading'.format(resp.status_code))
                break
            tmp_file.write(resp.text)
              
            print('downloaded {!s}'.format(urls[index]))
            index += step
        else:
            return

def main():
    for site in cfg.SITES_FOR_PARSE:
        if not path.exists(cfg.BASE_TMP_DIR):
            mkdir(cfg.BASE_TMP_DIR)

        parser = site.Parser(200)
        
        print('Start downloading index pages')
        index_urls = parser.get_index_urls()
        for thread_id in range(cfg.MAX_WORKING_THREADS):
            t = threading.Thread(name='index_page'+str(thread_id), 
                                 target=spice_downloader, 
                                 args=[thread_id, 
                                       parser.get_work_name(), 
                                       index_urls,
                                       cfg.MAX_WORKING_THREADS, 
                                       cfg.BASE_INDEX_PAGES_DIR,
                                       {'User-Agent': choice(cfg.USER_AGENTS)}])
            t.start()
        while threading.active_count() > 1:
            sleep(0.5)
        print('Finish downloading index pages')
         
         
        filenames = get_files_in_directory(cfg.BASE_INDEX_PAGES_DIR)
        print('...parse index pages...')
        content_urls = parser.get_content_urls(filenames)
        print('Start downloading content pages')  
        for thread_id in range(cfg.MAX_WORKING_THREADS):
            t = threading.Thread(name='context_page'+str(thread_id), 
                                 target=spice_downloader, 
                                 args=[thread_id, 
                                       parser.get_work_name(), 
                                       content_urls, 
                                       cfg.MAX_WORKING_THREADS, 
                                       cfg.BASE_CONTENT_PAGES_DIR, 
                                       {'User-Agent': choice(cfg.USER_AGENTS)}])
                
            t.start()
        while threading.active_count() > 1:
            sleep(0.5)
        print('Finish downloading content pages')
         
        print('Start parsing and add content to base')
          
        engine = create_engine(cfg.MYSQL_CONNECTION+'/?charset=utf8', echo=False, encoding='utf8')
        try:
            engine.execute('USE {}'.format(cfg.MYSQL_DBNAME))
        except:
            print('"{}" database does not exist'.format(cfg.MYSQL_DBNAME))
            raise
        Session = sessionmaker(bind=engine)
        session = Session()
          
        filenames = get_files_in_directory(cfg.BASE_CONTENT_PAGES_DIR)
        for content in parser.get_content(filenames, session):            
            session.add(content)
            
        # TODO: fix single query
        try:
            session.commit()
        except Exception, error:
            print(error)
            continue
        print('Finish parsing and add content to base')
         
        print('...cleaning...')
        rmtree(cfg.BASE_TMP_DIR)
 
if __name__ == '__main__':
    main()