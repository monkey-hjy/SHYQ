import collections
import re
import time

from pyecharts import options as opts
from pyecharts.charts import Bar, Timeline, Line, Grid
import datetime
import gne

import requests
from lxml import etree


def get_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.83 Safari/537.36'
    }
    urls = [
        'https://wsjkw.sh.gov.cn/yqtb/index.html',
        'https://wsjkw.sh.gov.cn/yqtb/index_2.html',
        'https://wsjkw.sh.gov.cn/yqtb/index_3.html',
        'https://wsjkw.sh.gov.cn/yqtb/index_4.html',
    ]
    res = list()
    for url in urls:
        response = requests.get(url, headers=headers)
        html = etree.HTML(response.text)
        news_urls = html.xpath("//a[contains(text(), '新增本土新冠肺炎确诊病例')]/@href")
        for n_u in news_urls:
            now_res = collections.defaultdict(int)
            date = datetime.datetime.strptime(n_u.split('/')[2], '%Y%m%d') - datetime.timedelta(days=1)
            if date <= datetime.datetime.strptime('20220325', '%Y%m%d'):
                break
            date = str(date.date())
            n_u = 'https://wsjkw.sh.gov.cn' + n_u
            response = requests.get(n_u, headers=headers)
            response = re.sub('<.*?>', '', response.text)
            res_content = re.findall('无症状感染者(\d+)—无症状感染者(\d+)，居住于(.*?)，', response)
            res_content += re.findall('病例(\d+)—病例(\d+)，居住于(.*?)，', response)
            for info in res_content:
                now_res[info[2]] += int(info[1]) - int(info[0])
            now_res = dict(now_res)
            print(date, now_res)
            res.append([date, now_res])

    urls = [
        'https://wsjkw.sh.gov.cn/yqtb/index_4.html',
        'https://wsjkw.sh.gov.cn/yqtb/index_5.html',
    ]
    for url in urls:
        response = requests.get(url, headers=headers)
        html = etree.HTML(response.text)
        news_urls = html.xpath("//a[contains(text(), '新增本土新冠肺炎确诊病例')]/@href")
        for n_u in news_urls:
            now_res = dict()
            date = datetime.datetime.strptime(n_u.split('/')[2], '%Y%m%d') - datetime.timedelta(days=1)
            if date >= datetime.datetime.strptime('20220326', '%Y%m%d'):
                continue
            if date < datetime.datetime.strptime('20220306', '%Y%m%d'):
                break
            date = str(date.date())
            n_u = 'https://wsjkw.sh.gov.cn' + n_u
            response = requests.get(n_u, headers=headers)
            response = re.sub('<.*?>|&quot;', '', response.text)
            res_content = re.findall('岁，居住于(.*?)区', response)
            res_content += re.findall('岁，居住地为(.*?)区', response)
            for q_name in set(res_content):
                now_res[q_name + '区'] = res_content.count(q_name)
            print(date, now_res)
            res.append([date, now_res])
    res.append(['START', {
            '浦东新区': 0,
            '黄浦区': 0,
            '徐汇区': 0,
            '长宁区': 0,
            '静安区': 0,
            '普陀区': 0,
            '虹口区': 0,
            '杨浦区': 0,
            '闵行区': 0,
            '宝山区': 0,
            '嘉定区': 0,
            '金山区': 0,
            '松江区': 0,
            '青浦区': 0,
            '奉贤区': 0,
            '崇明区': 0,
        }])
    return list(reversed(res))


all_data = get_data()
t1 = Timeline(init_opts=opts.InitOpts(width='1400px', height='700px'))     # 创建 Timeline对象
q_data = {
    '浦东新区': 0,
    '黄浦区': 0,
    '徐汇区': 0,
    '长宁区': 0,
    '静安区': 0,
    '普陀区': 0,
    '虹口区': 0,
    '杨浦区': 0,
    '闵行区': 0,
    '宝山区': 0,
    '嘉定区': 0,
    '金山区': 0,
    '松江区': 0,
    '青浦区': 0,
    '奉贤区': 0,
    '崇明区': 0,
}
line_x = list()
line_y = list()
for date, info in all_data:
    grid = Grid()
    q_data = {k: v + info.get(k, 0) for k, v in q_data.items()}
    now_data = sorted(q_data.items(), key=lambda x: x[1], reverse=False)
    x_list = list()
    y_list = list()
    for x, y in now_data:
        x_list.append(x)
        y_list.append(y)
    bar = (Bar()
           .add_xaxis(x_list)
           .add_yaxis(series_name='人数', y_axis=y_list, label_opts=opts.LabelOpts(position='left', font_size=14))
           .set_series_opts(label_opts=opts.LabelOpts(is_show=True, position='right', font_size=12, color='blue'))
           .reversal_axis()
           .set_global_opts(
      title_opts=opts.TitleOpts(
        "{} 新增 {} 例\t\t共 {} 例".format(date, sum(info.values()), sum(q_data.values())),
        pos_left='30%',
        pos_top='55%',
        title_textstyle_opts=opts.TextStyleOpts(
          font_style='oblique',
          color='red',
          font_weight="bold",
          font_size=20)),
        legend_opts=opts.LegendOpts(pos_right='10%'),
        yaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(font_size=12))
    )
    )
    line_x.append(date)
    line_y.append(sum(info.values()))
    line = Line().add_xaxis(line_x).add_yaxis(series_name='人数', y_axis=line_y, is_smooth=True)
    grid.add(bar, grid_opts=opts.GridOpts(pos_bottom='50%'))
    grid.add(line, grid_opts=opts.GridOpts(pos_top='60%'))
    t1.add(grid, date[5:])

t1.add_schema(
    symbol='arrow',             # 设置标记时间；
    symbol_size=2,              # 标记大小;
    play_interval=1000,         # 播放时间间隔；
    control_position='right',   # 控制位置;
    linestyle_opts=opts.LineStyleOpts(
        width=10,
        type_='dashed',
        color='rgb(255,0,0,0.5)'
    ),
    label_opts=opts.LabelOpts(
        color='rgb(0,0,255,0.5)',
        font_size=15,
        font_style='italic',
        font_weight='bold',
        font_family='Time New Roman',
        position='left',
        interval=20,
    )
)
t1.render("timeline_bar.html")


