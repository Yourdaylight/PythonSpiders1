# processing.py
import re, os
import jieba
import requests
import pandas as pd
from pyecharts import options as opts
from pyecharts.charts import WordCloud
from pyecharts.commons.utils import JsCode
from pyecharts.charts import Line, Grid
import matplotlib.pyplot as plt

plt.rcParams['font.sans-serif'] = 'SimHei'
plt.rcParams['axes.unicode_minus'] = False

cid = "189702747"
save_name = "houlang"


def get_bullet(cid):
    """爬取弹幕"""
    if not os.path.exists(f'{cid}.xml'):
        cid = "189702747"
        url = f'https://comment.bilibili.com/{cid}.xml'
        res = requests.get(url)
        # 保存到本地
        with open(f'{cid}.xml', 'wb') as f:
            f.write(res.content)


def process_xml(cid, csv_name):
    """将爬取的xml文件转成csv"""
    if os.path.exists(f'{cid}.xml'):
        with open(f'{cid}.xml', encoding='utf-8') as f:
            data = f.read()
        comments = re.findall('<d p="(.*?)">(.*?)</d>', data)
        print("弹幕数据爬取完成:{}条".format(len(comments)))
        # 转成csv后保存
        danmus = [','.join(item) for item in comments]
        headers = ['stime', 'mode', 'size', 'color', 'date', 'pool', 'author', 'dbid', 'text']
        headers = ','.join(headers)
        danmus.insert(0, headers)
        with open(f'{csv_name}.csv', 'w', encoding='utf_8_sig') as f:
            f.writelines([line + '\n' for line in danmus])


def plot_wordcloud(text=None, csv_name=None):
    # 读取弹幕文件绘图
    if csv_name:
        with open(f'{csv_name}.csv', encoding='utf-8') as f:
            text = " ".join([line.split(',')[-1] for line in f.readlines()])
    # 这行用来读取评论数据绘图
    text = " ".join(text) if isinstance(text, list) else text
    # 统一逻辑
    words = jieba.cut(text)
    _dict = {}
    for word in words:
        if len(word) >= 2:
            _dict[word] = _dict.get(word, 0) + 1
    items = list(_dict.items())
    items.sort(key=lambda x: x[1], reverse=True)

    c = (
        WordCloud().add(
            "",
            items,
            word_size_range=[20, 120],
            textstyle_opts=opts.TextStyleOpts(font_family="cursive"),
        ).render("wordcloud_%s.html" % csv_name)
    )


def plot_time_trend(save_name):
    """时间与评论信息关系图"""
    with open(f'{save_name}.csv', encoding='utf-8') as f:
        text = [float(line.split(',')[0]) for line in f.readlines()[1:]]
    text = sorted([int(item) for item in text])
    data = {}
    for item in text:
        item = int(item / 60)
        data[item] = data.get(item, 0) + 1

    x_data = list(data.keys())
    y_data = list(data.values())
    # 配置折线图参数
    background_color_js = (
        "new echarts.graphic.LinearGradient(0, 0, 0, 1, "
        "[{offset: 0, color: '#c86589'}, {offset: 1, color: '#06a7ff'}], false)"
    )
    area_color_js = (
        "new echarts.graphic.LinearGradient(0, 0, 0, 1, "
        "[{offset: 0, color: '#eb64fb'}, {offset: 1, color: '#3fbbff0d'}], false)"
    )
    c = (
        Line(init_opts=opts.InitOpts(bg_color=JsCode(background_color_js)))
            .add_xaxis(xaxis_data=x_data)
            .add_yaxis(
            series_name="弹幕数量",
            y_axis=y_data,
            is_smooth=True,
            symbol="circle",
            symbol_size=6,
            linestyle_opts=opts.LineStyleOpts(color="#fff"),
            label_opts=opts.LabelOpts(is_show=True, position="top", color="white"),
            itemstyle_opts=opts.ItemStyleOpts(
                color="red", border_color="#fff", border_width=3
            ),
            tooltip_opts=opts.TooltipOpts(is_show=True),
            areastyle_opts=opts.AreaStyleOpts(
                color=JsCode(area_color_js), opacity=1),
            markpoint_opts=opts.MarkPointOpts(
                data=[opts.MarkPointItem(type_="max")])
        )
            .set_global_opts(
            title_opts=opts.TitleOpts(
                title="",
                pos_bottom="5%",
                pos_left="center",
                title_textstyle_opts=opts.TextStyleOpts(
                    color="#fff", font_size=16),
            ),
            xaxis_opts=opts.AxisOpts(
                type_="category",
                boundary_gap=False,
                axistick_opts=opts.AxisTickOpts(
                    is_show=True,
                    length=25,
                    linestyle_opts=opts.LineStyleOpts(color="#ffffff1f"),
                ),
                splitline_opts=opts.SplitLineOpts(
                    is_show=True, linestyle_opts=opts.LineStyleOpts(color="#ffffff1f")
                )
            ),
            yaxis_opts=opts.AxisOpts(
                type_="value",
                position="left",
                axistick_opts=opts.AxisTickOpts(
                    is_show=True,
                    length=15,
                    linestyle_opts=opts.LineStyleOpts(color="#ffffff1f"),
                ),
                splitline_opts=opts.SplitLineOpts(
                    is_show=True, linestyle_opts=opts.LineStyleOpts(color="#ffffff1f")
                ),
            ),
            legend_opts=opts.LegendOpts(is_show=False),
            tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="line")
        )
            .render("highlights.html")
    )


def plot_time_date(csv_name, key="date", encoding="utf-8"):
    """绘制每日评论数据时间趋势图"""
    df = pd.read_csv(csv_name + ".csv", encoding=encoding, error_bad_lines=False)
    # 时间戳转日期
    df["date"] = pd.to_datetime(df[key].astype("int"), unit='s')
    df = df.set_index("date")
    df = df.resample('D').count()
    df.iloc[:, 0].plot(xlabel="date", title=csv_name + "每日评论数量")
    plt.savefig(csv_name + ".png")
    plt.show()



def get_comments(save_name):
    """
    爬取评论数据
    :return:
    """
    save_name = "%s_comments.csv" % save_name
    res = {
        "ctime": [],
        "content": []
    }
    if not os.path.exists(save_name):
        base_url = "https://api.bilibili.com/x/v2/reply/main?csrf=d2aeb9c43da1fbc7e93b0689d461733d&mode=3&next={}&oid=412935552&plat=3&type=1"
        # 分页爬取评论数据
        for page in range(2, 20):
            try:
                url = base_url.format(page)
                content = requests.get(url).json()
                data = content.get("data").get("replies")
                for item in data:
                    # 解析数据，提取时间和评论内容
                    ctime = item["ctime"]
                    content = item["content"]["message"]
                    res["ctime"].append(ctime)
                    res["content"].append(content)
                    if item.get("replies"):
                        for j in item["replies"]:
                            ctime = j["ctime"]
                            content = j["content"]["message"]
                            res["ctime"].append(ctime)
                            res["content"].append(content)
            except Exception:
                print("error page:{}".format(page))
        # 保存
        pd.DataFrame(res).to_csv(save_name)
    print("评论数据爬取完成:{}条".format(len(res["content"])))


def compare_with_bullet_comments():
    """"弹幕与评论对比")"""
    res = {"ctime": [], "type": []}
    bullet_comments = pd.read_csv(save_name + ".csv", encoding="utf-8",error_bad_lines=False)
    res["ctime"].extend(bullet_comments["color"].tolist())
    res["type"].extend(["bullet" for i in range(len(bullet_comments))])
    comments = pd.read_csv(save_name + "_comments.csv", encoding="gbk",error_bad_lines=False)
    res["ctime"].extend(comments["ctime"].tolist())
    res["type"].extend(["comment" for i in range(len(comments))])
    df = pd.DataFrame(res)
    df["ctime"] = pd.to_datetime(df["ctime"].astype("int"), unit='s')
    df = df.set_index("ctime")
    df1 = df[df["type"]=="bullet"].resample('D').count()
    df2 = df[df["type"]=="comment"].resample('D').count()
    plt.scatter(df1.index,df1.type,label="弹幕数量")
    plt.scatter(df2.index,df2.type,label="评论数量")
    plt.title("弹幕与评论对比")
    plt.legend()
    plt.savefig("compare.png")
    plt.show()

def main():
    # 爬取弹幕数据保存本地
    get_bullet(cid)
    process_xml(cid, save_name)
    # 爬取评论数据保存本地
    get_comments(save_name)
    # 评论数据词云图
    comments = pd.read_csv(save_name + "_comments.csv", encoding="gbk")
    plot_wordcloud(comments["content"].tolist())
    # 弹幕数据词云图
    plot_wordcloud(None, save_name)
    # 弹幕数据时间弹幕关系图
    plot_time_trend(save_name)
    # 绘制弹幕时间趋势
    plot_time_date(save_name, key="color")
    # 绘制评论时间趋势
    plot_time_date(save_name + "_comments", encoding="gbk", key="ctime")
    # 弹幕与评论对比
    compare_with_bullet_comments()
    print("全部处理完成！")

if __name__ == '__main__':
    main()
