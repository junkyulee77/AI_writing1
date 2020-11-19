


import os
import numpy as np
import json
import shutil
import threading


import utils






# =================================================================================================
# Background에서 지속적으로 돌아가야 할 수도 있어서 thread로 처리
class parser(threading.Thread):
    def __init__(self, category, search_list=[], keyword_list=[], data_path='./', min_len=10, from_new=False, MODEL_MANAGER=None):
        threading.Thread.__init__(self)
        self.category = category
        self.search_list = search_list
        self.keyword_list = keyword_list
        #
        self.data_path = data_path
        self.min_len = min_len
        self.from_new = from_new
        self.MODEL_MANAGER = MODEL_MANAGER
    #
    def run(self):
        self.parsing()
    #
    def parsing(self):
        try:
            # ----------------------------------------------------------------------------------
            search_list = self.search_list
            keyword_list = self.keyword_list
            print('parsing(): search_list:', search_list, ', keyword_list:', keyword_list, ', category:', self.category)
            # ------------------------------------------------------------------------
            # Search
            contents = utils.load_data('contents.dict')
            # search_list = contents.get(self.category).get('search_list')
            search_list = list(contents.get(self.category).keys())
            #
            # ------------------------------------------------------------------------
            try:
                if self.from_new is True:
                    category_dic = {
                        'category': self.category,
                        'contents': {'begin': {}, 'middle': {}, 'end': {}},
                        'urls': []
                    }
                else:
                    category_dic = self.MODEL_MANAGER.get(self.category)
                    if category_dic is None:
                        category_dic = {
                            'category': self.category,
                            'contents': {'begin': {}, 'middle': {}, 'end': {}},
                            'urls': []
                        }
            except Exception as ex:
                error = 1
                category_dic = {
                    'category': self.category,
                    'contents': {'begin': {}, 'middle': {}, 'end': {}},
                    'urls': []
                }
            #
            print('parsing(): category_dic', category_dic)
            structures = category_dic.get('contents')
            if structures is None or structures is {}:
                structures = {'begin': {}, 'middle': {}, 'end': {}}
                category_dic.update({'contents': structures})
            #
            print('parsing(): structures', structures)
            # ---------------------------------------------------------------------------------------
            # parsed_urls = category_dic.get('urls')
            for s in range(len(search_list)):       # s % 20 == 0 => 저장
                search = search_list[s]
                # ------------------------------------------------------------------------------------------
                # Keywords
                keyword_list = contents.get(self.category).get(search).get('keyword_list')
                print('parsing(): keyword_list', keyword_list)
                #
                try:
                    raw_text_list = contents.get(self.category).get(search).get('content_list')
                    print('parsing(): raw_text_list', len(raw_text_list))
                    #
                    # Structures: Begin - Middle - End
                    print('......search:', search, ', num_text_list:', len(raw_text_list))
                    # for r in range(len(raw_text_list)):
                    for r in range(len(raw_text_list)):
                        raw_text = raw_text_list[r]
                        #
                        # Middle
                        self._set_content_structure(structures['middle'], raw_text, search, keyword_list, self.min_len)
                except Exception as ex:
                    error = 1
                #
                self.MODEL_MANAGER.update({self.category: category_dic})
                if s % 100 == 0:
                    utils.save_data(category_dic, self.data_path + 'models/{}.model'.format(self.category))
            #
            # 전체 search_list 를 다 돌려보려면 시간너무 오래 걸림
            utils.save_data(category_dic, self.data_path + 'models/{}.model'.format(self.category))
            print('learning DONE!')
        except Exception as ex:
            error = 1
    #
    def _set_content_structure(self, gubun_dic, gubun_text, search, keyword_list, min_len=10):
        parag_str_list = []
        while True:
            # ------------------------------------------------------
            # p_index = gubun_text.find('\n\n')     # => 문단별
            p_index = gubun_text.find('\n')     # => 문장별
            # ------------------------------------------------------
            if p_index == -1:  # 마지막 paragragph
                parag_str = gubun_text
                if parag_str == '':
                    break
                parag_str_list.append(parag_str)
                break
            # ------------------------------------------------------
            # Paragraph 단위별
            parag_str = gubun_text[: p_index].strip()
            if parag_str != '':
                parag_str_list.append(parag_str)
            gubun_text = gubun_text[p_index + 1: ].strip()
        #
        # End of while
        for p in range(len(parag_str_list)):
            parag_str = parag_str_list[p]
            #
            for keyword in keyword_list:    # 앞 뒤 문장 연결
                if keyword in parag_str:
                    parag_str_from_to = ''
                    if p > 1:
                        parag_str_from_to = parag_str_from_to + ' ' + parag_str_list[p - 2]
                    if p > 0:
                        parag_str_from_to = parag_str_from_to + ' ' + parag_str_list[p - 1]
                    parag_str_from_to = parag_str_from_to + parag_str
                    if p < len(parag_str_list) - 2:
                        parag_str_from_to = parag_str_from_to + ' ' + parag_str_list[p + 1]
                    if p < len(parag_str_list) - 3:
                        parag_str_from_to = parag_str_from_to + ' ' + parag_str_list[p + 2]
                    # -----------------------------------------------------------------------------
                    words = []
                    for word in parag_str_from_to.split(' '):
                        if word not in ['']:
                            words.append(word)
                    #
                    if len(words) >= min_len:
                        # print('{}+{}'.format(search.lower(), keyword.lower()))
                        keyword_dic = gubun_dic.get('{}+{}'.format(search.lower(), keyword.lower()))
                        if keyword_dic is None:
                            keyword_dic = {2: {'start': []}, 3: {'start': []}}
                            gubun_dic.update({'{}+{}'.format(search.lower(), keyword.lower()): keyword_dic})
                        #
                        for depth in range(3, 4):       # 2, 3
                            start_words = keyword_dic.get(depth).get('start')
                            unique_start_num = len(np.unique(start_words))
                            starts_cnt = start_words.count(words[: depth])
                            # print(unique_start_num, starts_cnt)
                            if starts_cnt <= unique_start_num:
                                start_words.append(words[: depth])
                            # ------------------------------------------------------------------
                            for w in range(len(words) - depth + 1):
                                short_words_key = words[w]
                                for d in range(1, depth - 1):
                                    short_words_key = short_words_key + '_' + words[w + d]
                                short_words_list = keyword_dic[depth].get(short_words_key)
                                if short_words_list is None:
                                    short_words_list = []
                                    keyword_dic[depth].update({short_words_key: short_words_list})
                                unique_words_num = len(np.unique(short_words_list))
                                words_cnt = short_words_list.count(words[w + depth - 1])
                                if words_cnt <= unique_words_num:
                                    short_words_list.append(words[w + depth - 1])



