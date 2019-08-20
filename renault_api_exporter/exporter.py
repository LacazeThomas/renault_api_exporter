#!/usr/bin/python

import json
import time
from prometheus_client import start_http_server
from prometheus_client.core import GaugeMetricFamily, REGISTRY
import argparse
import yaml
from objectpath import *
import logging
import dateutil.parser
import asyncio
import aiohttp
import json
import urllib
# -*- coding: utf-8 -*-

class JsonPathCollector(object):
  def __init__(self, config):
    self._config = config

  def collect(self):
    config = self._config
    result_tree = Tree(JSON)
    for metric_config in config['metrics']:
      metric_name = "{}_{}".format(config['metric_name_prefix'], metric_config['name'])
      metric_description = metric_config.get('description', '')
      metric_path = metric_config['path']
      value = result_tree.execute(metric_path)
      if(metric_name == "zoe_lastUpdateTime"):
        value = dateutil.parser.parse(result_tree.execute(metric_path)).strftime('%s')
        logging.debug("metric_name: {}, value for '{}' : {}".format(metric_name, metric_path, value))
        metric = GaugeMetricFamily(metric_name, metric_description, value=value)
        yield metric
      else:
        logging.debug("metric_name: {}, value for '{}' : {}".format(metric_name, metric_path, value))
        metric = GaugeMetricFamily(metric_name, metric_description, value=value)
        yield metric

async def get_android_config(session, location):
    url = 'https://renault-wrd-prod-1-euw1-myrapp-one.s3-eu-west-1.amazonaws.com/configuration/android/config_' + location + '.json'
    async with session.get(url) as response:
        responsetext = await response.text()
        if responsetext == '':
            responsetext = '{}'
        jsonresponse = json.loads(responsetext)
        if 'message' in jsonresponse:
            self.tokenData = None
            raise MyRenaultServiceException(jsonresponse['message'])
        print('done')
        return jsonresponse

async def get_gigyasession(session, gigyarooturl, gigyaapikey, loginID, password):
    payload = {'loginID': loginID, 'password': password, 'apiKey': gigyaapikey}
    url = gigyarooturl + '/accounts.login?' + urllib.parse.urlencode(payload)
    async with session.get(url) as response:
        responsetext = await response.text()
        if responsetext == '':
            responsetext = '{}'
        jsonresponse = json.loads(responsetext)
        if 'message' in jsonresponse:
            self.tokenData = None
            raise MyRenaultServiceException(jsonresponse['message'])
        return jsonresponse

async def get_gigyaaccount(session, gigyarooturl, gigyaapikey, gigyacookievalue):
    payload = {'oauth_token': gigyacookievalue}
    url = gigyarooturl + '/accounts.getAccountInfo?' + urllib.parse.urlencode(payload)
    async with session.get(url) as response:
        responsetext = await response.text()
        if responsetext == '':
            responsetext = '{}'
        jsonresponse = json.loads(responsetext)
        if 'message' in jsonresponse:
            self.tokenData = None
            raise MyRenaultServiceException(jsonresponse['message'])
        return jsonresponse

async def get_gigyajwt(session, gigyarooturl, gigyaapikey, gigyacookievalue):
    payload = {'oauth_token': gigyacookievalue, 'fields': 'data.personId,data.gigyaDataCenter', 'expiration': 900}
    url = gigyarooturl + '/accounts.getJWT?' + urllib.parse.urlencode(payload)
    async with session.get(url) as response:
        responsetext = await response.text()
        if responsetext == '':
            responsetext = '{}'
        jsonresponse = json.loads(responsetext)
        if 'message' in jsonresponse:
            self.tokenData = None
            raise MyRenaultServiceException(jsonresponse['message'])
        return jsonresponse

async def get_kamereonperson(session, kamereonrooturl, kamereonapikey, gigya_jwttoken, personId):
    payload = {'country': 'FR'}
    headers = {'x-gigya-id_token': gigya_jwttoken, 'apikey': kamereonapikey}
    url = kamereonrooturl + '/commerce/v1/persons/' + personId + '?' + urllib.parse.urlencode(payload)
    async with session.get(url, headers=headers) as response:
        responsetext = await response.text()
        if responsetext == '':
            responsetext = '{}'
        jsonresponse = json.loads(responsetext)
        if 'message' in jsonresponse:
            self.tokenData = None
            raise MyRenaultServiceException(jsonresponse['message'])
        return jsonresponse

async def get_kamereontoken(session, kamereonrooturl, kamereonapikey, gigya_jwttoken, accountId):
    payload = {'country': 'FR'}
    headers = {'x-gigya-id_token': gigya_jwttoken, 'apikey': kamereonapikey}
    url = kamereonrooturl + '/commerce/v1/accounts/' + accountId + '/kamereon/token?' + urllib.parse.urlencode(payload)
    async with session.get(url, headers=headers) as response:
        responsetext = await response.text()
        if responsetext == '':
            responsetext = '{}'
        jsonresponse = json.loads(responsetext)
        if 'message' in jsonresponse:
            self.tokenData = None
            raise MyRenaultServiceException(jsonresponse['message'])
        return jsonresponse

async def get_status(session, kamereonrooturl, kamereonapikey, gigya_jwttoken, kamereonaccesstoken, vin, typeapi):
    headers = {'x-gigya-id_token': gigya_jwttoken, 'apikey': kamereonapikey, 'x-kamereon-authorization' : 'Bearer ' + kamereonaccesstoken}
    url = kamereonrooturl + '/commerce/v1/accounts/kmr/remote-services/car-adapter/v1/cars/' + vin + '/' + typeapi
    async with session.get(url, headers=headers) as response:
        responsetext = await response.text()
        if responsetext == '':
            responsetext = '{}'
        jsonresponse = json.loads(responsetext)
        if 'message' in jsonresponse:
            self.tokenData = None
            raise MyRenaultServiceException(jsonresponse['message'])
        return jsonresponse

async def main():
    async with aiohttp.ClientSession() as session:await mainwithsession(session)

async def mainwithsession(session):
    global JSON
    android_config = await get_android_config(session, CREDENTIALS_RenaultServiceLocation)
    with open('android_config.json', 'w') as outfile:
        json.dump(android_config, outfile)
    
    gigyarooturl = android_config['servers']['gigyaProd']['target']
    gigyaapikey = android_config['servers']['gigyaProd']['apikey']

    kamereonrooturl = android_config['servers']['wiredProd']['target']
    kamereonapikey = android_config['servers']['wiredProd']['apikey']
    
    gigya_session = await get_gigyasession(session, gigyarooturl, gigyaapikey, CREDENTIALS_RenaultServicesUsername, CREDENTIALS_RenaultServicesPassword)
    with open('gigya_session.json', 'w') as outfile:
        json.dump(gigya_session, outfile)
    
    gigyacookievalue = gigya_session['sessionInfo']['cookieValue']

    gigya_account = await get_gigyaaccount(session, gigyarooturl, gigyaapikey, gigyacookievalue)
    with open('gigya_account.json', 'w') as outfile:
        json.dump(gigya_account, outfile)

    gigya_jwt = await get_gigyajwt(session, gigyarooturl, gigyaapikey, gigyacookievalue)
    with open('gigya_jwt.json', 'w') as outfile:
        json.dump(gigya_jwt, outfile)
    
    gigya_jwttoken= gigya_jwt['id_token']
    
    kamereonpersonid = gigya_account['data']['personId']
    
    kamereon_person = await get_kamereonperson(session, kamereonrooturl, kamereonapikey, gigya_jwttoken, kamereonpersonid)
    with open('kamereon_person.json', 'w') as outfile:
        json.dump(kamereon_person, outfile)
    kamereonaccountid = kamereon_person['accounts'][0]['accountId']

    kamereon_token = await get_kamereontoken(session, kamereonrooturl, kamereonapikey, gigya_jwttoken, kamereonaccountid)
    with open('kamereon_token.json', 'w') as outfile:
        json.dump(kamereon_token, outfile)
    
    kamereonaccesstoken = kamereon_token['accessToken']

    kamereon_battery = await get_status(session, kamereonrooturl, kamereonapikey, gigya_jwttoken, kamereonaccesstoken, CREDENTIALS_VIN,"battery-status")
    JSON = json.loads(json.dumps(kamereon_battery))

    kamereon_cockpit = await get_status(session, kamereonrooturl, kamereonapikey, gigya_jwttoken, kamereonaccesstoken, CREDENTIALS_VIN, "cockpit")
    jsonToAppend = json.loads(json.dumps(kamereon_cockpit))
    JSON['data']['attributes'].update(jsonToAppend['data']['attributes'])


def getRenaultAPI():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

if __name__ == "__main__":
  global CREDENTIALS_RenaultServiceLocation,CREDENTIALS_RenaultServicesUsername,CREDENTIALS_RenaultServicesPassword,CREDENTIALS_VIN
  parser = argparse.ArgumentParser(description='Expose metrics bu jsonpath for configured url')
  parser.add_argument('config_file_path', help='Path of the config file')
  args = parser.parse_args()
  with open(args.config_file_path) as config_file:
    config = yaml.load(config_file, yaml.SafeLoader)
    log_level = config.get('log_level')
    CREDENTIALS_RenaultServiceLocation = config.get('RenaultServiceLocation')
    CREDENTIALS_RenaultServicesUsername = config.get('RenaultServiceUsername')
    CREDENTIALS_RenaultServicesPassword = config.get('RenaultServicePassword')
    CREDENTIALS_VIN = config.get('RenaultServiceVIN')
    API_Refresh = config.get('RenaultServiceAPIRefresh')
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.getLevelName(log_level.upper()))
    exporter_port = config.get('exporter_port')
    logging.debug("Config %s", config)
    logging.info('Starting server on port %s', exporter_port)
    start_http_server(exporter_port)
    getRenaultAPI()
    REGISTRY.register(JsonPathCollector(config))
  while True:
      time.sleep(API_Refresh)
      getRenaultAPI()