

import os
import copy
import numpy as np
import pandas as pd
import random
import time
import json



import utils



END_OF_SENTS = ['.', '!', '?', '~', '다', '당', '요', '용', '죠', '죵', '여', '쥬', '됨']




# =================================================================================================
def writing(category, search, keyword, filter_words, length=100, depth=3, data_path='./', MODEL_MANAGER=None):
    if category == '':
        return
    # -----------------------------------------------------------------
    try:
        category_dic = MODEL_MANAGER.get(category)
        start_list = []
        # -----------------------------------------------------------------
        key_splits = keyword.split('_')
        if len(key_splits) == 1:
            gubun = 'middle'
        elif len(key_splits) == 2:
            gubun = key_splits[0]
            keyword = key_splits[1]
        filter_splits = filter_words.split(',')
        #
        # -----------------------------------------------------------------------------------------
        # START
        candidates = []
        try:
            if search != '':
                candidates = category_dic.get('contents').get(gubun).get('{}+{}'.format(search.lower(), keyword.lower())).get(depth).get('start')  # 3(N)단어 목록
                candidates = copy.deepcopy(candidates)
        except Exception as ex:
            error = 1
        #
        # print(search, keyword, len(candidates))
        if candidates is None or candidates == []:
            return '- 컨텐츠 추가 수집 후 제공 가능합니다. -'
        for filter in filter_splits:
            if filter in candidates:
                candidates.remove(filter)
        # ---------------------------------------------------------------------------------------
        start = utils.randomChoice(candidates)    # 3(N)단어
        print('start_candidates:', start, len(candidates))
        start_list.append(start)
        generated = start
        #
        next_key = start[-1]
        for i in range(2, depth):
            next_key = start[-i] + '_' + next_key     # 뒤 (n - 1)단어
        previous_key = next_key
        #
        # -----------------------------------------------------------------------------------------
        cnt = 0
        gen_str = ''
        no_candidates = 0
        while True:
            cnt += 1
            if cnt >= 50:
                break
            # -------------------------------------------------------------------------------------
            candidates = []
            try:
                if search != '':
                    candidates = category_dic.get('contents').get(gubun).get('{}+{}'.format(search.lower(), keyword.lower())).get(depth).get(next_key)
                    candidates = copy.deepcopy(candidates)
            except Exception as ex:
                error = -1
            #
            print('\tcandidates:', len(candidates))
            if candidates is None:
                candidates = []
            for filter in filter_splits:
                if filter in candidates:
                    candidates.remove(filter)
            if candidates == []:
                if depth == 3:  # => depth 2도 점검 (다양성은 증가하나 정확도 떨어짐)
                    #
                    if candidates is None:
                        candidates = []
                    for filter in filter_splits:
                        if filter in candidates:
                            candidates.remove(filter)
                    #
                    if len(candidates) == 0:
                        next_key = previous_key
                        no_candidates += 1
                        if len(generated) == 3 or (len(generated) > 3 and no_candidates >= 3):     # start
                            try:
                                if search != '':
                                    start_candidates = category_dic.get('contents').get(gubun).get('{}+{}'.format(search.lower(), keyword.lower())).get(depth).get('start')  # 3(N)단어 목록
                                    start_candidates = copy.deepcopy(start_candidates)
                            except Exception as ex:
                                error = 1
                            if start_candidates == []:
                                continue
                            # -------------------------------------------------------------------------------------
                            for filter in filter_splits:
                                if filter in start_candidates:
                                    start_candidates.remove(filter)
                            for start_cand in start_candidates:
                                if start_cand in start_list:
                                    start_candidates.remove(start_cand)
                            #
                            new_start = utils.randomChoice(start_candidates)  # 3(N)단어
                            start_list.append(new_start)
                            generated += new_start
                            #
                            next_key = new_start[-1]
                            for i in range(2, depth):
                                next_key = new_start[-i] + '_' + next_key  # 뒤 (n - 1)단어
                            previous_key = next_key
                            no_candidates = 0
                            continue
                        #
                        elif len(generated) > 3:      # start가 아닌 경우
                            generated = generated[: -1]
                            next_key = previous_key
                            continue
            # ------------------------------------------------------------------------------------------------------
            if candidates is None or candidates == []:
                continue
            selected = utils.randomChoice(candidates)
            if '.' in selected:
                selected_splits = selected.split('.')
                selected = selected_splits[0] + '.'
            #
            generated.append(selected)
            gen_str = generated[0]
            for i in range(1, len(generated)):
                gen_str = gen_str + ' ' + generated[i]
            # -----------------------------------------------------------------------------
            # print('\tnext_key:', next_key, ', candidates:', len(candidates), selected, ', len_gen_str:', len(gen_str))
            if len(gen_str) >= int(length * 0.8) and selected[-1] in END_OF_SENTS:
                print(selected[-1], len(gen_str))
            if len(gen_str) >= int(length * 2):
                print(length, len(gen_str))
            if (len(gen_str) >= int(length * 0.8) and selected[-1] in END_OF_SENTS) or len(gen_str) >= int(length * 2):
                break
            # -----------------------------------------------------------------------------
            if selected[-1] in END_OF_SENTS:    # 새로운 start
                start_candidates = category_dic.get('contents').get(gubun).get('{}+{}'.format(search.lower(), keyword.lower())).get(depth).get('start')  # 3(N)단어 목록
                start_candidates = copy.deepcopy(start_candidates)
                for start_cand in start_candidates:
                    if start_cand in start_list:
                        start_candidates.remove(start_cand)
                # --------------------------------------------------------
                if start_candidates == []:   # 더 이상 시작 문구가 없을때
                    print('\tNO Start Word')
                    break
                # --------------------------------------------------------
                start = utils.randomChoice(start_candidates)  # 3(N)단어
                # print('new_start:', start)
                start_list.append(start)
                generated += start
                #
                next_key = start[-1]
                for i in range(2, depth):
                    next_key = start[-i] + '_' + next_key  # 뒤 (n - 1)단어
                previous_key = next_key
            # -----------------------------------------------------------------------------
            else:
                previous_key = next_key
                next_key_split = next_key.split('_')
                next_key = selected
                for i in range(1, depth - 1):
                    next_key = next_key_split[-i] + '_' + next_key  # 뒤 (n - 1)단어
        #
        return gen_str
        #
    except Exception as ex:
        error = 1
        return ''

