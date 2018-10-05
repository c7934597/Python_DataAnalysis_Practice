import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import jieba
from wordcloud import WordCloud
from collections import Counter
import os

# 1
# 首先我們先到iThome鐵人的首頁，把第一頁到最後一頁的網址抄下來
url = "https://ithelp.ithome.com.tw/ironman?page=1#ir-list"
res = requests.get(url)  ## 先爬下第一頁
soup = BeautifulSoup(res.text, 'lxml')
maxpage = int(soup.select('.pagination')[0].find_all('a')[-2].text)  ## 定位出最後一頁的頁數
urls = []
for i in range(maxpage):  ## 把接下來要爬的網頁準備好
    page = i + 1
    url = "https://ithelp.ithome.com.tw/ironman?page=" + str(page) + "#ir-list"  ## 大家可以觀察每一頁url的變化
    urls.append(url)

# 接著爬入每一頁，把每個文章的比賽分類，以及其網址抄下來。之所以要抄分類，是因為文章網址內部找不到分類，所以只好在這邊些記錄下來。
articles_rows = []
for idx, url in enumerate(urls):  ## enumerate這個東西很好用，請大家多多利用
    res = requests.get(url)
    soup = BeautifulSoup(res.text, 'lxml')

    articles = soup.select('.ir-list')  ## 找出該頁面的所有文章

    for article in articles:
        article_dict = {}
        group = article.select('.group-badge__name')[0].text.replace(' ', '').replace('\n', '')  ## 定位該篇文章參與比賽的參賽組別
        article_url = article.select('.ir-list__title')[0].select('a')[0]['href']  ## 紀錄該篇文章的網址
        article_dict['group'] = group
        article_dict['article_url'] = article_url
        articles_rows.append(article_dict)

    if idx % 10 == 0:  ## 讓你大概知道進度到哪了
        print(idx)


# 2
df = pd.DataFrame(articles_rows)
#df  ## 查看DataFrame的樣子

# 3
#進入到每一篇文章中擷取資訊
def ArticleContentCrawler(row):
    url = row['article_url']
    res = requests.get(url)
    soup = BeautifulSoup(res.text, 'lxml')

    ## linke count
    like_count = int(soup.select('.likeGroup__num')[0].text)  ## 定位讚的次數

    ## article header
    header = soup.select('.qa-header')[0]
    corpusinfo = header.select('h3')[0].text.replace(' ', '').replace('\n', '')
    corpus_title = corpusinfo.split('第')[0]  ## 定位文章集的的主題
    corpus_day = int(re.findall(r'第[\d]+篇', corpusinfo)[0].replace('第', '').replace('篇', ''))  ## 定位參賽第幾天

    article_title = header.select('h2')[0].text.replace(' ', '').replace('\n', '')  ## 定位文章的title
    writer_name = header.select('.ir-article-info__name')[0].text.replace(' ', '').replace('\n', '')  ## 定位作者名稱
    writer_url = header.select('.ir-article-info__name')[0]['href']  ## 定位作者的個人資訊業面

    publish_date_str = header.select('.qa-header__info-time')[0][
        'title']  ## 定位發文日期，為了讓日期的格式被讀成python的datetime，所以做了下面很瑣碎的事
    date_items = pd.Series(
        publish_date_str.split(' ')[0].split('-') + publish_date_str.split(' ')[1].split(':')).astype(int)
    publish_datetime = datetime(date_items[0], date_items[1], date_items[2], date_items[3], date_items[4],
                                date_items[5])

    browse_count = int(re.findall(r'[\d]+', header.select('.ir-article-info__view')[0].text)[0])  ## 定位瀏覽次數

    ## markdown_html
    markdown_html = soup.select('.markdown__style')[0]
    text_content = "\n".join([p.text for p in markdown_html.select('p')])  ## 定位所有文章的段落，這邊沒有爬圖片跟程式碼了
    h1 = [h1.text for h1 in markdown_html.select('h1')]  ## 定位文章的標題們
    h2 = [h2.text for h2 in markdown_html.select('h2')]
    h3 = [h3.text for h3 in markdown_html.select('h3')]
    h4 = [h4.text for h4 in markdown_html.select('h4')]
    h5 = [h5.text for h5 in markdown_html.select('h5')]
    h6 = [h6.text for h6 in markdown_html.select('h6')]

    row['like_count'] = like_count

    row['corpus_title'] = corpus_title
    row['corpus_day'] = corpus_day
    row['article_title'] = article_title
    row['writer_name'] = writer_name
    row['writer_url'] = writer_url
    row['publish_datetime'] = publish_datetime
    row['browse_count'] = browse_count

    row['text_content'] = text_content
    row['h1'] = h1 if h1 != [] else None  ## 如果是空list的話紀錄為None後面比較好處理
    row['h2'] = h2 if h2 != [] else None
    row['h3'] = h3 if h3 != [] else None
    row['h4'] = h4 if h4 != [] else None
    row['h5'] = h5 if h5 != [] else None
    row['h6'] = h6 if h6 != [] else None

    row['crawled_date'] = datetime.now()

    if int(row.name) % 50 == 0:  ## 列印出進度
        print(str(row.name) + " pages crawled!")

    return row


df = df.apply(ArticleContentCrawler, axis=1)
#df

# 4
#方案一: 存成csv檔
df.to_csv('ithomeironman.csv', index=False, encoding='utf8')
pd.read_csv('ithomeironman.csv')  ## 把檔案讀出來看看有沒有儲存成功

# 5
#方案二: 存進MongoDB
#這邊請務必先把database以及collection開好，然後我使用的是local端的MongoDB所以你電腦要裝好才有，沒有的話可以參考使用mlab，詳情見Python與MongoDB的互動
'''
from pymongo import MongoClient
conn = MongoClient()
db = conn.ithome_ironman
collection = db.articles
cursor = collection.insert_many(list(df.T.to_dict().values()))  # 這是DataFrame塞進Mongo的常見寫法
'''

# 6

'''
#6-1 來看看大家哪一天發文的長度比較長
content_length_each_day = df.groupby('corpus_day').mean()['content_length']
content_length_each_day.plot(kind='bar')
plt.show()

#6-2 各組的發文長度
content_length_each_group = df.groupby('group').mean()['content_length']
content_length_each_group.plot(kind='bar')
plt.show()
'''

#6-3 各組的的文平均瀏覽次數
browse_count_each_group = df.groupby('group').mean()['browse_count']
browse_count_each_group.plot(kind='bar')
plt.show()

#6-4 各組的的文平均讚數
like_count_each_group = df.groupby('group').mean()['like_count']
like_count_each_group.plot(kind='bar')
plt.show()

#7
#每個參賽者的比較
'''
df_group_corpus_title = df.groupby(['group', 'corpus_title'])
df_group_first = df_group_corpus_title.first()[['writer_name', 'writer_url']]
df_group_count = df_group_corpus_title.count ()[['article_url']]
df_group_mean = df_group_corpus_title.mean()[['like_count', 'browse_count', 'content_length']]
df_group_max = df_group_corpus_title.max()[['corpus_day']]
df_sorted = df_group_count.join([df_group_first, df_group_mean, df_group_max])
df_sorted.columns = ['article_count', 'writer_name', 'writer_url', 'avg_like_count', 'avg_browse_count', 'avg_article_length', 'max_corpus_day']
df_sorted = df_sorted[['avg_like_count', 'avg_browse_count', 'article_count', 'avg_article_length', 'max_corpus_day', 'writer_name', 'writer_url']]
# df_sorted.to_csv('sorted.csv')
df_sorted
'''

#8.
#各組別文字分析(全文)

with open('stops.txt', 'r', encoding='utf8') as f:
    stops = f.read().split('\n')
from string import punctuation
stops.extend(punctuation)
stops.extend(['\n', ' ', '使用', '一個'])

def tokenize(sentence):
    terms = []
    if pd.notnull(sentence):
        for term in jieba.cut(sentence):
            term = term.lower()
            if term not in stops:
                terms.append(term)
    return terms


for g in set(df['group']):
    print(g)
    df_content = df[df['group'] == g][['text_content']]
    df_content['processed'] = df_content['text_content'].apply(tokenize)
    total_terms = []
    for terms in df_content['processed']:
        total_terms.extend(terms)

    wordcloud = WordCloud(font_path="simsun.ttf", background_color='white')
    wordcloud.generate_from_frequencies(frequencies=Counter(total_terms))
    plt.figure(figsize=(10, 10))
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    plt.savefig(os.path.join('day19_pic', 'worldcloud_' + g + '_chinese'), bbox_inches='tight', pad_inches=0)
    plt.show()

#9
#各組別文字分析(英文)
for g in set(df['group']):
    print(g)
    df_content = df[df['group'] == g][['text_content']]
    df_content['processed'] = df_content['text_content'].apply(tokenize)
    english_terms = []
    for terms in df_content['processed']:
        for term in terms:
            match_eng = re.match(r'[a-z]+', term)
            if match_eng != None and match_eng.group(0) == term:
                english_terms.append(term)

    wordcloud = WordCloud(font_path="simsun.ttf", background_color='white')
    wordcloud.generate_from_frequencies(frequencies=Counter(english_terms))
    plt.figure(figsize=(10, 10))
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    plt.savefig(os.path.join('day19_pic', 'worldcloud_' + g + '_English'), bbox_inches='tight', pad_inches=0)
    plt.show()

#10
#各組別程式語言出現比例 整理出各組程式語言出現的次數
group_lang_count = {}
for g in set(df['group']):
    print(g)
    df_content = df[df['group'] == g][['text_content']]
    df_content['processed'] = df_content['text_content'].apply(tokenize)
    total_terms = []
    for terms in df_content['processed']:
        for term in terms:
            match_eng = re.match(r'[a-z]+', term)
            if match_eng != None and match_eng.group(0) == term:
                total_terms.append(term)

    langs = ["nodejs", "node", "reactjs", "react", "js",
             "python", "javascript", "ruby", 'java', 'c',
             'c#', 'angularjs', 'angular', 'typescript',
             'd3', 'd3js', 'sql', 'html', 'css', 'jquery',
             'go', 'vue', 'vuejs', 'r']

    langs = sorted(langs)

    lang_count = {}
    for lang in langs:
        count = 0
        if lang in total_terms:
            count = Counter(total_terms).get(lang)
        lang_count[lang] = count

    print(lang_count)
    group_lang_count[g] = lang_count

df_lang = pd.DataFrame(list(group_lang_count.values()), index=group_lang_count.keys())
df_lang

#11
#畫圖
for g in set(df['group']):
    df_lang.T[g].plot(kind='pie', autopct='%.2f', title=g, fontsize=10, )
    plt.title(g, fontsize=20)
    plt.savefig(os.path.join('day19_pic', 'lang_pie_' + g), bbox_inches='tight', pad_inches=0)
    plt.show()