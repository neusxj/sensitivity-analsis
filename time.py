# -*- coding: utf-8 -*-
"""
Created on Mon Apr  8 13:47:15 2019

@author: ZeroPC
"""
import time,datetime
timeDateStr='2020-04-10 10:20:16'
def time_char_to_minute(timeDateStr):
    time1=datetime.datetime.strptime(timeDateStr,"%Y-%m-%d %H:%M:%S")  #timeDateStr日期输出格式化并转换成数组形式，datatime类的静态方法
    secondsFrom1970=time.mktime(time1.timetuple())   #它把一个时间元组转换成时间戳，返回用秒数表示时间的浮点数
    ticks = time.time()     #系统当前转换为时间戳，时间戳是指格林威治时间1970年01月01日00时00分00秒(北京时间1970年01月01日08时00分00秒)起至现在的总秒数。
    time_result=(secondsFrom1970-ticks)/60  #转换为分钟
    time_result=float('%.2f' % time_result)
    return int(time_result)
print(time_char_to_minute(timeDateStr))    