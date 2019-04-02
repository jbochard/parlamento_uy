import re
import time
import datetime
import unidecode
import collections
from requests import get

re_coma = re.compile('\s*,\s*')
re_id_legislador = re.compile('.*/(\d+)')
re_estado_aprueba = re.compile('.*(sanciona|concedida|aprueba).*', re.RegexFlag.IGNORECASE)
re_estado_promulga = re.compile('.*promulga.*', re.RegexFlag.IGNORECASE)
RETRY = 10


def find(html, tag, debug=False):
    f = html.find(tag)
    if f:
        return f
    else:
        if debug:
            print('------------------------------ Sub HTML -----------------------------------------')
            print(html)
            print('---------------------------------------------------------------------------------')
    return None


def find_class(html, tag, class_, debug=False):
    f = html.find(tag, class_)
    if f:
        return f
    else:
        if debug:
            print('------------------------------ Sub HTML -----------------------------------------')
            print(html)
            print('---------------------------------------------------------------------------------')
    return None


def get_html(url):
    retry = RETRY
    while True:
        try:
            response = get(url)
            if response.status_code == 200:
                return response
            else:
                print("Retry: %s..." % url)
                retry = retry - 1
        except Exception as e:
            print("Retry by error: %s..." % e)
            retry = retry - 1
        if retry == 0:
            break
        else:
            time.sleep((RETRY-retry) / 5)
    raise Exception('No se pudo cargar url: %s' % url)


def normalize_html_name(name):
    if name:
        return re_coma.sub(name.text.strip(), ', ')
    return ''


def normalize_name_to_file(name):
    return unidecode.unidecode(name).lower().replace(',', '').replace(" ", "_")


def extract_id(url):
    if re_id_legislador.match(url.strip()):
        return int(re_id_legislador.match(url.strip()).group(1))
    else:
        return 0


def extract_html_str(txt):
    if txt:
        return txt.text.strip()
    return ''


def extract_html_int(txt):
    if txt:
        return int(txt.text.strip())
    return 0


def extract_html_date(date):
    if date:
        return datetime.datetime.strptime(date.text.strip(), '%d-%m-%Y')
    return ''


def import_pool(pool, list, func, args=()):
    r = [pool.apply_async(func, args=(*args, x)) for x in list]
    lst = [p.get() for p in r]
    if isinstance(lst, collections.Sequence) and len(lst) > 0 and isinstance(lst[0], collections.Sequence):
        return [y for x in lst for y in x]
    else:
        return lst


def calculate_project_state(cuerpo, texto):
    if re_estado_aprueba.match(texto):
        return 'APRUEBA_%s' % cuerpo
    if re_estado_promulga.match(texto):
        return 'PROMULGA'
    return 'EN_TRAMITE'


def calculate_project_general__state(texto):
    if re_estado_aprueba.match(texto):
        return 'APRUEBA'
    if re_estado_promulga.match(texto):
        return 'PROMULGA'
    return 'EN_TRAMITE'
