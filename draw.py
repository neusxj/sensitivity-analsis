import plotly.figure_factory as ff
from datetime import datetime
from plotly.offline import plot, iplot
from json2dict import json2dict
import random


def draw_gantt(results):
    df = json2dict(results) #每个炉次的加工开始时间、加工持续时间、加工结束时间和炉次号整理为一个集合，把该集合命名为df
    df.sort(key = lambda x: x['Task'], reverse = False)

    #colors = ['#7a0504', (0.2, 0.7, 0.3), 'rgb(210, 60, 180)']
    #colors = ["#FCB711", "#F37021", "#CC004C", "#6460AA", "#0089D0", "#0DB14B","#FC0504", "#647021"]
    colors = []
    for k in range(len(results)):
        colorTuple = tuple(random.randint(1, 100)/100 for i in range(3))
        colors.append(colorTuple)

    fig = ff.create_gantt(df, colors=colors, index_col='Resource',
                          reverse_colors=True, show_colorbar=True, group_tasks=True)
    
    #fig = ff.create_gantt(df)
    plot(fig, filename='gantt-use-a-pandas-dataframe.html')
