# -*- coding: utf-8 -*-
# @Time    : 2018/01/23 10:02
# @Author  : xuzy
# @Software: PyCharm
# @Function:
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.support.wait import WebDriverWait
import time
import base64
import apiutil
import random


def cal_location(word, rsp):
    try:
        if rsp['ret'] == 0:
            for i in rsp['data']['item_list']:
                result = i['itemstring'].find(word)
                if result == -1:
                    continue
                else:
                    x = i['itemcoord'][0]['x']
                    y = i['itemcoord'][0]['y']
                    width = i['itemcoord'][0]['width']
                    height = i['itemcoord'][0]['height']

                    location_x = int(x + (width / 4) * (result + 0.5))
                    location_y = int(y + height / 2)

                    return int(location_x * 23 / 20), int(location_y * 23 / 20)

            return 0, 0
    except Exception as e:
        return 0, 0


class CrackSlider():
    """
    通过腾讯OCR，识别文字位置，并计算位置相对距离，破解点击验证码
    """

    def __init__(self):
        super(CrackSlider, self).__init__()
        # 实际地址
        self.url = 'https://www.52pojie.cn/'
        self.driver = webdriver.Chrome()
        self.wait = WebDriverWait(self.driver, 30)
        self.zoom = 1

    def open(self):
        self.driver.get(self.url)
        self.driver.maximize_window()

    def recognize_image(self):
        """
        优图ocr地址，免费申请
        https://ai.qq.com/product/ocr.shtml#identify
        :return:
        """
        app_id = 'appid'
        app_key = 'app_key'
        with open('./captcha.jpg', 'rb') as bin_data:
            image_data = bin_data.read()

        ai_obj = apiutil.AiPlat(app_id, app_key)

        print('----------------------SEND REQ----------------------')
        rsp = ai_obj.getOcrGeneralocr(image_data)
        print(rsp)
        return rsp

    def get_tracks(self, distance):
        v = 0
        t = random.uniform(0.1, 0.3)
        forward_tracks = []
        current = 0
        mid = distance * 3 / 5
        while current < distance:
            if current < mid:
                a = 2
            else:
                a = -3
            s = v * t + 0.5 * a * (t ** 2)
            v = v + a * t
            current += s
            forward_tracks.append(round(s))

        return {'forward_tracks': forward_tracks}

    def crack_slider(self):
        try:
            self.open()
            captcha = 'captcha.jpg'

            self.driver.find_element_by_xpath('//input[@id="ls_username"]').send_keys('你的用户名')
            self.driver.find_element_by_xpath('//input[@id="ls_password"]').send_keys('你的密码!')
            self.driver.find_element_by_xpath('//button[@class="pn vm"]').click()

            distance = 260
            tracks = self.get_tracks((distance + 2) * self.zoom)  # 对位移的缩放计算

            time.sleep(2)
            # slider = self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'nc_iconfont btn_slide')))
            slider = self.driver.find_element_by_xpath("//*[@id='nc_1_n1z']")

            time.sleep(1)

            ActionChains(self.driver).click_and_hold(slider).perform()

            for track in tracks['forward_tracks']:
                ActionChains(self.driver).move_by_offset(xoffset=track, yoffset=0).perform()

            time.sleep(0.5)

            while True:

                print('进入while循环')
                print('*' * 50)
                # print(location_x,location_y)
                print('*' * 50)
                time.sleep(0.5)
                # self.driver.find_element_by_xpath('//i[@id="nc_1__btn_2"]').click()
                captcha_image = self.driver.find_element_by_xpath('//div[@class="clickCaptcha_img"]/img')
                captcha = captcha_image.get_attribute('src')
                print(captcha)

                # 下载图片
                fh = open("captcha.jpg", "wb")
                fh.write(base64.b64decode(captcha.split(',')[1]))
                fh.close()

                # 获取要识别的文字

                word_ele = self.driver.find_element_by_xpath('//div[@id="nc_1__scale_text"]/i')
                word = word_ele.text.replace('”', '').replace('“', '').strip()

                print('请点击图中的{}字'.format(word))

                # 识别图中的文字
                rsp = self.recognize_image()

                # 计算要点击的文字在图中的位置

                location_x, location_y = cal_location(word, rsp)
                print(location_x, location_y)
                ActionChains(self.driver).move_to_element_with_offset(captcha_image, location_x,
                                                                      location_y).click().perform()
                time.sleep(1)
                # if '验证通过' in self.driver.page_source:
                #     break
                try:
                    menu = self.driver.find_element_by_xpath('//a[@class="showmenu"]')
                except Exception as e:
                    menu = None
                if menu:
                    break

            self.driver.get('https://www.52pojie.cn/home.php?mod=task&do=apply&id=2')
            time.sleep(5)
            self.driver.quit()
        except Exception as e:
            print(e)
            exit(0)

            c.crack_slider()


if __name__ == '__main__':
    c = CrackSlider()
    c.crack_slider()
