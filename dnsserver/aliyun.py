from .idnsserver import servers, IDNSServer
from urllib.parse import quote
import uuid
import hmac
import base64
import hashlib
import logging
from datetime import datetime
import requests


class AliyunDNSServer(IDNSServer):
    ALIDNS_SITE = 'https://alidns.aliyuncs.com'

    def __request(self, method, params=None, **param_dict)->requests.Response:
        if params:
            params.update(param_dict)
        else:
            params = param_dict
        params = self.__signature_with_public_prama(method, params)
        response = requests.request(method, self.ALIDNS_SITE, params=params)
        return response

    def __init__(self, config):
        self.records = dict()
        self.ALIYUN_ACCESS_KEY_ID = config.get('accesskey')
        self.ALIYUN_ACCESS_KEY_SECRET = config.get('secret')

    def refresh_dns_record(self):
        new_records = dict()
        for prefix, domain in self.records:
            new_records[(prefix, domain)] = self.__get_dns_record(
                prefix, domain)
        self.records = new_records

    def clear(self):
        self.records = dict()

    def __get_dns_record(self, prefix, domain):
        max_pagesize = 500
        res = self.__request(
            'GET',
            Action='DescribeDomainRecords',
            DomainName=domain,
            RRKeyWord=prefix,
            TypeKeyWord='A',
            PageSize=max_pagesize,
        )
        if res.status_code == 200:
            response = res.json()
            logging.info(response)
            total_count = response.get('TotalCount', 0)
            if total_count > max_pagesize:
                logging.warning('the total number of match record is bigger \
than max single page, may loss the real record')
            for record in response['DomainRecords']['Record']:
                if record['RR'] == prefix:
                    return record['Value'], record['RecordId']
        else:
            logging.error(res.content)
        return None

    def add_dns_record(self, subdomains):
        logging.debug('this is AliyunDNSServer get dns func')
        for prefix, domain in subdomains:
            self.records[(prefix, domain)] = self.__get_dns_record(
                prefix, domain)
        logging.debug(self.records)

    def update_address(self, ip):
        logging.debug('this is AliyunDNSServer set dns func')
        for (prefix, domain), value in self.records.items():
            if value is not None:
                old_ip, record_id = value
                if old_ip != ip:
                    self.__request('GET',
                                   Action='UpdateDomainRecord',
                                   RecordId=record_id,
                                   RR=prefix, Type='A', Value=ip)
            else:
                self.__request('GET',
                               Action='AddDomainRecord',
                               DomainName=domain,
                               RR=prefix, Type='A', Value=ip)
        return

    @staticmethod
    def __percent_encode(param_string):
        encode_string = str(param_string).encode('utf8')
        res = quote(encode_string, '')
        res = res.replace('+', '%20')
        res = res.replace('*', '%2A')
        res = res.replace('%7E', '~')
        return res

    @staticmethod
    def __signature(sign_to_string, sign_secret_key):
        h = hmac.new(sign_secret_key.encode('utf8'),
                     sign_to_string.encode('utf8'), hashlib.sha1)
        signature_string = base64.encodestring(h.digest()).strip()
        return signature_string.decode('utf8')

    def __signature_with_public_prama(self, method, params):
        '''
        reference to https://help.aliyun.com/document_detail/29747.html
        '''
        params.update({
            'Format': 'json',
            'Version': '2015-01-09',
            'SignatureMethod': 'HMAC-SHA1',
            'SignatureNonce': str(uuid.uuid4()),
            'SignatureVersion': '1.0',
            'AccessKeyId': self.ALIYUN_ACCESS_KEY_ID,
            'Timestamp': datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
        })

        sorted_params = map(lambda param: '='.join(
            map(self.__percent_encode, param)), sorted(params.items()))
        canonicalized_query_string = '&'.join(sorted_params)
        sign_to_string = method + "&%2F&" + \
            self.__percent_encode(canonicalized_query_string)

        sign_secret_key = self.ALIYUN_ACCESS_KEY_SECRET + '&'
        params['Signature'] = self.__signature(sign_to_string, sign_secret_key)
        return params


servers['aliyun'] = AliyunDNSServer
