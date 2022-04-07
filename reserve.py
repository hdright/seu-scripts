import datetime
import json
import logging
import ssl
from time import sleep
import urllib

import ddddocr

import config
import urls
from utils.login import login


def main():
    ssl._create_default_https_context = ssl._create_unverified_context

    card_num = config.card_num
    logging.debug(card_num)
    logging.debug("请输入密码:")
    password = config.password
    logging.debug('*'*len(password))
    logging.debug("开始登陆")
    s = login(card_num, password)

    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest',
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    res = s.get(urls.res_val_image, headers=headers, allow_redirects=True)
    res = s.get(str(res.content).split(".href='")
                [-1].split("'</script>")[0], headers=headers)
    with open('validateimage.jpg', 'wb') as file:
        file.write(res.content)

    f = open('validateimage.jpg', 'rb')
    img_bytes = f.read()
    valid_s = ocr.classification(img_bytes)

    postdata = {
        'ids': '',
        'useTime': config.reserve_data['reservetime'],
        'itemId': config.reserve_data['item'],
        'allowHalf': 2,
        'validateCode': valid_s,
        'phone': config.reserve_data['phone'],
        'remark': '',
        'useUserIds': '',
    }

    data = urllib.parse.urlencode(postdata).encode('utf-8')

    res = s.post(urls.res_url, data=data,
                 headers=headers, allow_redirects=False)
    logging.debug(res.status_code)
    logging.debug(res.text)
    try:
        resJson = json.loads(res.text)
    except:
        return -1
    if 'sucuss' in resJson.keys():
        logging.info(resJson['sucuss'])
        return 1
    else:
        logging.error(resJson)
        return 0


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, filename="reserve.log",
                        format="%(asctime)s - %(levelname)-9s - %(filename)-8s : %(lineno)s line - %(message)s")

    now_time = datetime.datetime.now()
    # logging.info("现在小时数： %d" % now_time.time().hour)
    # 获取启动时间
    if now_time.time().hour < 8:
        days_to_add = 0
    else:
        days_to_add = 1
    next_time = now_time + datetime.timedelta(days=+days_to_add)
    next_year = next_time.date().year
    next_month = next_time.date().month
    next_day = next_time.date().day
    next_time = datetime.datetime(
        next_year, next_month, next_day, 7, 59, 56, 0)
    # 获取距离启动时间，单位为秒
    timer_start_time = (next_time - now_time).total_seconds()
    logging.info("睡眠 %d 秒" % timer_start_time)
    sleep(timer_start_time)

    ocr = ddddocr.DdddOcr()
    success = 0
    count = 0
    timer_e_time = 0
    while(success!=1 and count < 20 and timer_e_time < 450):
        success = main()
        if success == -1:
            sleep(10)
            pass
        elif success == 0:
            count += 1
        now_time = datetime.datetime.now()
        timer_e_time = (now_time - next_time).total_seconds()# 已经抢了多长时间（秒）
        

