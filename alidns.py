#! /usr/bin/env python3
import json
import uuid
import hmac
import base64
import hashlib
import requests
import urllib.request
from os.path import dirname, realpath
from os.path import join as path_join
from datetime import datetime
from collections import namedtuple

cnf_file = path_join(dirname(realpath(__file__)), 'aliyun.json')


def refresh_cnf():
    global cnf
    global cnf_file
    cnf_dict = json.load(open(cnf_file))
    cnf = namedtuple('cnf', cnf_dict.keys())(**cnf_dict)


refresh_cnf()


def percent_encode(param_string):
    encode_string = str(param_string).encode('utf8')
    res = urllib.request.quote(encode_string, '')
    res = res.replace('+', '%20')
    res = res.replace('*', '%2A')
    res = res.replace('%7E', '~')
    return res


def signature(sign_to_string, sign_secret_key):
    h = hmac.new(sign_secret_key.encode('utf8'),
                 sign_to_string.encode('utf8'), hashlib.sha1)
    signature_string = base64.encodestring(h.digest()).strip()
    return signature_string.decode('utf8')


def signature_with_public_prama(params):
    '''
    reference to https://help.aliyun.com/document_detail/29747.html
    '''
    global cnf
    params.update({
        'Format': 'json',
        'Version': '2015-01-09',
        'SignatureMethod': 'HMAC-SHA1',
        'SignatureNonce': str(uuid.uuid4()),
        'SignatureVersion': '1.0',
        'AccessKeyId': cnf.ALIYUN_ACCESS_KEY_ID,
        'Timestamp': datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
    })

    sorted_params = map(lambda param: '='.join(
        map(percent_encode, param)), sorted(params.items()))
    canonicalized_query_string = '&'.join(sorted_params)
    sign_to_string = cnf.REQUEST_METHOD + "&%2F&" + \
        percent_encode(canonicalized_query_string)

    sign_secret_key = cnf.ALIYUN_ACCESS_KEY_SECRET + '&'
    params['Signature'] = signature(sign_to_string, sign_secret_key)
    return params


def alidns_request(params=None, **param_dict):
    global cnf
    ALIDNS_SITE = 'https://alidns.aliyuncs.com'
    if params:
        params.update(param_dict)
    else:
        params = param_dict
    params = signature_with_public_prama(params)
    response = getattr(requests, cnf.REQUEST_METHOD.lower())(
        ALIDNS_SITE, params=params)
    return response


def get_dns_list(**param_dict):
    param_dict_items = set(param_dict.items())
    for domain_name, prefixs in cnf.ALIYUN_DOMAIN_NAME_DICT.items():
        for prefix in prefixs.split(','):
            prefix = prefix.strip()
            res = alidns_request(Action='DescribeDomainRecords',
                                 DomainName=domain_name, RRKeyWord=prefix)
            print(res.json())
            for record in res.json()['DomainRecords']['Record']:
                if record['RR'] == prefix and param_dict_items.issubset(record.items()):
                    yield record['DomainName'], record['Value'], record['RR'], record['RecordId']
                    break
            else:
                yield domain_name, "", prefix, None


def update_dns(domain_name, ip_address, prefix, record_id, **param_dict):
    if record_id:
        response = alidns_request(Action='UpdateDomainRecord', RecordId=record_id,
                                  RR=prefix, Type='A', Value=ip_address, **param_dict)
    else:
        response = alidns_request(Action='AddDomainRecord', DomainName=domain_name,
                                  RR=prefix, Type='A', Value=ip_address, **param_dict)
    print(response.text)
    return response


if __name__ == '__main__':
    #for (k, v) in signature_with_public_prama({'Action':'DescribeDomains'}).items(): print(k + ':'+v)
    for x in get_dns_list():
        print(x)
