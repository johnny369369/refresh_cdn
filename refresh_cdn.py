# -*- coding:utf-8 -*-
import binascii
import hashlib
import sys,string,datetime,time,random,json,uuid,urllib,base64,hmac,os
import requests
import urllib.request, urllib.parse, urllib.error, urllib.request, urllib.error
from urllib import parse
from hashlib import sha1,sha256
import time
import pysnooper

#@pysnooper.snoop()
class Txy_api(object):
    def __init__(self,action=None,product=None):
        self.secretKey = 'your key' if product == 'your product' else 'your key'
        self.cdn_host = 'cdn.api.qcloud.com'
        self.cdn_url = '/v2/index.php'
        self.cdn_api = 'https://cdn.api.qcloud.com/v2/index.php'
        self.txy_params = {}
        self.txy_params['Action'] = action
        self.txy_params['Timestamp'] = str(int(time.time()))
        self.txy_params['Nonce'] = random.randint(1, sys.maxsize)
        self.txy_params['SecretId'] = 'your key id' if product == 'b79' else 'your key id'
        self.txy_params['Version'] = '2018-07-09'

    def make(self,method='POST'):
        p = {}
        for k in self.txy_params:
            p[k.replace('_', '.')] = self.txy_params[k]
        ps = '&'.join('%s=%s' % (k, p[k]) for k in sorted(p))
        msg = '%s%s%s?%s' % (method.upper(), self.cdn_host, self.cdn_url, ps)
        hashed = hmac.new(self.secretKey.encode(), msg.encode(), sha256).digest()
        return base64.b64encode(hashed).decode()

    def refreshcdn_dir(self,refresh_url):
        self.txy_params['dirs.0'] = refresh_url
        mysign = self.make()
        self.txy_params['Signature'] = mysign
        try:
            r = requests.post(self.cdn_api,self.txy_params)
            if int(r.status_code) == 200:
               print(f'\t\tTxy_cdn地址:{refresh_url}刷新成功')
        except Exception as e:
            print(f'网络连接失败:{self.cdn_api} 异常为:{e.__str__()}')

class Ali_api(object):
    def __init__(self,action=None,url=None):
        self.access_key_id = 'your key id'
        self.access_key_secret = 'your key'
        self.url = url

        self.ali_params = {}
        self.ali_params['Action'] = action
        self.ali_params['Format'] = 'json'
        self.ali_params['Version'] = '2014-11-11'
        self.ali_params['AccessKeyId'] = self.access_key_id
        self.ali_params['SignatureVersion'] = '1.0'
        self.ali_params['SignatureMethod'] = 'HMAC-SHA1'
        self.ali_params['SignatureNonce'] = str(uuid.uuid1())

    def percent_encode(self, ttt):
        res = urllib.parse.quote(ttt.encode('utf8'), '')
        res = res.replace('+', '%20')
        res = res.replace('*', '%2A')
        res = res.replace('%7E', '~')
        return res

    def compute_signature(self,ali_params,access_key_secret):
        sortedParameters = sorted(list(ali_params.items()), key=lambda ali_params: ali_params[0])
        canonicalizedQueryString = ''
        for (k, v) in sortedParameters:
            canonicalizedQueryString += '&' + self.percent_encode(k) + '=' + self.percent_encode(v)
        stringToSign = 'GET&%2F&' + self.percent_encode(canonicalizedQueryString[1:])
        h = hmac.new(bytes(access_key_secret + "&",'utf-8'), bytes(stringToSign,'utf-8'), sha1)
        signature = base64.encodebytes(h.digest()).strip()
        return signature

    def compose_url(self, user_params):
        for key in list(user_params.keys()):
            self.ali_params[key] = user_params[key]
        signature = self.compute_signature(self.ali_params,self.access_key_secret)
        self.ali_params['Signature'] = signature
        url = self.url + "/?" + urllib.parse.urlencode(self.ali_params)
        return url

    def refresh_cdn(self,ObjectPath,ObjectType):
        self.ali_params['TimeStamp'] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        self.ali_params['ObjectPath'] = ObjectPath
        self.ali_params['ObjectType'] = ObjectType
        result_url = self.compose_url(self.ali_params)
        try:
            r = requests.get(result_url)
            if int(r.status_code) == 200:
               print(f'\t\tAli_cdn地址:{ObjectPath}刷新成功')
        except Exception as e:
            print(f'网络连接失败:{result_url} 异常信息为:{e.__str__()}')

# @pysnooper.snoop()
class Qs_cloud(object):

    def __init__(self):
        self.apikey = 'your key'
        self.username = 'your email'
        self.urlhost = 'https://open.chinanetcenter.com'
        self.date = datetime.datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
        self.headers = {
            'Date': self.date,
            'Content-type': 'application/json'
        }
        self.method = 'post'
        self.passwd = self.getAuth()

    def getAuth(self):
        signed_apikey = hmac.new(self.apikey.encode('utf-8'), self.date.encode('utf-8'), sha1).digest()
        signed_apikey = base64.b64encode(signed_apikey)
        return signed_apikey

    def refresh_cdn(self,url):
        try:
            cdnurl = f'{self.urlhost}/ccm/purge/ItemIdReceiver'
            data = '{"urls": ["%s"]}' % (url)
            if self.method.upper() == 'POST':
               r = requests.post(cdnurl, data=data, headers=self.headers,auth=(self.username,self.passwd))
            else:
               r = requests.get(cdnurl, headers=headers)
        except Exception as e:
            print(f'Error:刷新全速云CDN失败异常:{e.__str__()}')
        else:
            return r.json()
def Usage():
    print('\t缺少供应商简称参数或刷新cdn_url参数')
    print('\t目前有CDN厂商有 ali txy qsy')
    print('\t使用示例 python refresh_cdn.py ali url')

if __name__ == '__main__':
    if len(sys.argv) < 3:
       Usage()
    else:
        product = sys.argv[1]
        refresh_url = sys.argv[2]
        if product == 'ali':
           ali = Ali_api(action='RefreshObjectCaches', url='https://cdn.aliyuncs.com')
           ali.refresh_cdn(ObjectPath=refresh_url, ObjectType='Directory')
        elif product == 'qsy':
           qs = Qs_cloud().refresh_cdn(refresh_url)
           if result['Code'] == '1':
              print(f'全速云Cdn地址:{refresh_url}刷新url和目录成功')
        elif product == 'txy':
           if str('keywords') in str(refresh_url):
              txy = Txy_api(action='RefreshCdnDir',product='nwf')
              txy.refreshcdn_dir(refresh_url=refresh_url)
           elif str('dkeywords') in str(refresh_url) or str('keywords') in str(refresh_url):
              txy = Txy_api(action='RefreshCdnDir',product='your product')
              txy.refreshcdn_dir(refresh_url=refresh_url)
           else:
               txy = Txy_api(action='RefreshCdnDir', product='your product')
               txy.refreshcdn_dir(refresh_url=refresh_url)
        else:
            print('没有找到对应CDN产品号')

