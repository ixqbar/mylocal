#!/usr/bin/env python
#-*-coding:utf-8-*-
#
#
#@author ixqbar@gmail.com http://xingqiba.sinaapp.com/
#
# 漯河 http://ext.weather.com.cn/101181501.json
# 上海 http://ext.weather.com.cn/101020100.json
# 曹县 http://ext.weather.com.cn/101121007.json
#
#
#
#
#{"l":"冬月廿三","c":"101020100","n":"上海","en":"shanghai","t":3,"w":"西北风 1级","h":59,"s":"雨夹雪#","d1":{"l":"3","h":"0","s":"雨夹雪","w":"北风"},"d2":{"l":"5","h":"1","s":"阴"},"d3":{"l":"6","h#":"3","s":"小雨"},"w1":"北风","i":{"cityid":"101020100","cy":{"level":"7级","label":"冷","descrip#tion":"天气冷，建议着棉衣、皮夹克加羊毛衫等冬季服装。年老体弱者宜着厚棉衣或冬大衣。"},"xc":{"level":"4级","la#bel":"不宜","description":"不宜洗车，未来24小时内有雨，如果在此期间洗车，雨水和路上的泥水可能会再次弄脏您的爱车#。"},"uv":{"level":"1级","label":"最弱","description":"属弱紫外线辐射天气，无需特别防护。若长期在户外，建##议涂擦SPF在8-12之间的防晒护肤品。"}}}
#

from urllib2 import urlopen,Request
import json
import os

def weather():
    #city_list = [{'city_id' : '101020100', 'city_name' : '上海'}, {'city_id' : '101181501', 'city_name' : '漯河'}, {'city_id' : '101121007', 'city_name' : '曹县'}];
    #city_list = [{'city_id' : '101020100', 'city_name' : '上海'}, {'city_id' : '101181501', 'city_name' : '漯河'}];
    city_list = [{'city_id' : '101020100', 'city_name' : '上海'}];
    current_path = os.path.split(__file__)[0] + '/'
    message = []
    for city_info in city_list:
        url     = 'http://ext.weather.com.cn/%s.json' % (city_info['city_id'])
        req     = Request(url, headers={"Referer":"http://ext.weather.com.cn/10200.html"})
        data    = urlopen(req).read()
        result  = json.loads(data.decode('utf-8'))
        message0 = "%s:今日%s℃/%s℃ %s %s" % (city_info['city_name'], result['d1']['l'].encode('utf-8'), result['d1']['h'].encode('utf-8'), result['d1']['s'].encode('utf-8'), result['d1']['w'].encode('utf-8') if result['d1'].has_key('w') else '')
        message1 = "明日%s℃/%s℃ %s %s" % (result['d2']['l'].encode('utf-8'), result['d2']['h'].encode('utf-8'), result['d2']['s'].encode('utf-8'), result['d2']['w'].encode('utf-8') if result['d2'].has_key('w') else '')
        message2 = "后日%s℃/%s℃ %s %s" % (result['d3']['l'].encode('utf-8'), result['d3']['h'].encode('utf-8'), result['d3']['s'].encode('utf-8'), result['d3']['w'].encode('utf-8') if result['d3'].has_key('w') else '')
        message.append('%s,%s,%s' % (message0, message1, message2))

    #command = '%sfetion --mobile=13671527966 --pwd= --exit-on-verifycode --to=13671527966,18201763461 --msg-utf8="%s"' % (current_path, ','.join(message))
    command = '%sfetion --mobile=13671527966 --pwd= --to=13671527966,18201763461 --msg-utf8="%s"' % (current_path, ','.join(message))
    print(command)
    os.system(command)

if __name__ == '__main__':
    weather()
