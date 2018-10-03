# 一、把取得的html純文字送給BeautifulSoup，產生BeautifulSoup類別
from bs4 import BeautifulSoup
import requests
re = requests.get("https://www.crummy.com/software/BeautifulSoup/bs4/doc/")
soup = BeautifulSoup(re.text, features="html.parser")
# 二、找到element
## 透過tag名稱尋找元素(第一個，回傳一個元素類別)
elem = soup.find('a')
print(elem)
print("----------------------------------")
## 透過tag名稱尋找元素(全部，回傳一個元素類別「陣列」)
elems = soup.find_all('a')
for elem in elems:
    print(elem)
print("----------------------------------")
## 透過selector尋找元素(回傳一個元素類別「陣列」)
selector = "#quick-start > h1"
elem = soup.select(selector)
print(elem)
print("----------------------------------")
# 三、取出element中的重要資訊
## 取出element特定attribute的值
elem = soup.find('a')
print(elem)
print(elem['href']) ##方法一
print(elem.get('href'))  ##方法二
print("----------------------------------")
## 取出一對tag間的文字
selector = "#quick-start > h1"
elem = soup.select(selector)
print(elem[0])
print(elem[0].text)
print("----------------------------------")
## 取得整個網頁的所有文字)
print(soup.get_text())
print("----------------------------------")