import requests
import time
url = "http://cid.acad.ncku.edu.tw/files/14-1056-54086,r677-1.php?Lang=zh-tw"
contextLi = []
i=0
while i < 10:
    re = requests.get(url)
    re.encoding = 'utf8'
    contextLi.append(re.text)
    i += 1
    print(i , " succeed")
    time.sleep(2)
print("this is the first requests----------------------------------\n", contextLi[0])
print("this is the last requests----------------------------------\n",contextLi[-1])