import requests

## 這是一個很有名的，爬蟲愛好者常去挑戰的一個募資網站
url = "https://www.indiegogo.com/projects/viviva-colorsheets-the-most-portable-watercolors-painting-travel--4#/"

## 使用假header，有些網站會擋request的header，所以要用假header
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36'}

re = requests.get(url, headers=headers)
re.encoding = 'utf8'
print(re.text)