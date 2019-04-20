import os
import re
import time
import datetime
import hashlib
import requests
import unidecode
import collections
from requests import get

from scripts.exceptions import WebConnectionError

re_coma = re.compile('\s*,\s*')
re_id_legislador = re.compile('.*/(\d+)\??.*')
re_estado_aprueba = re.compile('.*(sanciona|concedida|aprueba).*', re.RegexFlag.IGNORECASE)
re_estado_promulga = re.compile('.*promulga.*', re.RegexFlag.IGNORECASE)
RETRY = 10


def find(html, tag, debug=False):
    if html:
        f = html.find(tag)
        if f:
            return f
        else:
            if debug:
                print('------------------------------ Sub HTML -----------------------------------------')
                print(html)
                print('---------------------------------------------------------------------------------')
    return None


def find_all(html, tag, debug=False):
    if html:
        f = html.find_all(tag)
        if f:
            return f
        else:
            if debug:
                print('------------------------------ Sub HTML -----------------------------------------')
                print(html)
                print('---------------------------------------------------------------------------------')
    return list()


def find_class(html, tag, class_, debug=False):
    if html:
        f = html.find(tag, class_)
        if f:
            return f
        else:
            if debug:
                print('------------------------------ Sub HTML -----------------------------------------')
                print(html)
                print('---------------------------------------------------------------------------------')
    return None


def find_all_class(html, tag, class_, debug=False):
    if html:
        f = html.find_all(tag, class_)
        if f:
            return f
        else:
            if debug:
                print('------------------------------ Sub HTML -----------------------------------------')
                print(html)
                print('---------------------------------------------------------------------------------')
    return list()


def find_link_in(html, txt_, debug=False):
    if html:
        links = html.find_all('a')
        if links:
            for link in links:
                if txt_ in link.get('href'):
                    return link
        else:
            if debug:
                print('------------------------------ Sub HTML -----------------------------------------')
                print(html)
                print('---------------------------------------------------------------------------------')
    return None


def get_html(url):
    requests.packages.urllib3.disable_warnings()
    retry = RETRY
    while True:
        try:
            digester = hashlib.md5()
            digester.update(url.encode('utf-8'))
            key = digester.hexdigest()
            if os.path.isfile('../cache/cache_%s.txt' % key):
                f = open('../cache/cache_%s.txt' % key, 'r')
                response = f.read()
                f.close()
                return response
            else:
                response = get(url, verify=False)
                if response.status_code == 200:
                    f = open('../cache/cache_%s.txt' % key, 'w')
                    f.write(response.text)
                    f.close()
                    return response.text
                else:
                    print("Retry: %s..." % url)
                    retry = retry - 1
        except Exception as e:
            raise WebConnectionError()


def normalize_html_name(name):
    if name:
        return re_coma.sub(name.text.strip(), ', ')
    return ''


def normalize_name_to_file(name):
    return unidecode.unidecode(name).lower().replace(',', '').replace(" ", "_")


def extract_id(link_html):
    if link_html is not None and link_html.get('href') is not None:
        if re_id_legislador.match(link_html.get('href').strip()):
            return int(re_id_legislador.match(link_html.get('href').strip()).group(1))
    return None


def extract_html_str(txt):
    if txt:
        return txt.text.strip()
    return None


def extract_html_int(txt):
    if txt:
        return int(txt.text.strip())
    return 0


def extract_html_date(date):
    if date:
        return datetime.datetime.strptime(date.text.strip(), '%d-%m-%Y')
    return ''


def import_pool_to_lst(pool, list, func, args=()):
    r = [pool.apply_async(func, args=(*args, x)) for x in list]
    lst = [p.get() for p in r]
    if isinstance(lst, collections.Sequence) and len(lst) > 0 and isinstance(lst[0], collections.Sequence):
        return [y for x in lst for y in x]
    else:
        return lst


def import_pool_to_dict(pool, list, func, args=()):
    r = [pool.apply_async(func, args=(*args, x)) for x in list]
    lst = [p.get() for p in r]
    dict_result = {}
    for d in lst:
        dict_result = {**d, **dict_result}
    return dict_result


def legisladores_dict(senadores):
    d = dict()
    for senador in senadores:
        d[senador['nombre']] = senador['id_senador']
    return d
