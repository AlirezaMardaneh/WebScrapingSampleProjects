import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from persiantools import digits
import pandas as pd


url = "https://www.digikala.com/search/category-mobile-phone/product-list/"
pages = 5
time_sleep = 4

options = webdriver.EdgeOptions()
options.add_argument("--start-maximized")
browser = webdriver.Edge(options=options)
browser.get(url)
time.sleep(time_sleep)

js_code = "arguments[0].scrollIntoView();"
for i in range(pages):
    elements = browser.find_elements(By.CSS_SELECTOR, "section.product-list_ProductList__banner__Mxvqm")
    if elements:
        final_element = elements[-1]
        browser.execute_script(js_code, final_element)
        time.sleep(time_sleep)

content = BeautifulSoup(browser.page_source, "html.parser")
browser.quit()
related_tags = content.css.select("div.product-list_ProductList__item__LiiNI a div article > div.grow-1 > div.grow-1")


data = []
for item in related_tags:
    name_tag = item.find("h3")
    star_tag = item.find("p", class_="text-body2-strong color-700")
    price_tag = item.find_all("span")[-1]
    name = name_tag.string.replace('\u200c', ' ') if name_tag else None
    star = float(digits.fa_to_en(star_tag.string)) if star_tag else None
    price = None
    try:
        price = float(digits.fa_to_en(price_tag.string.replace(',', '')))
    except:
        pass
    data.append({"name": name, "star": star, "price": price})

df = pd.DataFrame(data)
df["name"] = df.name.str.replace("  ", " ")

pattern = r'گوشی موبایل (?P<brand>.*) مدل (?P<model>[-\w\s/]*) (?P<sim>دو|تک) سیم کارت ظرفیت (?P<memory>.*) و رم (?P<ram>\d* گیگابایت|مگابایت)[-\s]*(?P<description>.*)'
df = pd.concat([df, df.name.str.extract(pattern)], axis=1)
