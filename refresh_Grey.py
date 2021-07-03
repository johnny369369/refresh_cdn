#!/usr/bin/env python
# ! coding=utf-8
import requests, json, os, sys
import pysnooper
# @pysnooper.snoop()
class Grey_operating():

      def __init__(self,token=None):
          self.grey_token = token
          self.grey_host = 'http://api2.greypanel.com'
          self.header = {'greycdn-token':self.grey_token,
                         "User-Agent": "Greypanel-CDN-API-V2",
                          'Content-Type': 'application/json'}

      def add_domain_to_grey(self,domain=None,uid='you uid'):
          '''添加域名到灰域
             从外部传入test.com,*.test.com域名逐一添加
             接口/api/v1/domain/create?uid=
             必选参数domain uid
          '''
          return_data = {}
          try:
              data = {'displayName':domain,
                       'sslEnable':'0'}
              api_url = f'{self.grey_host}/api/v1/domain/create?uid={uid}'
              response = requests.post(url=api_url,data=json.dumps(data),headers=self.header).json()
          except Exception as e:
              return_data['status'] = 'error'
              return_data['message'] = e.__str__()
              return  return_data
          else:
              return_data['data'] = response
              return return_data

      def upload_domain_cert_to_grey(self,domain=None):
          '''
          添加域名证书到灰域
          接口/api/v1/ssl/upload-cert
          必选参数 sslCrt sslKey sslAutoEnable sslForceEnable
          '''
          return_data = {}
          api_url = f'{self.grey_host}/api/v1/ssl/upload-cert'
          cert_path = '/opt/project/scripts/cert_path'
          try:
              with open(f'{cert_path}/{domain}.key','r') as f:
                   domainkey = f.read()
              with open(f'{cert_path}/{domain}.crt','r') as f:
                   domaincrt = f.read()
              data = {'sslCrt':domaincrt,"sslKey":domainkey,"sslAutoEnable": '0',"sslForceEnable": '0' }
              response = requests.post(url=api_url,data=json.dumps(data),headers=self.header)
          except Exception as e:
              return_data['status'] = 'error'
              return_data['message'] = e.__str__()
          else:
              return response.json()

      def get_grey_site_list(self):
          '''
          获取灰域站点列表 返回站点信息
          接口/api/v1/site/list/all
          必选参数token
          '''
          return_data = {}
          try:
              api_url = f'{self.grey_host}/api/v1/site/list/all'
              response = requests.post(url=api_url,headers=self.header).json()
          except Exception as e:
                 return_data['status'] = 'error'
                 return_data['message'] = e.__str__()
          else:
              return response

      def refresh_cdn(self):
          '''
          刷新灰域CDN
          接口api/v1/cache/purge/by-site?uid=
          必选参数uid
          先获取站点列表信息 然后把获取的信息存入字典 在字典获取到站点的UID结合URL POST发出请求
          '''
          return_data = {}
          try:
              web_site_dict = {}
              get_site = self.get_grey_site_list()
              for site_list in get_site['result']:
                  web_site_dict[site_list['name']] = site_list['uid']
              for site in web_site_dict.keys():
                  print(site)
              choose_site = input('请选择要刷新的站点:')
              api_url = '{}/api/v1/cache/purge/by-site?uid={}'.format(self.grey_host,web_site_dict[choose_site])
              response = requests.post(url=api_url,headers=self.header).json()
          except Exception as e:
              return_data['status'] = 'error'
              return_data['message'] = e.__str__()
              return  return_data
          else:
              return response


def check_menu_dict(data,title):
    '''菜单字典
       返回用户选择操作'''
    try:
        user_input = ''
        while user_input.strip() not in data:
            for key in data:
                print('\t',key)
            user_input = input(f'请选择{title},或输入q退出:').strip()
            if user_input == 'q':
                sys.exit(1)
        return user_input.strip()
    except Exception as e:
        print(e.__str__())

if __name__ == '__main__':
   Token_Dict = {'you-product':'you-token','you-product':'you-toekn'}
   # domain_list = ['test.com','*.test.com']
   # for domain in domain_list:
   #     print(start.add_domain_to_grey(domain))
   # print(start.upload_domain_cert_to_grey(domain='test.com'))
   # print(start.refresh_cdn())
   Select_Product = check_menu_dict(Token_Dict,'你操作的产品')
   start = Grey_operating(Token_Dict[Select_Product])
   start.refresh_cdn()
