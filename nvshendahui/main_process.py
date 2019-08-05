# coding = utf-8
"""
@author: zhou
@time:2019/8/2 14:16
@File: main_process.py
"""

import requests
import json
from bs4 import BeautifulSoup
import re
import time
from download_page import DownloadPage
import os
from tools import get_picture, save_to_file, save_pic


def get_list(page):
    nvshen_id_list = []
    nvshen_id_picture = []
    for i in range(1, page):
        print("获取第" + str(i) + "页数据")
        url = 'http://api.dongqiudi.com/search?keywords=%E5%A5%B3%E7%A5%9E%E5%A4%A7%E4%BC%9A&type=all&page=' + str(i)
        html = requests.get(url=url).text
        news = json.loads(html)['news']
        if len(news) == 0:
            print("没有更多啦")
            break
        nvshen_id = [k['id'] for k in news]
        nvshen_id_list = nvshen_id_list + nvshen_id
        nvshen_id_picture = nvshen_id_picture + [{k['id']: k['thumb']} for k in news]
        time.sleep(1)
    return nvshen_id_list, nvshen_id_picture


def download_page(nvshen_id_list):
    for i in nvshen_id_list:
        print("正在下载ID为" + i + "的HTML网页")
        url = 'https://www.dongqiudi.com/archive/%s.html' % i
        download = DownloadPage()
        html = download.getHtml(url)
        download.saveHtml(i, html)
        time.sleep(2)


def deal_loaclfile(nvshen_id_picture):
    files = os.listdir('html_page/')
    nvshen_list = []
    special_page = []
    for f in files:
        if f[-4:] == 'html' and not f.startswith('~'):
            htmlfile = open('html_page/' + f, 'r', encoding='utf-8').read()
            content = BeautifulSoup(htmlfile, 'html.parser')
            try:
                tmp_list = []
                nvshen_name = content.find(text=re.compile("上一期女神"))
                if nvshen_name is None:
                    continue
                nvshen_name_new = re.findall(r"女神(.+?)，", nvshen_name)
                nvshen_count = re.findall(r"超过(.+?)人", nvshen_name)
                tmp_list.append(''.join(nvshen_name_new))
                tmp_list.append(''.join(nvshen_count))
                tmp_list.append(f[:-4])
                tmp_score = content.find_all('span', attrs={'style': "color:#ff0000"})
                tmp_score = list(filter(None, [k.string for k in tmp_score]))
                if '.' in tmp_score[0]:
                    if len(tmp_score[0]) > 3:
                        tmp_list.append(''.join(list(filter(str.isdigit, tmp_score[0].strip()))))
                        nvshen_list = nvshen_list + get_picture(content, tmp_list, nvshen_id_picture)
                    else:
                        tmp_list.append(float(tmp_score[0]) * 10)
                        nvshen_list = nvshen_list + get_picture(content, tmp_list, nvshen_id_picture)
                elif len(tmp_score) > 1:
                    if '.' in tmp_score[1]:
                        if len(tmp_score[1]) > 3:
                            tmp_list.append(''.join(list(filter(str.isdigit, tmp_score[1].strip()))))
                            nvshen_list = nvshen_list + get_picture(content, tmp_list, nvshen_id_picture)
                        else:
                            tmp_list.append(float(tmp_score[1]) * 10)
                            nvshen_list = nvshen_list + get_picture(content, tmp_list, nvshen_id_picture)
                    else:
                        special_page.append(f)
                        print("拿不到score的HTML：", f)
                else:
                    special_page.append(f)
                    print("拿不到score的HTML：", f)
            except:
                print("解析出错的HTML：", f)
                raise
    return nvshen_list, special_page


def main_process(nvshen_id_list, nvshen_id_picture):
    session = {
        'dqduid': 'eyJpdiI6InF4UGh5aG5wNVQ1aDFvVGZkeTR5eU16aHVJYk5RN1RVVHptU210c3pra0U9IiwidmFsdWUiOiIrcXlQa3pmNGhaSkVHN3RvZ3ZyUVhuT0VBdTdYcEhrQ01EaEFTNW5heFY0QmZod0x0dlwvUFwvczc1TGQ0NERNVERcL21USUdCeDFYT1dQT3R1eTNaVXBiZz09IiwibWFjIjoiMWM2Y2ZmMWU3MDcyMWQwNTEwZGJjM2RlNDkyODMyYjI0ZjY1Y2MwODAxMTVmY2U2YmMwZmQ0MTRlYjMxOWE0YSJ9'}
    header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win32; x32; rv:54.0) Gecko/20100101 Firefox/54.0',
              'Connection': 'keep-alive'}
    nvshen_list = []
    for i in nvshen_id_list:
        print("进入循环")
        url1 = 'https://www.dongqiudi.com/archive/%s.html' % i
        html2 = requests.get(url=url1, cookies=session, headers=header).text
        content = BeautifulSoup(html2, "html.parser")
        try:
            tmp_list = []
            nvshen_name = content.find(text=re.compile("上一期女神"))
            if nvshen_name is None:
                continue
            nvshen_name_new = re.findall(r"女神(.+?)，", nvshen_name)
            nvshen_count = re.findall(r"超过(.+?)人", nvshen_name)
            tmp_list.append(''.join(nvshen_name_new))
            tmp_list.append(''.join(nvshen_count))
            tmp_list.append(i)
            print(tmp_list)
            tmp_score = content.find_all('span', attrs={'style': "color:#ff0000"})
            tmp_score = list(filter(None, [k.string for k in tmp_score]))
            for m in tmp_score:
                if '.' in m.string:
                    if len(m.string) > 3:
                        tmp_list.append(m.string.strip()[-3:])
                        nvshen_list = nvshen_list + get_picture(content, tmp_list, nvshen_id_picture)
                        print(nvshen_list)
                    else:
                        tmp_list.append(m.string)
                        nvshen_list = nvshen_list + get_picture(content, tmp_list, nvshen_id_picture)
                        print(nvshen_list)
            time.sleep(2)
        except:
            print("出错的：", i)
            raise
        print("循环结束")
    return nvshen_list


if __name__ == '__main__':
    # list1, nvshen_id_picture = get_list(20)
    nvshen_id_picture = [{'1186017': 'https://img1.qunliao.info/fastdfs4/M00/CD/39/180x135/crop/-/ChMf8F1ED1uAd2QdAAGd1jMo6oM730.jpg'}, {'1179853': 'https://img1.qunliao.info/fastdfs4/M00/CB/42/180x135/crop/-/ChMf8F078maAMBTuAAFWXk5lsEU391.jpg'}, {'1179558': 'https://img1.qunliao.info/fastdfs4/M00/CB/42/180x135/crop/-/ChMf8F07xPOAegh1AAEnYVW7MNs834.jpg'}, {'1174124': 'https://img1.qunliao.info/fastdfs4/M00/CB/18/180x135/crop/-/ChNLkl0yhG-AOBcXAAFWCP0bvbM543.jpg'}, {'1173681': 'https://img1.qunliao.info/fastdfs4/M00/CB/14/180x135/crop/-/ChNLkl0xXrWAaPP0AAgGO5jjE1s107.png'}, {'1168209': 'https://img1.qunliao.info/fastdfs4/M00/CA/F7/180x135/crop/-/ChMf8F0pSPCAAGvzAABCs4nrlWA528.jpg'}, {'1167991': 'https://img1.qunliao.info/fastdfs4/M00/CA/F7/180x135/crop/-/ChMf8F0pSMyAaKD4AAChcnGLtYI696.jpg'}, {'1158313': 'https://img1.qunliao.info/fastdfs4/M00/CA/D9/180x135/crop/-/ChMf8F0gYLKAakyaAACqDFNlzzc901.jpg'}, {'1158300': 'https://img1.qunliao.info/fastdfs4/M00/CA/D6/180x135/crop/-/ChMf8F0fHEKACfHuAAFjxmL0PDE687.jpg'}, {'1155543': 'https://img1.qunliao.info/fastdfs4/M00/CA/CD/180x135/crop/-/ChMf8F0cXwKASDweAABbMvSnXhE918.jpg'}, {'1153133': 'https://img1.qunliao.info/fastdfs4/M00/CA/C5/180x135/crop/-/ChNLkl0a1lyAG-zQAAXRWlAKelA777.png'}, {'1151703': 'https://img1.qunliao.info/fastdfs4/M00/CA/C4/180x135/crop/-/ChMf8F0ZyX-AH-rhAAl9P5QGi3E854.png'}, {'1148667': 'https://img1.qunliao.info/fastdfs4/M00/CA/BC/180x135/crop/-/ChNLkl0YIAmAFqdFAABdqUsD-Z8970.jpg'}, {'1146909': 'https://img1.qunliao.info/fastdfs4/M00/CA/B6/180x135/crop/-/ChMf8F0WADuAO34uAA8Q_HFxtM4135.png'}, {'1146710': 'https://img1.qunliao.info/fastdfs4/M00/CA/B3/180x135/crop/-/ChNLkl0V4h-AatECAAO29H-VQ4o326.png'}, {'1139540': 'https://img1.qunliao.info/fastdfs4/M00/CA/96/180x135/crop/-/ChNLkl0QjNyAaKTDAABgrGMMpt4400.jpg'}, {'1139355': 'https://img1.qunliao.info/fastdfs4/M00/CA/98/180x135/crop/-/ChMf8F0QebmAZFDcAAjlNfN21Pg833.png'}, {'1137501': 'https://img1.qunliao.info/fastdfs4/M00/CA/93/180x135/crop/-/ChMf8F0PIbmAU2OSAAZL_2qsQqQ170.jpg'}, {'1137537': 'https://img1.qunliao.info/fastdfs4/M00/CA/93/180x135/crop/-/ChMf8F0PLUeANGj4AAbm4U2TkE0219.png'}, {'1135665': 'https://img1.qunliao.info/fastdfs4/M00/CA/8D/180x135/crop/-/ChMf8F0NxiSAVv_NAADy4nwBXjc670.jpg'}, {'1135358': 'https://img1.qunliao.info/fastdfs4/M00/CA/8C/180x135/crop/-/ChMf8F0NmgCALH33AAm9pkrZmAQ626.png'}, {'1131610': 'https://img1.qunliao.info/fastdfs4/M00/CA/82/180x135/crop/-/ChNLkl0LJyWAGnobAAkWm30pKsY365.png'}, {'1072265': 'https://img1.qunliao.info/fastdfs4/M00/CA/17/180x135/crop/-/ChMf8FzpJhWADEypAAE_WBvcGbE138.jpg'}, {'1039791': 'https://img1.qunliao.info/fastdfs4/M00/CA/0A/180x135/crop/-/ChMf8FzkrKyAIy0DAAd3q6ibP30634.png'}, {'1033809': 'https://img1.qunliao.info/fastdfs4/M00/C9/FE/180x135/crop/-/ChNLklzhHmmAWpPoAADv94Cmy3I306.jpg'}, {'1083878': 'https://img1.qunliao.info/fastdfs4/M00/CA/28/180x135/crop/-/ChNLklzuW7mAKxUkAAB6cWRVtHo375.jpg'}, {'1081668': 'https://img1.qunliao.info/fastdfs4/M00/CA/28/180x135/crop/-/ChMf8Fzt6ieAEhmXAAPR6R9UsbA541.png'}, {'1078899': 'https://img1.qunliao.info/fastdfs4/M00/CA/22/180x135/crop/-/ChMf8Fzrj0yAHUXLAAEIIrhOXCY156.jpg'}, {'1075312': 'https://img1.qunliao.info/fastdfs4/M00/CA/1E/180x135/crop/-/ChNLklzrUb-ABZ9sAAamZKLLACA034.png'}, {'1069476': 'https://img1.qunliao.info/fastdfs4/M00/CA/12/180x135/crop/-/ChMf8Fzns9-ATbokAAMVf-bMyoY371.png'}, {'1053424': 'https://img1.qunliao.info/fastdfs4/M00/CA/0D/180x135/crop/-/ChNLklzmZUKAZc6dAAVGMtOzx8g662.png'}, {'950983': 'https://img1.qunliao.info/fastdfs4/M00/C9/81/180x135/crop/-/ChNLklzBfPuATHJWAACCPzsvRg8880.jpg'}, {'1028512': 'https://img1.qunliao.info/fastdfs4/M00/C9/F6/180x135/crop/-/ChNLklzfhXuAWMM1AASci5Jpg34578.png'}, {'990130': 'https://img1.qunliao.info/fastdfs4/M00/C9/F5/180x135/crop/-/ChMf8FzeZuqAREwRAAPIswJf2aQ480.png'}, {'968179': 'https://img1.qunliao.info/fastdfs4/M00/C9/D8/180x135/crop/-/ChNLklzZlhmAAosXAADQVu8vcos346.jpg'}, {'966722': 'https://img1.qunliao.info/fastdfs4/M00/C9/CF/180x135/crop/-/ChMf8FzXuACAWdBxAAL3V4R2Dic099.png'}, {'965913': 'https://img1.qunliao.info/fastdfs4/M00/C9/CB/180x135/crop/-/ChMf8FzWqluAQKsVAAyCmagus2U527.png'}, {'965125': 'https://img1.qunliao.info/fastdfs4/M00/C9/C5/180x135/crop/-/ChNLklzVX1-AfUakAACVhdk1WSo193.jpg'}, {'964326': 'https://img1.qunliao.info/fastdfs4/M00/C9/C2/180x135/crop/-/ChMf8FzTz_qAYIhPAAdb31jUaWo610.png'}, {'963996': 'https://img1.qunliao.info/fastdfs4/M00/C9/BF/180x135/crop/-/ChNLklzTn7mAfLOJAAIoIxuETfA765.png'}, {'949220': 'https://img1.qunliao.info/fastdfs4/M00/C9/69/180x135/crop/-/ChMf8Fy7Cs-AeJwxAACkDFS_U8w613.jpg'}, {'962576': 'https://img1.qunliao.info/fastdfs4/M00/C9/B8/180x135/crop/-/ChMf8FzREs-ADNL_AAUkG8C6TqA969.png'}, {'961776': 'https://img1.qunliao.info/fastdfs4/M00/C9/B5/180x135/crop/-/ChMf8FzQEnGAAbRbAAVwQ4eh15s817.png'}, {'960962': 'https://img1.qunliao.info/fastdfs4/M00/C9/AE/180x135/crop/-/ChMf8FzOqWCAdbHLAAOAoOQrsZg389.png'}, {'959812': 'https://img1.qunliao.info/fastdfs4/M00/C9/A7/180x135/crop/-/ChMf8FzNFXaAVwFWAANf_4zAwV0225.png'}, {'959106': 'https://img1.qunliao.info/fastdfs4/M00/C9/A4/180x135/crop/-/ChMf8FzL4ZeAQ8DpAAjPHZSeHvA732.png'}, {'958601': 'https://img1.qunliao.info/fastdfs4/M00/C9/A3/180x135/crop/-/ChMf8FzLqnOAdJOqAAMIq7DZ7Xk286.png'}, {'957967': 'https://img1.qunliao.info/fastdfs4/M00/C9/9E/180x135/crop/-/ChMf8FzJd0qAQMB8AAhp2kQwnIE899.png'}, {'956445': 'https://img1.qunliao.info/fastdfs4/M00/C9/93/180x135/crop/-/ChNLklzGsleAM_YNAALF9Z_0Xkk864.png'}, {'955682': 'https://img1.qunliao.info/fastdfs4/M00/C9/8E/180x135/crop/-/ChNLklzFj_6AMUFFAAL-q8-5guI042.png'}, {'954549': 'https://img1.qunliao.info/fastdfs4/M00/C9/87/180x135/crop/-/ChNLklzEDo6AIMHeAAQCFNtw50Q709.png'}, {'953658': 'https://img1.qunliao.info/fastdfs4/M00/C9/83/180x135/crop/-/ChNLklzChbKAP1n7AARl1c0kzWA199.png'}, {'953347': 'https://img1.qunliao.info/fastdfs4/M00/C9/84/180x135/crop/-/ChMf8FzBwdqAbR3wAADBTqsEdvk670.jpg'}, {'951016': 'https://img1.qunliao.info/fastdfs4/M00/C9/7A/180x135/crop/-/ChNLkly_eiWALTIUAAEh6t7y4wA031.jpg'}, {'950556': 'https://img1.qunliao.info/fastdfs4/M00/C9/75/180x135/crop/-/ChMf8Fy9ixKAcPWNAAjzVtnRraM314.png'}, {'950114': 'https://img1.qunliao.info/fastdfs4/M00/C9/70/180x135/crop/-/ChMf8Fy8WweAK8exAAYQGu1cHAk803.png'}, {'948245': 'https://img1.qunliao.info/fastdfs4/M00/C9/62/180x135/crop/-/ChMf8Fy4tqyAGInEAACBXI_wmZE790.jpg'}, {'947689': 'https://img1.qunliao.info/fastdfs4/M00/C9/5F/180x135/crop/-/ChMf8Fy3voKAUiPgAADtR8btDj8910.jpg'}, {'947011': 'https://img1.qunliao.info/fastdfs4/M00/C9/5B/180x135/crop/-/ChMf8Fy2koCAchbqAALKwwGolUs293.png'}, {'946650': 'https://img1.qunliao.info/fastdfs4/M00/C9/55/180x135/crop/-/ChNLkly1Rg2ACTnlAAKPMmULkno856.png'}, {'945938': 'https://img1.qunliao.info/fastdfs4/M00/C9/4D/180x135/crop/-/ChMf8FyzBLCALuFYAAYUTWjH0mk029.jpg'}, {'945092': 'https://img1.qunliao.info/fastdfs4/M00/C9/4B/180x135/crop/-/ChMf8FyyoZWAcUIUAALIR57JYwo898.png'}, {'944208': 'https://img1.qunliao.info/fastdfs4/M00/C9/43/180x135/crop/-/ChNLklyxTUOAKMTeAACHOyZc0vU713.jpg'}, {'943953': 'https://img1.qunliao.info/fastdfs4/M00/C9/40/180x135/crop/-/ChMf8FyvdKOAKMy1AAC-HDcdC88433.jpg'}, {'943488': 'https://img1.qunliao.info/fastdfs4/M00/C9/3A/180x135/crop/-/ChMf8FytqwCALEAtAAR2ftuumBo899.png'}, {'943095': 'https://img1.qunliao.info/fastdfs4/M00/C9/37/180x135/crop/-/ChNLklytVNGADl2cAAZtRlRPJdY701.png'}, {'942442': 'https://img1.qunliao.info/fastdfs4/M00/C9/33/180x135/crop/-/ChNLklysCliAKg3XAAH1vuQTSRQ023.png'}, {'941814': 'https://img1.qunliao.info/fastdfs4/M00/C9/2E/180x135/crop/-/ChNLklyqM0uAbr_PAADTaVy5HiY282.jpg'}, {'941250': 'https://img1.qunliao.info/fastdfs4/M00/C9/2D/180x135/crop/-/ChMf8FypZWiALyenAABai3t7muE991.jpg'}, {'940373': 'https://img1.qunliao.info/fastdfs4/M00/C9/25/180x135/crop/-/ChMf8FynJ6uAJuZ3AAQW8dcF01I475.png'}, {'940075': 'https://img1.qunliao.info/fastdfs4/M00/C9/20/180x135/crop/-/ChNLklylkbaATv2bAAUJhU0XaMg548.png'}, {'939487': 'https://img1.qunliao.info/fastdfs4/M00/C9/1B/180x135/crop/-/ChNLklykZvyAFdH_AACdddwtF3w964.jpg'}, {'938997': 'https://img1.qunliao.info/fastdfs4/M00/C9/18/180x135/crop/-/ChNLklyjj52AQhpeAAKKgNeW6vc242.jpg'}, {'938466': 'https://img1.qunliao.info/fastdfs4/M00/C9/18/180x135/crop/-/ChMf8FyizEiAKcY5AAifr59ZOuY068.png'}, {'936939': 'https://img1.qunliao.info/fastdfs4/M00/C9/09/180x135/crop/-/ChNLklyfKPaAVb6oAAPjeXdlnPo395.png'}, {'934269': 'https://img1.qunliao.info/fastdfs4/M00/C8/F8/180x135/crop/-/ChMf8FyYaPOAHVHaAALbx-NuJTo968.png'}, {'936519': 'https://img1.qunliao.info/fastdfs4/M00/C9/0A/180x135/crop/-/ChMf8Fye1TqAJEzfAAlz88CN2lU689.png'}, {'935943': 'https://img1.qunliao.info/fastdfs4/M00/C9/07/180x135/crop/-/ChMf8FydgviAVpNSAAE3GbmAFIo934.jpg'}, {'935610': 'https://img1.qunliao.info/fastdfs4/M00/C9/03/180x135/crop/-/ChMf8FycN4uAVcSoAAC5GRh7RWU810.jpg'}, {'934786': 'https://img1.qunliao.info/fastdfs4/M00/C8/FA/180x135/crop/-/ChNLklyZpRqAXGB3AAtVwiuDfcM369.png'}, {'933793': 'https://img1.qunliao.info/fastdfs4/M00/C8/F4/180x135/crop/-/ChMf8FyXNUCABzV-AALqt69O_Is563.png'}, {'932913': 'https://img1.qunliao.info/fastdfs4/M00/C8/EC/180x135/crop/-/ChNLklyUycGAebnRAAYtEb-ThEY594.png'}, {'918419': 'https://img1.qunliao.info/fastdfs4/M00/C8/7D/180x135/crop/-/ChNLklx2YoiANNRFAAKvU_83SqE086.png'}, {'933292': 'https://img1.qunliao.info/fastdfs4/M00/C8/F1/180x135/crop/-/ChMf8FyVz--AddIrAALczZ9aJD4479.png'}, {'919191': 'https://img1.qunliao.info/fastdfs3/M00/BE/C9/ChOxM1xP9J6ATe-cAABGOoaU-uA833.png'}, {'917711': 'https://img1.qunliao.info/fastdfs4/M00/C8/7B/180x135/crop/-/ChMf8Fx07lWAXO_ZAAZpE19FINU811.png'}, {'917324': 'https://img1.qunliao.info/fastdfs4/M00/C8/78/180x135/crop/-/ChNLklx0qrCAY8OCAAXw8F1NSPw630.png'}, {'916583': 'https://img1.qunliao.info/fastdfs4/M00/C8/70/180x135/crop/-/ChNLklxyj_iAM3jmAABLtV3ieRI276.jpg'}, {'915987': 'https://img1.qunliao.info/fastdfs4/M00/C8/6D/180x135/crop/-/ChMf8FxxA_yAS7pqAANTMLAKIsg102.png'}, {'915667': 'https://img1.qunliao.info/fastdfs4/M00/C8/68/180x135/crop/-/ChNLklxv_0OAe44xAASDQNRC3hA153.png'}, {'915115': 'https://img1.qunliao.info/fastdfs4/M00/C8/66/180x135/crop/-/ChMf8FxusWqAbg1VAABQzwDw4h0753.jpg'}, {'913808': 'https://img1.qunliao.info/fastdfs4/M00/C8/5A/180x135/crop/-/ChNLklxr3J2AD4SfAAbkQBdrH3Q254.png'}, {'913219': 'https://img1.qunliao.info/fastdfs4/M00/C8/55/180x135/crop/-/ChNLklxqiTaAOeFHAAJeMJZp3Zw416.png'}, {'912565': 'https://img1.qunliao.info/fastdfs4/M00/C8/52/180x135/crop/-/ChMf8FxpDDSAIIB5AALJz9CNCN0462.png'}, {'912197': 'https://img1.qunliao.info/fastdfs4/M00/C8/4F/180x135/crop/-/ChMf8Fxn89OALxILAAOyfc2EifU186.png'}, {'911792': 'https://img1.qunliao.info/fastdfs4/M00/C8/4C/180x135/crop/-/ChMf8FxmvlaAJ0zOAABjyptgUlA492.jpg'}, {'911182': 'https://img1.qunliao.info/fastdfs4/M00/C8/45/180x135/crop/-/ChNLklxlL4KALsvRAAKZZe4IYHo526.png'}, {'910742': 'https://img1.qunliao.info/fastdfs4/M00/C8/44/180x135/crop/-/ChNLklxk1UKAWTXYAANKU55Mev8809.png'}, {'909997': 'https://img1.qunliao.info/fastdfs4/M00/C8/3E/180x135/crop/-/ChNLklxifXiARuE6AASGuK4ulFA047.png'}, {'909768': 'https://img1.qunliao.info/fastdfs4/M00/C8/3C/180x135/crop/-/ChNLklxhjwyATz_GAAW8svYZWx4120.png'}, {'908130': 'https://img1.qunliao.info/fastdfs4/M00/C8/2F/180x135/crop/-/ChNLklxc8r2AV7h6AAOZLcMkikU539.png'}, {'909054': 'https://img1.qunliao.info/fastdfs4/M00/C8/3A/180x135/crop/-/ChMf8FxgWlOASRU0AAhcpkt2VtY277.png'}, {'908611': 'https://img1.qunliao.info/fastdfs4/M00/C8/32/180x135/crop/-/ChNLklxe4e6AbgQnAAKR2SRAtGE798.png'}, {'907647': 'https://img1.qunliao.info/fastdfs4/M00/C8/2B/180x135/crop/-/ChNLklxbJdSANc_0AAH7QYBA0fU676.png'}, {'907033': 'https://img1.qunliao.info/fastdfs4/M00/C8/27/180x135/crop/-/ChNLklxYXQ2AUV7iAALm5wWFdhY853.png'}, {'906302': 'https://img1.qunliao.info/fastdfs4/M00/C8/21/180x135/crop/-/ChNLklxWcfqARt7MAAH-UFk_j8I174.png'}, {'905830': 'https://img1.qunliao.info/fastdfs4/M00/C8/20/180x135/crop/-/ChMf8FxVptWALbEsAAQxYm50OgE199.png'}, {'905591': 'https://img1.qunliao.info/fastdfs4/M00/C8/1B/180x135/crop/-/ChNLklxUcnmACjDaAAIK-P-omog500.png'}, {'905026': 'https://img1.qunliao.info/fastdfs3/M00/C0/D7/180x135/crop/-/ChOxM1xS8VyAMe1DAAPGxI_J0yk543.png'}, {'904550': 'https://img1.qunliao.info/fastdfs3/M00/C0/3A/180x135/crop/-/ChOxM1xR8-WATJKQAAB5OwwVX5g365.jpg'}, {'903859': 'https://img1.qunliao.info/fastdfs3/M00/BF/0D/180x135/crop/-/ChOxM1xQOD6AGC_MAAHVXavT60o044.png'}, {'903404': 'https://img1.qunliao.info/fastdfs3/M00/BE/3C/180x135/crop/-/ChOxM1xPCEqAaXMQAAVVZ0Us2QM633.png'}, {'902688': 'https://img1.qunliao.info/fastdfs3/M00/BD/A0/180x135/crop/-/ChOxM1xOaLOAD9O0AAFrhTdbEu0039.png'}, {'902213': 'https://img1.qunliao.info/fastdfs3/M00/BC/67/180x135/crop/-/ChOxM1xMUvaAIXHKAAB94dAAiYM259.jpg'}, {'901654': 'https://img1.qunliao.info/fastdfs3/M00/BB/BF/180x135/crop/-/ChOxM1xK9aSAamuGAAKCmd7I3T0110.png'}, {'901032': 'https://img1.qunliao.info/fastdfs3/M00/BA/D6/180x135/crop/-/ChOxM1xJr5eAauSTAAQLsFNK5Oo200.png'}, {'900460': 'https://img1.qunliao.info/fastdfs3/M00/BA/19/180x135/crop/-/ChOxM1xIUQeAL1TcAAA-1IGJK2Q420.jpg'}, {'899794': 'https://img1.qunliao.info/fastdfs3/M00/B9/5F/180x135/crop/-/ChOxM1xGvsuAKtqeAAGN86x8p2U352.png'}, {'899398': 'https://img1.qunliao.info/fastdfs3/M00/B8/EC/180x135/crop/-/ChOxM1xFwYSACvmdAAJ0fhJuwso638.png'}, {'898625': 'https://img1.qunliao.info/fastdfs3/M00/B7/FB/180x135/crop/-/ChOxM1xEaoiAL44eAAFqaHU8Xsg790.png'}, {'897935': 'https://img1.qunliao.info/fastdfs3/M00/B5/71/180x135/crop/-/ChOxM1xC14aAVBdRAAJcY1yuxQ8610.jpg'}, {'897660': 'https://img1.qunliao.info/fastdfs3/M00/B5/12/180x135/crop/-/ChOxM1xB9cyALbfjAACQixuiSA8741.jpg'}, {'896975': 'https://img1.qunliao.info/fastdfs3/M00/B4/33/180x135/crop/-/ChOxM1xAVX-AEikRAAHjqnaJpmw580.png'}, {'890267': 'https://img1.qunliao.info/fastdfs3/M00/A9/DB/180x135/crop/-/ChOxM1wx3D2AUbzhAACvwJEKrAM048.jpg'}, {'896424': 'https://img1.qunliao.info/fastdfs3/M00/B3/F0/180x135/crop/-/ChOxM1w_5YaAX-TXAAKSSjVJXOg113.png'}, {'895814': 'https://img1.qunliao.info/fastdfs3/M00/B3/2C/180x135/crop/-/ChOxM1w-ogqAcE01AACry_JpSZ4746.jpg'}, {'895223': 'https://img1.qunliao.info/fastdfs3/M00/B2/76/180x135/crop/-/ChOxM1w9TjaAWEQvAAc8ryOoSyE370.png'}, {'894604': 'https://img1.qunliao.info/fastdfs3/M00/AF/3A/180x135/crop/-/ChOxM1w7NtmAGLXbAACdNdhaoRs959.jpg'}, {'893917': 'https://img1.qunliao.info/fastdfs3/M00/AE/5B/180x135/crop/-/ChOxM1w5jgGAQYUJAAL6TmusDK8315.png'}, {'893581': 'https://img1.qunliao.info/fastdfs3/M00/AD/AC/180x135/crop/-/ChOxM1w4q3yAJlFeAAA2macv28M595.jpg'}, {'892716': 'https://img1.qunliao.info/fastdfs3/M00/AC/B2/180x135/crop/-/ChOxM1w24LGANS6SAALsgHDztqM458.png'}, {'892095': 'https://img1.qunliao.info/fastdfs3/M00/AC/02/180x135/crop/-/ChOxM1w1jSCAEWFCAAKzRvat5HQ766.png'}, {'891808': 'https://img1.qunliao.info/fastdfs3/M00/AB/99/180x135/crop/-/ChOxM1w0qGqASlMVAAOuZD627c4134.png'}, {'890958': 'https://img1.qunliao.info/fastdfs3/M00/AA/8D/180x135/crop/-/ChOxM1wzFqqAWCyvAAMYc-yolKw596.png'}, {'890229': 'https://img1.qunliao.info/fastdfs3/M00/A9/D0/180x135/crop/-/ChOxM1wxy92AbD7lAAF3SbZDyeo447.png'}, {'889907': 'https://img1.qunliao.info/fastdfs3/M00/A9/8D/180x135/crop/-/ChOxM1wxZHyAbhxBAABAe0Uv0jA276.jpg'}, {'889236': 'https://img1.qunliao.info/fastdfs3/M00/A8/D9/180x135/crop/-/ChOxM1wwIY6Ac0bQAAC8OjrA_s4709.jpg'}, {'888546': 'https://img1.qunliao.info/fastdfs3/M00/A7/9A/180x135/crop/-/ChOxM1wt9DCAS9nUAAA-6rBz9Ac985.jpg'}, {'887630': 'https://img1.qunliao.info/fastdfs3/M00/A6/A6/180x135/crop/-/ChOxM1wsPeuAXB5iAAIZ7NhZ2oQ553.png'}, {'887196': 'https://img1.qunliao.info/fastdfs3/M00/A6/1B/180x135/crop/-/ChOxM1wrBnWAAdp0AAiDnneEjrQ212.png'}, {'886673': 'https://img1.qunliao.info/fastdfs3/M00/A5/FA/180x135/crop/-/ChOxM1wq2zmAPmRgAAHdF7yePec884.jpg'}, {'886131': 'https://img1.qunliao.info/fastdfs3/M00/A5/43/180x135/crop/-/ChOxM1wpiKyADcDGAAJIOtrntbE859.png'}, {'885468': 'https://img1.qunliao.info/fastdfs3/M00/A4/8C/180x135/crop/-/ChOxM1woLf-AJX79AAGKsyqUj1w831.png'}, {'884828': 'https://img1.qunliao.info/fastdfs3/M00/A3/6B/180x135/crop/-/ChOxM1wl50eAYirhAATJ2zTKb3A368.png'}, {'884621': 'https://img1.qunliao.info/fastdfs3/M00/A3/41/180x135/crop/-/ChOxM1wlldyAdpJZAAHzJ2ykFPQ688.jpg'}, {'884240': 'https://img1.qunliao.info/fastdfs3/M00/A2/EA/180x135/crop/-/ChOxM1wkzaSAPJTXAABpju9lT_s205.jpg'}, {'883354': 'https://img1.qunliao.info/fastdfs3/M00/A2/B7/180x135/crop/-/ChOxM1wkiHeABWj_AAAtLtIJ86A407.jpg'}, {'883393': 'https://img1.qunliao.info/fastdfs3/M00/A2/1D/180x135/crop/-/ChOxM1wjZyKAUtZqAAIcUivs6og358.png'}, {'884229': 'https://img1.qunliao.info/fastdfs3/M00/A2/F7/180x135/crop/-/ChOxM1wk37iAH_tHAABetcegY9s918.jpg'}, {'883044': 'https://img1.qunliao.info/fastdfs3/M00/A1/96/180x135/crop/-/ChOxM1wiKl-AP27SAAbMboYo_0Y755.png'}, {'882432': 'https://img1.qunliao.info/fastdfs3/M00/A0/D0/180x135/crop/-/ChOxM1wgf2qAbgibAAMqOjeUy3w327.png'}, {'882032': 'https://img1.qunliao.info/fastdfs3/M00/A0/5B/180x135/crop/-/ChOxM1wfYyKAenz_AAHPOJynRuU924.png'}, {'881199': 'https://img1.qunliao.info/fastdfs3/M00/9F/72/180x135/crop/-/ChOxM1wd3qKAaNDnAAMMvcrzRo0947.png'}, {'880653': 'https://img1.qunliao.info/fastdfs3/M00/9E/C1/180x135/crop/-/ChOxM1wcgqyAdOl7AAM3KsOj1Y8847.png'}, {'880707': 'https://img1.qunliao.info/fastdfs3/M00/9E/FC/180x135/crop/-/ChOxM1wc2wiAEyQiAACSg4TwIJM750.jpg'}, {'880144': 'https://img1.qunliao.info/fastdfs3/M00/9E/A0/180x135/crop/-/ChOxM1wcS62AEw0MAAKQLo8bsJs728.png'}, {'879830': 'https://img1.qunliao.info/fastdfs3/M00/9D/AA/180x135/crop/-/ChOxM1waVViATr9lAAB0OPrFOX4521.jpg'}, {'879194': 'https://img1.qunliao.info/fastdfs3/M00/9D/12/180x135/crop/-/ChOxM1wY-4-AB1VbAAGSwTph0U0294.png'}, {'878461': 'https://img1.qunliao.info/fastdfs3/M00/9C/39/180x135/crop/-/ChOxM1wXlWaAcLl-AAHqLHmB748093.png'}, {'877778': 'https://img1.qunliao.info/fastdfs3/M00/9B/2E/180x135/crop/-/ChOxM1wWKvmAArbDAAQHB-Aqik0274.png'}, {'877160': 'https://img1.qunliao.info/fastdfs3/M00/9A/F7/180x135/crop/-/ChOxM1wVyEaAZyBwAAAzbEVmr98782.jpg'}, {'876770': 'https://img1.qunliao.info/fastdfs3/M00/9A/0C/180x135/crop/-/ChOxM1wTr8uAWko3AAMgIxjxUng644.png'}, {'876179': 'https://img1.qunliao.info/fastdfs3/M00/99/5A/180x135/crop/-/ChOxM1wSMMiAcsNRAARQ-5V2Eew377.png'}, {'874930': 'https://img1.qunliao.info/fastdfs3/M00/98/2F/180x135/crop/-/ChOxM1wP0wSAPBrRAAqz4hXUuzk110.png'}, {'874754': 'https://img1.qunliao.info/fastdfs3/M00/97/98/180x135/crop/-/ChOxM1wOjC-ATstqAAILswhoOPo674.png'}, {'874221': 'https://img1.qunliao.info/fastdfs3/M00/96/F1/180x135/crop/-/ChOxM1wNK7yATxw-AAHw1MBhtPw009.png'}, {'873302': 'https://img1.qunliao.info/fastdfs3/M00/95/B4/180x135/crop/-/ChOxM1wKuMGAfvH0AABnLE3vXjU844.jpg'}, {'873294': 'https://img1.qunliao.info/fastdfs3/M00/95/AE/180x135/crop/-/ChOxM1wKqfyAAbmmAACSKhik4DM002.jpg'}, {'873102': 'https://img1.qunliao.info/fastdfs3/M00/95/66/180x135/crop/-/ChOxM1wKNSiANkfOAAPA-DcRPxI405.png'}, {'872711': 'https://img1.qunliao.info/fastdfs3/M00/94/C8/180x135/crop/-/ChOxM1wI9fOATliPAAB0-1FSb5w278.jpg'}, {'872099': 'https://img1.qunliao.info/fastdfs3/M00/93/E1/180x135/crop/-/ChOxM1wHjkGAPENGAALBSIe4RY8803.png'}, {'871726': 'https://img1.qunliao.info/fastdfs3/M00/93/9E/180x135/crop/-/ChOxM1wHQKmACj59AAAxXs22dUM299.jpg'}, {'871511': 'https://img1.qunliao.info/fastdfs3/M00/93/1D/180x135/crop/-/ChOxM1wGHQmAS7WiAAKJVPqHJTE252.png'}, {'871059': 'https://img1.qunliao.info/fastdfs3/M00/92/6F/180x135/crop/-/ChOxM1wE9Q6AN9PwAANB3GazLBs700.png'}, {'870554': 'https://img1.qunliao.info/fastdfs3/M00/92/40/180x135/crop/-/ChOxM1wEnQyAYbYBAAHJIVP5vYo129.png'}, {'870060': 'https://img1.qunliao.info/fastdfs3/M00/91/8F/180x135/crop/-/ChOxM1wDTx6AC9odAABN1l50mdY208.jpg'}, {'869856': 'https://img1.qunliao.info/fastdfs3/M00/BE/C9/ChOxM1xP9J6ATe-cAABGOoaU-uA833.png'}, {'869631': 'https://img1.qunliao.info/fastdfs3/M00/90/7F/180x135/crop/-/ChOxM1wBJ1mAVJ4BAADyecmCqdE260.png'}, {'868875': 'https://img1.qunliao.info/fastdfs3/M00/8F/F8/180x135/crop/-/ChOxM1v_55SAZMIMAAPrkkTetFE053.png'}, {'868647': 'https://img1.qunliao.info/fastdfs3/M00/8F/D4/180x135/crop/-/ChOxM1v_qjmAUR42AAEyds8PASo269.jpg'}, {'868005': 'https://img1.qunliao.info/fastdfs3/M00/8F/83/180x135/crop/-/ChOxM1v-4IaAGg3EAAEXEULWr6Q116.png'}, {'866523': 'https://img1.qunliao.info/fastdfs3/M00/8E/8B/180x135/crop/-/ChOxM1v84HuAdkMvAAJ9cBvXRsg715.png'}, {'865229': 'https://img1.qunliao.info/fastdfs3/M00/8D/F5/180x135/crop/-/ChOxM1v7w4iADIEfAAoiZvtWU1k427.png'}, {'864665': 'https://img1.qunliao.info/fastdfs3/M00/8D/6B/180x135/crop/-/ChOxM1v6kwmABRaQAAF7_EEWjX0452.png'}, {'863487': 'https://img1.qunliao.info/fastdfs3/M00/8C/8F/180x135/crop/-/ChOxM1v5KRiAAx_XAARAWKj4WD8373.png'}, {'862721': 'https://img1.qunliao.info/fastdfs3/M00/8C/57/180x135/crop/-/ChOxM1v4u4iAVSK_AAGrEf734-Q668.png'}, {'861843': 'https://img1.qunliao.info/fastdfs3/M00/8B/70/180x135/crop/-/ChOxM1v2b7mAareVAAHQY5-oaKQ648.png'}, {'861055': 'https://img1.qunliao.info/fastdfs3/M00/8B/02/180x135/crop/-/ChOxM1v1WimAfTANAAIZ3G1nwbo348.png'}, {'860193': 'https://img1.qunliao.info/fastdfs3/M00/8A/69/180x135/crop/-/ChOxM1v0CXuAaOUmAAO0FEt8TOU955.png'}, {'859181': 'https://img1.qunliao.info/fastdfs3/M00/89/CD/180x135/crop/-/ChOxM1vyn_OAP3cOAASaCHydHaU784.png'}, {'858133': 'https://img1.qunliao.info/fastdfs3/M00/89/2D/180x135/crop/-/ChOxM1vxGJCAZWAMAAL7dut0piM032.png'}, {'856939': 'https://img1.qunliao.info/fastdfs3/M00/88/47/180x135/crop/-/ChOxM1vu6VOAf3-tAAEsM3DhSew248.png'}, {'856811': 'https://img1.qunliao.info/fastdfs3/M00/88/21/180x135/crop/-/ChOxM1vuolKACDwlAAZGyA01Exw908.png'}, {'856083': 'https://img1.qunliao.info/fastdfs3/M00/87/CA/180x135/crop/-/ChOxM1vtvjyAebMPAAbm0FtlveM130.png'}, {'855067': 'https://img1.qunliao.info/fastdfs3/M00/86/E5/180x135/crop/-/ChOxM1vr6TWAe-NiAAJKpXXxo1A932.png'}, {'854705': 'https://img1.qunliao.info/fastdfs3/M00/86/9B/180x135/crop/-/ChOxM1vrQJuAJr47AAdHWXoRLP0379.png'}, {'853491': 'https://img1.qunliao.info/fastdfs3/M00/86/1C/180x135/crop/-/ChOxM1vqPOSAaLZKAAYLBJ8Ckg8615.png'}, {'852205': 'https://img1.qunliao.info/fastdfs3/M00/84/FC/180x135/crop/-/ChOxM1voLWeAVHRFAAX8PO1pjBs247.png'}, {'850839': 'https://img1.qunliao.info/fastdfs3/M00/84/1A/180x135/crop/-/ChOxM1vmyAuAYe6CAAHlvOJASrs414.png'}, {'849837': 'https://img1.qunliao.info/fastdfs3/M00/83/6E/180x135/crop/-/ChOxM1vlwJyAMlfeAABLzHc8DiY784.jpg'}, {'848805': 'https://img1.qunliao.info/fastdfs3/M00/82/95/180x135/crop/-/ChOxM1vj_QmAK9xkAAIeFVjOA5A931.png'}, {'847693': 'https://img1.qunliao.info/fastdfs3/M00/81/E6/180x135/crop/-/ChOxM1viz7iAKHaCAAG7FxZIgpE613.png'}, {'846549': 'https://img1.qunliao.info/fastdfs3/M00/81/4E/180x135/crop/-/ChOxM1vhgPaAUKiEAAEu3ZG69Gk837.png'}, {'846609': 'https://img1.qunliao.info/fastdfs3/M00/81/55/180x135/crop/-/ChOxM1vhjw-AISfoAAHr9tKBDW8866.png'}, {'845445': 'https://img1.qunliao.info/fastdfs3/M00/81/12/180x135/crop/-/ChOxM1vhCgOAML8DAAByq9HSEQA456.jpg'}, {'844623': 'https://img1.qunliao.info/fastdfs3/M00/80/3C/180x135/crop/-/ChOxM1ve9miAT8PwAAO5lQDX5rw910.png'}, {'842925': 'https://img1.qunliao.info/fastdfs3/M00/7F/3B/180x135/crop/-/ChOxM1vdSIWAMnMAAANKDgS-3LQ039.png'}, {'842021': 'https://img1.qunliao.info/fastdfs3/M00/7E/C4/180x135/crop/-/ChOxM1vcOEOAJZpLAARMeEmO3V8112.png'}, {'841271': 'https://img1.qunliao.info/fastdfs3/M00/7E/2B/180x135/crop/-/ChOxM1va55-AJZevAABp2ybVdGU578.jpg'}, {'840601': 'https://img1.qunliao.info/fastdfs3/M00/7D/C1/180x135/crop/-/ChOxM1vaJq2AGAAvAABy50igqz8755.jpg'}, {'839385': 'https://img1.qunliao.info/fastdfs3/M00/7C/ED/180x135/crop/-/ChOxM1vYZbiAB8bDAAMpuc1BwSg083.png'}, {'838353': 'https://img1.qunliao.info/fastdfs3/M00/7C/2F/180x135/crop/-/ChOxM1vW932AJ0IjAAGigv5qMGk618.png'}, {'836819': 'https://img1.qunliao.info/fastdfs3/M00/7B/42/180x135/crop/-/ChOxM1vVqv6AIP6mAAMPQbKJ9e4789.png'}, {'835685': 'https://img1.qunliao.info/fastdfs3/M00/7A/DA/180x135/crop/-/ChOxM1vVIU2AFXQ4AADZl00-zWE170.jpg'}, {'834697': 'https://img1.qunliao.info/fastdfs3/M00/79/D0/180x135/crop/-/ChOxM1vTAdOAN6fpAAA22O-RYrk189.jpg'}, {'833579': 'https://img1.qunliao.info/fastdfs3/M00/79/34/180x135/crop/-/ChOxM1vRpeGAelSoAARv1cSQorA494.png'}, {'832491': 'https://img1.qunliao.info/fastdfs3/M00/78/86/180x135/crop/-/ChOxM1vQWlGAMvuzAAMYWsf34Sg109.png'}, {'831341': 'https://img1.qunliao.info/fastdfs3/M00/77/CC/180x135/crop/-/ChOxM1vO_cqAKM58AAKZRWCB3EA193.png'}, {'830441': 'https://img1.qunliao.info/fastdfs3/M00/77/7C/180x135/crop/-/ChOxM1vOi0WAIlrNAAHfRLtXgms070.png'}, {'829423': 'https://img1.qunliao.info/fastdfs3/M00/76/8C/180x135/crop/-/ChOxM1vMhs2AXDG7AAFpjAd0kiY520.png'}, {'827673': 'https://img1.qunliao.info/fastdfs3/M00/76/3A/180x135/crop/-/ChOxM1vL-TGAJyquAABvi0vmnEA205.jpg'}, {'825847': 'https://img1.qunliao.info/fastdfs3/M00/74/54/180x135/crop/-/ChOxM1vIPpOAZT8AAAHza_WMyRk175.png'}, {'824995': 'https://img1.qunliao.info/fastdfs3/M00/74/2C/180x135/crop/-/ChOxM1vH-BCAJn5cABCJ91fBlcA530.png'}, {'826965': 'https://img1.qunliao.info/fastdfs3/M00/75/1A/180x135/crop/-/ChOxM1vJ8JCAWbhrAADhFyq9cs0637.jpg'}, {'824093': 'https://img1.qunliao.info/fastdfs3/M00/73/A5/180x135/crop/-/ChOxM1vGpBCACD4HAAQEU47wpjg667.png'}, {'823177': 'https://img1.qunliao.info/fastdfs3/M00/72/70/180x135/crop/-/ChOxM1vEaaSAetS2AAKjSZZ7X50582.png'}, {'822525': 'https://img1.qunliao.info/fastdfs3/M00/72/44/180x135/crop/-/ChOxM1vEEy-AZE7EAAJX-Y4OJwM110.jpg'}, {'821787': 'https://img1.qunliao.info/fastdfs3/M00/71/70/180x135/crop/-/ChOxM1vCGJSABrjiAABwXKkuTB8013.jpg'}, {'820793': 'https://img1.qunliao.info/fastdfs3/M00/70/99/180x135/crop/-/ChOxM1vAhkeAU4zWAAZokFRkmys534.png'}, {'820507': 'https://img1.qunliao.info/fastdfs3/M00/BE/C9/ChOxM1xP9J6ATe-cAABGOoaU-uA833.png'}, {'820149': 'https://img1.qunliao.info/fastdfs3/M00/70/61/180x135/crop/-/ChOxM1vADZSAXzFWAABlGsuPxQg759.jpg'}, {'819217': 'https://img1.qunliao.info/fastdfs3/M00/6F/B0/180x135/crop/-/ChOxM1u-FvaAaNq-AANhqJDVAs8867.png'}, {'818107': 'https://img1.qunliao.info/fastdfs3/M00/6E/F8/180x135/crop/-/ChOxM1u8ayqAG6yLAAtT-by_V9E862.png'}, {'817227': 'https://img1.qunliao.info/fastdfs3/M00/6E/62/180x135/crop/-/ChOxM1u7IUOAKIZCAAGSpeY5uzE266.jpg'}, {'816963': 'https://img1.qunliao.info/fastdfs3/M00/6E/35/180x135/crop/-/ChOxM1u6yWOAAzwuAAOM7Qh-U1g933.png'}, {'815811': 'https://img1.qunliao.info/fastdfs3/M00/6D/84/180x135/crop/-/ChOxM1u5dxaAHTTQAAEBhT8ZDDk787.jpg'}, {'814697': 'https://img1.qunliao.info/fastdfs3/M00/6C/C7/180x135/crop/-/ChOxM1u4KtaAWFogAAG6eDlKIPU266.png'}, {'813611': 'https://img1.qunliao.info/fastdfs3/M00/6C/0A/180x135/crop/-/ChOxM1u2UZCAPFHUAAGHvRVZsoY492.jpg'}, {'812559': 'https://img1.qunliao.info/fastdfs3/M00/6B/94/180x135/crop/-/ChOxM1u1gx2AZ7qmAABi3gRdHS8715.jpg'}, {'812123': 'https://img1.qunliao.info/fastdfs3/M00/6B/00/180x135/crop/-/ChOxM1u0TnKAZfvOAABqEv13WnI588.jpg'}, {'795697': 'https://img1.qunliao.info/fastdfs3/M00/60/A7/180x135/crop/-/ChOxM1ufUh2AJdR0AABXtcU22fg956.jpg'}, {'811183': 'https://img1.qunliao.info/fastdfs3/M00/6A/47/180x135/crop/-/ChOxM1uy37KAOOTSAAFbvf9hNcY489.png'}, {'810539': 'https://img1.qunliao.info/fastdfs3/M00/69/B9/180x135/crop/-/ChOxM1uxj6qAKAoLAAFd1FBBUJQ053.png'}, {'809533': 'https://img1.qunliao.info/fastdfs3/M00/69/1E/180x135/crop/-/ChOxM1uwOkCAAwbQAAFLt9kao_E742.jpg'}, {'807937': 'https://img1.qunliao.info/fastdfs3/M00/68/62/180x135/crop/-/ChOxM1uu8N2ASTmFAAFvDBPbXRs820.png'}, {'807093': 'https://img1.qunliao.info/fastdfs3/M00/67/CA/180x135/crop/-/ChOxM1utl1qAX7gCAAJf0g1skuY665.png'}, {'806213': 'https://img1.qunliao.info/fastdfs3/M00/67/34/180x135/crop/-/ChOxM1usSWCAPPLpAAFjjkjEkQs483.jpg'}, {'804913': 'https://img1.qunliao.info/fastdfs3/M00/66/71/180x135/crop/-/ChOxM1uqoO2APMwvAAHVbqFXhxw860.jpg'}, {'804087': 'https://img1.qunliao.info/fastdfs3/M00/65/FC/180x135/crop/-/ChOxM1upwneAQKiZAANvxmCcnw0223.png'}, {'802767': 'https://img1.qunliao.info/fastdfs3/M00/64/E7/180x135/crop/-/ChOxM1unrmqAcsIAAANgWJFg5GM686.png'}, {'802051': 'https://img1.qunliao.info/fastdfs3/M00/64/7A/180x135/crop/-/ChOxM1um-eWAA4kiAAB8VgiYMXA187.jpg'}, {'800587': 'https://img1.qunliao.info/fastdfs3/M00/63/B5/180x135/crop/-/ChOxM1ulr92AVpDVAAFOPLEt8J4517.jpg'}, {'799761': 'https://img1.qunliao.info/fastdfs3/M00/63/1C/180x135/crop/-/ChOxM1ukXtOADRXCAAL2Y5F0Vi8342.png'}, {'798893': 'https://img1.qunliao.info/fastdfs3/M00/62/80/180x135/crop/-/ChOxM1ujGI2AGlb7AAIR5IDXzhs895.jpg'}, {'797779': 'https://img1.qunliao.info/fastdfs3/M00/61/CA/180x135/crop/-/ChOxM1uhtvGACNL_AAPvKSEhLJQ791.png'}]

    # print("下载图片...")
    # try:
    #     for p in nvshen_id_picture:
    #         for k, v in p.items():
    #             save_pic(v, k)
    #             time.sleep(2)
    # except:
    #     raise
    # print(("下载图片完成！"))

    w_list = ['吴宣仪', '30万', '826965', '68', '825847',
              'https://img1.dongqiudi.com/fastdfs3/M00/74/54/180x135/crop/-/ChOxM1vIPpOAZT8AAAHza_WMyRk175.png']
    g_list = ['关之琳', '20万', '813611', '88', '812559',
              'https://img1.dongqiudi.com/fastdfs3/M00/6B/94/180x135/crop/-/ChOxM1u1gx2AZ7qmAABi3gRdHS8715.jpg']
    t_list = ['佟丽娅', '22万', '797779', '93', '795697',
              'https://img1.dongqiudi.com/fastdfs3/M00/60/A7/180x135/crop/-/ChOxM1ufUh2AJdR0AABXtcU22fg956.jpg']
    y_list = ['杨丞琳', '7万', '1173681', '45', '1168209',
              'https://img1.qunliao.info/fastdfs4/M00/CA/F7/ChMf8F0pTOKAaefqAA5nOMM0LK0171.jpg']
    nvshen_list, special_page = deal_loaclfile(nvshen_id_picture)
    nvshen_list.append(w_list)
    nvshen_list.append(g_list)
    nvshen_list.append(t_list)
    nvshen_list.append(y_list)
    print(nvshen_list)
    print("保存数据")
    save_to_file(nvshen_list, "nvshen")
    print("保存完成")
    print("完成！")



