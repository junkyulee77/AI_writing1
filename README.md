# 키워드별 실시간 웹크롤링 및 AI단문글쓰기
<br>

## 목차<br>
개요 및 목표<br>
전체 프로세스<br>
데이터수집(web-crawling)<br>
데이터파싱/학습<br>
문장생성<br>
Web-page(Flask)<br>
Prerequisites<br>
<br>

## 개요 및 목표<br>
### 개요<br>
하나의 주제에 대해서 글을 쓸 때 개인의 생각만으로는 적합한 표현이 떠오르지 않아 고심할 때가 많음<br>
인터넷에는 해당 주제에 대해 다양한 방식으로 표현한 컨텐츠가 많이 있어, 이를 활용하여 짧은 글을 쓸 수 있도록 함<br>
<br>
### 목표<br>
주어진 주제(대분류 + 중분류 + 소분류)에 대한 컨텐츠를 실시간 수집<br>
해당 컨텐츠 문장 구성을 실시간 학습<br>
학습한 내용을 기반으로 해당 주제에 대한 새로운 문장을 생성토록 함<br>
<br>

## 전체 프로세스<br>
컨텐츠수집(web-crawling) → 컨텐츠Parsing → 문장구조학습 → 새로운문장 생성<br>
<br>

## 데이터수집(web-crawling) <br>
컨텐츠는 ‘네이버 블로그’에서만 수집하는 것으로 함<br>
- URL pattern: https://search.naver.com/search.naver?query=검색어&nso=&where=view&sm=tab_nmr&mode=normal&start=스타트페이지번호‘
 <br>
 <br>
 
 requests, BeautifulSoup package 활용<br>
 - r = requests.get(url) <br>
 - soup = BeautifulSoup(r.text, 'html.parser', from_encoding='utf-8') <br>
 - 네이버 검색페이지 구조는 별도 분석 필요<br>
 <br>
 
수집한 컨텐츠를 dict 형태로 저장 (contents.dict)<br>
 - pickle, gzip으로 용량 최소화<br>
 - 추후 category, keyword별로 contents 조회, DB로 구성할 수도 있음<br>
 <br>
 
 ## 데이터파싱/학습<br>
저장해놓은 contents.dict 파일을 로드하여 파싱 및 학습<br>
- 구조분석을 서론(begin)-본론(middle)-결론(end)로 하면 좀 더 연결성 있는 문장 생성도 가능 (여기서는 구분없이-모두 middle 단문만 생성)<br>
<br>
파싱 및 학습<br>
- 앞 2개 단어 뒤에 나올 수 있는 연결단어를 저장. 확률값으로 뒤에 올 수 있는 단어 선택<br>
※ 엄격한 의미에서 Neural Net 이용하는 AI 방식은 아니지만, 적은 데이터로도 실제 사용된 문장 표현 가능<br>
<br>
학습한 내용도 dict type으로 파일로 저장 (확장자는 .model)<br>
- category별로 저장 (맛집.model, 여행.model)<br>
<br>

 ## 문장생성<br>
대분류(category)+중분류(search)+소분류(keyword)에 따라 맞춤 생성<br>
- 시작 단어 random choice- 연결 가능한 단어목록(candidate words) 추출 및 random choice<br>
<br>
설정한 문장 길이에 도달 + END_OF_SENTS 도달시까지 문장 생성<br>
- END_OF_SENTS = ['.', '!', '?', '~', '다', '당', '요', '용', '죠', '죵', '여', '쥬', '됨']<br>
  ※ 인터넷/블로그에는 비문 표현이 많아서 이에 대한 대응 필요<br>
  <br>

## Web-page (Flask)<br>
Flask(python web framework)를 이용하여 웹(localhost)에서 구동<br>
<br>

## Prerequisites<br>
flask<br>
requests, bs4<br>
random<br>
ThreadPool<br>



  


