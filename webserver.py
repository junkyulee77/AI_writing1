

# /usr/bin/env python


from flask import Flask, request, render_template, session, redirect, url_for, send_file
import os, gzip, pickle
import json
import random
import datetime
from multiprocessing.pool import ThreadPool


import crawler                      # keyword에 따라 web-crawling
import parsing_module as parser     # web contents를 parsing하여 구조파악(학습)  :  python 기본 모듈에 parser가 있어서 파일명 다르게 표시
import writer                       # 학습된 내용을 조합하여 글 생성
import utils





# ==================================================================================
app = Flask(__name__)
app.secret_key = 'any random string'
with app.app_context():
    print(app.name)




# Load Models : 이전에 저장되었던 category별 모델 로징
MODEL_MANAGER = {}
try:
    with open('./config.json', 'rb') as f:
        config = json.loads(f.read().decode())
    # -----------------------------------------------
    category_list = config.get('category_list')
    if len(category_list) > 0:
        for category in category_list:
            try:
                print(category)
                category_dic = utils.load_data('models/{}.model'.format(category))
                if category_dic is None:
                    category_dic = {
                        'category': category,
                        'contents': {'begin': {}, 'middle': {}, 'end': {}},
                        'urls': []
                    }
            except Exception as ex:
                print(str(ex))
                category_dic = {
                    'category': category,
                    'contents': {'begin': {}, 'middle': {}, 'end': {}},
                    'urls': []
                }
            MODEL_MANAGER.update({category: category_dic})
except Exception as ex:
    print(str(ex))




# ==================================================================================
# Main / index
@app.route("/")
def index():
    return redirect(url_for('write'))
    # return render_template('index.html', title='ai_writer')




@app.route("/write", methods=['GET', 'POST'])
def write():
    message = ''
    selected_category, search, keywords, length_write = '', '', '', 100
    writing = ''
    #
    try:
        with open('./config.json', 'rb') as f:
            config = json.loads(f.read().decode())
        # -----------------------------------------------------------------------------------------------------------
        category_list = config.get('category_list')
        now = datetime.datetime.now()
        now_date = now.strftime('%Y-%m-%d')
        tomorrow = (now + datetime.timedelta(days=1)).strftime('%Y-%m-%d')
        now_str = now.strftime('%Y-%m-%d %H:%M:%S')
        #
        # -------------------------------------------------------------------------------------------------------
        if request.method == 'POST':
            action_type = request.form['action_type'].strip()
            #
            selected_category = request.form['category_list'].strip()
            search = request.form['search'].strip()
            search = search.split(',')[0]
            keywords = request.form['keywords'].strip()
            filter_words = ''
            try:
                length_write = int(request.form['length_write'].strip())
            except:
                length_write = 100
            #
            print(selected_category, search, keywords, length_write)
            keyword_splits = keywords.split(',')
            # ===========================================================================================
            if action_type == '문서생성':      # - 글쓰기 (search, keyword, filter_words)
                if search == '':
                    return render_template('index.html',
                                           category_list=category_list, selected_category=selected_category,
                                           search=search, keywords=keywords, length_write=length_write,
                                           writing=writing,
                                           message="검색어는 필수입력 항목입니다.")
                #
                # ------------------------------------------------------------------------
                keyword_index = random.randint(0, len(keyword_splits) - 1)
                #
                pool = ThreadPool(processes=1)
                async_result = pool.apply_async(
                    writer.writing,
                    (
                        selected_category, search, keyword_splits[keyword_index],
                        filter_words, length_write, 3, './',
                        MODEL_MANAGER
                    )
                )  # Tuple of args for foo
                #
                # print(async_result)
                writing = async_result.get()  # get the return value from your function.
                writing = writing.replace('\u200b', '')
                if writing.strip() == '':
                    writing = '적합한 원고가 생성되지 않았습니다. 다시 시도해 주세요.'
                print('writing:', len(writing))
            # -----------------------------------------------------------------------------------------
            elif action_type == '학습하기':         # category, search, keywords에 따라 학습
                print(selected_category, search, keyword_splits)
                #
                # ---------------------------------------------------------------------------------------
                # 1. 수집하기
                for keyword in keyword_splits:
                    crawler_instance = crawler.crawler(selected_category, search, keyword, page_num=3)
                    crawler_instance.collecting()
                #
                # ---------------------------------------------------------------------------------------
                # 2. 학습하기
                if selected_category != '' and search != '' and keyword_splits != []:
                    try:
                        parser_instance = parser.parser(selected_category, search_list=[search], keyword_list=keyword_splits,
                                               data_path='./', min_len=10, from_new=False, MODEL_MANAGER=MODEL_MANAGER)
                        parser_instance.daemon = True
                        parser_instance.start()
                    except Exception as ex:
                        print(str(ex))
                else:
                    message = '학습하려면 카테고리, 검색어, 키워드를 모두 설정하여야 합니다.'
        # -----------------------------------------------------------------------------------------
        # Default
        if selected_category == '':
            selected_category = category_list[0]
        #
        print(category_list, selected_category)
        return render_template('index.html',
                               category_list=category_list, selected_category=selected_category,
                               search=search, keywords=keywords, length_write=length_write,
                               writing=writing, message=message)
        # -----------------------------------------------------------------------------------------
    except Exception as ex:
        print(str(ex))
        return render_template('index.html',
                               selected_category=selected_category, search=search, keywords=keywords,
                               length_write=length_write, writing=writing,
                               message="알 수 없는 오류가 발생하였습니다.")




# ===================================================================================
# Flask web 실행
if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5001)        # localhost
    # ---------------------------------------
    # 종료되면
    print('\nGood Bye~\n\n')




# 일반용
# nohup python webserver.py   output.log 2&1


