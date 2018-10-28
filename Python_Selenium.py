from selenium import webdriver
import time

chrome_path = "D:\PycharmProjects\selenium_driver_chrome\chromedriver.exe" #chromedriver.exe執行檔所存在的路徑
driver = webdriver.Chrome(chrome_path) # 如果你沒有把webdriver放在同一個資料夾中，必須指定位置給他
driver.get("https://timetable.nctu.edu.tw/")
def tryclick(driver, selector, count=0): ##保護機制，以防無法定位到還沒渲染出來的元素
    try:
        elem = driver.find_element_by_css_selector(selector)
        # elem = driver.find_element_by_xpath(Xpath)  # 如果你想透過Xpath定位元素
        elem.click() # 點擊定位到的元素
    except:
        time.sleep(2)
        count+=1
        if(count <2):
            tryclick(driver, selector,count)
        else:
            print("cannot locate element" + selector)
tryclick(driver, "#flang > option:nth-child(2)") # 設定成中文
tryclick(driver, "#crstime_search") # 點擊「檢索」按鍵
time.sleep(3) # 等待javascript渲染出來，當然這個部分還有更進階的作法，關鍵字是implicit wait, explicit wait，有興趣可以自己去找
html = driver.page_source # 取得html文字
driver.close()  # 關掉Driver打開的瀏覽器
print(html)
