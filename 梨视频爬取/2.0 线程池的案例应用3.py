# 爬取梨视频的视频数据
import json
import random
import requests
from lxml import etree
from multiprocessing import Pool

headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/83.0.4103.116 Safari/537.36 ',
        'Cookie': '__secdyid=18a4a1f0933bb2e7caac90e29ff34fb7b7f03700164039c8021603270592; acw_tc=781bad0616032705923185394e7dedc149a649110190bfcd46f628ca1e9b48; JSESSIONID=E7FC83D60A1300FC5B3862AA2284DB3A; PEAR_UUID=bbaad33f-e75d-4191-b9e2-5d8998add46b; _uab_collina=160327059250274050269398; UM_distinctid=1754a5fcd73349-01533d76870ce3-c781f38-144000-1754a5fcd74728; CNZZDATA1260553744=1995631239-1603267820-https%253A%252F%252Fwww.baidu.com%252F%7C1603267820; Hm_lvt_9707bc8d5f6bba210e7218b8496f076a=1603270594; p_h5_u=ECBFEAFA-B8C6-4671-A8D4-03777684387D; Hm_lpvt_9707bc8d5f6bba210e7218b8496f076a=1603271759; SERVERID=a6169b2e0636a71b774d6641c064eb8c|1603272088|1603270592',
        'Referer': 'https://www.pearvideo.com/category_59',
    }
# 存储视频链接
urls = []
# 原则：线程池处理的是阻塞耗时的操作


# 对音乐页面发起请求
def get_page(start):
    params = {
        'reqType': '5',
        'categoryId': '59',
        'start': start,
        'mrd': str(random.random()),
    }
    url = 'https://www.pearvideo.com/category_loading.jsp'
    response = requests.get(url=url, headers=headers, params=params)
    html = response.text

    return html


# 解析li标签下的网址，对网址发送请求
def detail_page(html):
    tree = etree.HTML(html)
    name = tree.xpath('//div/a/div[2]/text()')
    a_list = tree.xpath('//div[@class="vervideo-bd"]/a/@href')
    count = 0
    for a in a_list:
        detail_url = 'https://www.pearvideo.com/' + a
        contId = a.split('_')[-1]

        header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/83.0.4103.116 Safari/537.36 ',
            'Referer': detail_url,
        }

        params = {
            'contId': str(contId),
            'mrd': str(random.random())
        }

        get_url = 'https://www.pearvideo.com/videoStatus.jsp'
        # 对详情页的url发起请求
        response = requests.get(url=get_url, headers=header, params=params)
        detail_page_text = response.json()

        # 获取json数据中的视频地址
        videoInfo = detail_page_text['videoInfo']
        videos = videoInfo['videos']
        srcUrl = videos['srcUrl']

        # 因为取到的srcUrl是假的视频链接，所以要进一步处理
        title = '/'.join(srcUrl.split('/')[0:-1])
        body = "/cont-" + contId + '-'
        footer = '-'.join(srcUrl.split('-')[1:])
        file_root = title + body + footer

        # 把视频链接存储到列表里
        dic = {
            'name': name[count],
            'url': file_root,
        }
        count += 1

        urls.append(dic)


# 对视频链接发起请求，存储视频
def get_video(dic):
    url = dic['url']
    name = dic['name']
    data = requests.get(url=url, headers=headers).content

    # 存储视频
    with open('../video/' + name + '.mp4', 'wb') as fp:
        print(dic['name'], '下载中……')
        fp.write(data)
        print(dic['name'], '下载成功！')


if __name__ == '__main__':
    for count in range(0, 96, 12):
        html = get_page(count)
        detail_page(html)

        print(len(urls))
    # 实例化一个pool方法
    pool = Pool(4)
    pool.map(get_video, urls)

    pool.close()
    pool.join()

