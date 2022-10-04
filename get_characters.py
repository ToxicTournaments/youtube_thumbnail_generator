from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import requests
from PIL import Image

chromeOptions = Options()
# chromeOptions.add_argument('--headless')
chromeOptions.add_argument('--disable-gpu')
driver = webdriver.Chrome(
    ChromeDriverManager().install(), options=chromeOptions)
driver.get("https://www.mariowiki.com/Gallery:Super_Smash_Bros._Ultimate")

img_links = []
names = []


def save_image(title, image_link):

    path = './characters/'
    path = path + title.replace(' ', '_').replace(',',
                                                  '').replace(':', '').replace('?', '').replace("'", '').replace('-', '') + '.png'
    # path = path.replace('t_editorial_landscape_mobile',
    #                     't_editorial_landscape_3_4_desktop_3x').replace('t_thumb_squared', 't_editorial_landscape_3_4_desktop_3x').replace('t_lazy/', '')

    Image.open(requests.get(
        image_link, stream=True).raw).convert('RGBA').save(path)

    return path


elements = driver.find_elements(
    'xpath', '//*[@id="mw-content-text"]/table/tbody/tr/td[2]/div/ul[2]/li')

for element in elements:
    names.append(element.text[3:])
    img_links.append(element.find_element(
        'tag name', 'a').get_attribute('href'))

for i, img_link in enumerate(img_links):
    print(i)
    if (i == 37):
        continue
    if (i == 38):
        continue
    if (i == 57):
        continue
    if (i == 88):
        continue

    driver.get(img_link)
    save_image(names[i], driver.find_element(
        'xpath', '//*[@id="mw-content-text"]/table/tbody/tr/td/div[2]/p/a').get_attribute('href'))
