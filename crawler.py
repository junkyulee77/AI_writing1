


import os
import json
import shutil
import requests
from bs4 import BeautifulSoup
import threading



import utils




# New URL pattern
URL = 'https://search.naver.com/search.naver?query={}&nso=&where=view&sm=tab_nmr&mode=normal&start={}'




# ============================================================================================
# Background에서 지속적으로 돌아가야 할 수도 있어서 thread로 처리
class crawler(threading.Thread):
    def __init__(self, category, search, keyword, page_num):
        threading.Thread.__init__(self)
        self.category = category
        self.search = search
        self.keyword = keyword
        self.page_num = page_num
        #
        # ------------------------------------------------------------------------------------------
        # 신규데이터 여부 체크 및 저장
        self.contents = {}
        try:
            self.contents = utils.load_data('contents.dict')
            category_content = self.contents.get(category)
            if category_content is None:
                category_content = {search: {'keyword_list': [keyword], 'content_list': []}}
                self.contents.update({category: category_content})
            #
            search_content = category_content.get(search)
            if search_content is None:
                search_content = {'keyword_list': [keyword], 'content_list': []}
                category_content.update({search: search_content})
            #
            keyword_list = search_content.get('keyword_list')
            if keyword not in keyword_list:
                keyword_list.append(keyword)
        except Exception as ex:
            print(str(ex))
            self.contents.update({category: {search: {'keyword_list': [keyword], 'content_list': []}}})
        #
        utils.save_data(self.contents, 'contents.dict')
        # ------------------------------------------------------------------------------------------
    #
    def run(self):
        self.collecting()
    #
    def collecting(self):
        try:
            collect_key = '{}'.format(self.search.lower())
            if self.keyword != '':
                collect_key = collect_key + '+{}'.format(self.keyword)
            print('crawler.collecting()', self.category, self.search.lower(), self.keyword.lower(), collect_key)
            #
            # ----------------------------------------------------------------------------------
            for page in range(1, self.page_num * 10, 10):
                print(page)
                try:
                    url_key = URL.format(collect_key, page)
                    r = requests.get(url_key)
                    soup = BeautifulSoup(r.text, 'html.parser', from_encoding='utf-8')
                    #
                    a_list = soup.find_all('a')
                    for a in a_list:
                        try:
                            href = a['href']
                            classname = a['class']
                            if ('blog' in href or 'cafe' in href) and (classname[0] == 'thumb_single'):
                                r = requests.get(href)
                                soup = BeautifulSoup(r.text, 'html.parser', from_encoding='utf-8')
                                # ----------------------------------------------------------------------------------
                                p_list = soup.find_all('p')
                                contents = ''
                                if p_list != []:
                                    for p in p_list:
                                        try:
                                            if p.text != '':
                                                if len(p.text.strip()) == 0:
                                                    continue
                                                contents = contents + '\n' + p.text
                                                #
                                        except Exception as ex:
                                            error = 1
                                # --------------------------------------------------------------------------------
                                else:
                                    iframe = soup.find('iframe')
                                    href = iframe.get('src')
                                    # print('href:', href)
                                    if '/PostView.nhn?' in href:
                                        href = 'https://blog.naver.com/' + href
                                    r = requests.get(href)
                                    try:
                                        soup = BeautifulSoup(r.text, 'html.parser', from_encoding='utf-8')
                                    except Exception as ex:
                                        error = 1
                                        continue
                                    # ---------------------------------------------------------------------------
                                    p_list = soup.find_all('p')
                                    for p in p_list:
                                        try:
                                            if p.text != '':
                                                if len(p.text.strip()) == 0:
                                                    continue
                                                #
                                                contents = contents + '\n' + p.text
                                        except Exception as ex:
                                            error = 1
                                # --------------------------------------------
                                # Save Contents to 'contents.dict' (use DB if necessary)
                                content_list = self.contents.get(self.category).get(self.search).get('content_list')
                                content_list.append(contents)

                                # --------------------------------------------
                        except Exception as ex:
                            # print(str(ex))
                            error = 1
                except Exception as ex:
                    print(str(ex))
                    error = 1
            # ----------------------------------------------------------------------
            utils.save_data(self.contents, 'contents.dict')
            print('Collecting DONE!')
            # ----------------------------------------------------------------------
        except Exception as ex:
            print(str(ex))
            error = 1

