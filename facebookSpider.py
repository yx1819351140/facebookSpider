import json
import requests
from selenium.webdriver import ChromeOptions, Chrome, FirefoxOptions, Firefox
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from utils import format_path, md5_string, format_pub_time
from settings import FACEBOOK_EXCEL_PATH, FILTER_PATH, IMAGE_PATH, DATA_PATH, DRIVER_PATH, PROXY, PAGE
from lxml import etree
import openpyxl
import logging
import time
"""
facebook用户主页采集，使用geckodriver，需要与火狐浏览器版本对应，如果火狐浏览器自动更新，代码报错，需要重新下载geckodriver
下载地址:https://github.com/mozilla/geckodriver/releases
如果地址打不开自行百度geckodriver下载
下载完成后存放到任意路径，更新配置文件中driver地址
"""


class FacebookSpider(object):

    def __init__(self):
        book = openpyxl.load_workbook(format_path(FACEBOOK_EXCEL_PATH))
        sheet = book.active
        self.url_list = []
        self.name_list = []
        for i in range(sheet.max_row):
            url = sheet['A'][i].value
            if url:
                self.url_list.append(url)
            name = sheet['B'][i].value
            if name:
                self.name_list.append(name)
        # options = ChromeOptions()
        options = FirefoxOptions()

        options.add_argument(f'--proxy-server=http://{PROXY}')
        options.add_argument('--headless')
        # options.add_argument('--disable-gpu')
        # options.add_argument('--no-sandbox')
        # options.add_argument('--disable-dev-shm-usage')
        # # 跳过webdriver检测  以键值对的形式加入参数
        # options.add_experimental_option('excludeSwitches', ['enable-automation'])
        # options.add_experimental_option('useAutomationExtension', False)
        # options.add_argument("--disable-blink-features=AutomationControlled")

        # 指定driver地址，如果配置了环境变量可以不指定
        self.driver = Firefox(options=options, executable_path=DRIVER_PATH)
        # self.driver = Chrome(options=options)
        with open(FILTER_PATH, 'a+') as f:
            self.crawled_id_list = f.readline()
        self.proxies = {'https': PROXY, 'http': PROXY}
        self.logger = logging.getLogger(__name__)

    def start_request(self):
        for i in range(len(self.url_list)):
            url = self.url_list[i]
            name = self.name_list[i]
            self.parse(url, name)

    def parse(self, url, name):
        try:
            self.driver.get(url)
            WebDriverWait(self.driver, 10, 0.5).until(
                EC.presence_of_element_located((By.XPATH, '//div[@aria-label="关闭"]')))
            self.driver.find_element(by=By.XPATH, value='//div[@aria-label="关闭"]').click()

            for _ in range(PAGE):
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)  # 等待页面加载

            elements = self.driver.find_elements(by=By.XPATH, value='//div[contains(text(), "展开")]')
            for element in elements:
                # ActionChains(self.driver).move_to_element(element).click().perform()
                self.driver.execute_script("arguments[0].click();", element)

            html = etree.HTML(self.driver.page_source)
            elem_list = html.xpath('//div[@class="x78zum5 x1n2onr6 xh8yej3"]')
            if elem_list:
                for elem in elem_list:
                    try:
                        content = ''
                        content_list = elem.xpath('.//div[@dir="auto"]//text()')
                        for temp_content in content_list:
                            content = content + temp_content.strip()
                        pub_time_list = elem.xpath('./div//div[@class="xu06os2 x1ok221b"]//span/a/@aria-label')
                        if pub_time_list:
                            pub_time = format_pub_time(pub_time_list[0])
                        else:
                            pub_time = ''
                        _id = md5_string(content + pub_time)
                        # 去重
                        if _id + '\n' in self.crawled_id_list:
                            break

                        img_url_list = elem.xpath('.//div[@class="xqtp20y x6ikm8r x10wlt62 x1n2onr6"]/div/img/@src')
                        img_list = []
                        if img_url_list:
                            for i in range(len(img_url_list)):
                                img_name = self.save_img(img_url_list[i], i, _id)
                                if img_name:
                                    img_list.append(img_name)
                    except:
                        continue

                    if content:
                        facebook_item = {
                            'id': _id,
                            'content': content,
                            'img': img_list,
                            'media_name': 'facebook',
                            'media_type': '社交媒体',
                            'author': name.replace(' ', ''),
                            'url': url,
                            'create_time': time.strftime('%Y-%m-%d %H:%M:%S'),
                            'pub_time': pub_time,
                        }

                        self.save_data(facebook_item)
        except Exception as e:
            self.logger.error(f'[get_facebook_data]获取facebook数据异常：{e}，url：{url}')

    def save_img(self, url, i, _id):
        try:
            file_path = f'{IMAGE_PATH}/{_id}_{i}.jpg'
            with open(file_path, 'wb') as f:
                f.write(requests.get(url, proxies=self.proxies).content)
            return f'{_id}_{i}.jpg'
        except Exception as e:
            self.logger.error(f'[save_img]保存图片异常：{e}，url：{url}')
            return ''

    def save_data(self, item):
        try:
            with open(DATA_PATH, 'a', encoding='utf-8') as f:
                f.write(json.dumps(item, ensure_ascii=False) + '\n')
            with open(FILTER_PATH, 'a', encoding='utf-8') as f:
                f.write(item['id'] + '\n')
        except Exception as e:
            self.logger.error(f'[save_data]保存结果数据异常：{e}，url：{item["url"]}')

    def run(self):
        self.start_request()
        self.driver.close()


if __name__ == '__main__':
    facebook = FacebookSpider()
    facebook.run()
    # facebook.parse('https://www.facebook.com/DeptofDefense/', '美国国防部')
