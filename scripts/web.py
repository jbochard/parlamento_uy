import multiprocessing as mp
import sys

from bs4 import BeautifulSoup
from pandas import DataFrame

from scripts.utils import normalize_html_name, extract_id, extract_html_date, normalize_name_to_file, import_pool, \
    calculate_project_state, extract_html_str, extract_html_int, get_html, calculate_project_general__state, find, \
    find_class

legislaturas = {
    'Legislatura XLVIII': {'from': '15-02-2015', 'to': '14-02-2020'},
    'Legislatura XLVII': {'from': '15-02-2010', 'to': '14-02-2015'},
    'Legislatura XLVI': {'from': '15-02-2005', 'to': '14-02-2010'},
    'Legislatura XLV': {'from': '15-02-2000', 'to': '14-02-2005'},
    'Legislatura XLIV': {'from': '15-02-1995', 'to': '14-02-2000'},
    'Legislatura XLIII': {'from': '15-02-1990', 'to': '14-02-1995'},
    'Legislatura XLII': {'from': '15-02-1985', 'to': '14-02-1990'}
}


def __import_perfil(legislatura, senador):
    print('\tImportando perfil de %s' % senador['nombre'])

    file = get_html('https://parlamento.gub.uy/camarasycomisiones/legisladores/%s' % senador['id_senador'])
    h = BeautifulSoup(file.text, 'html.parser')
    email = ''
    if find_class(h, 'div', 'field-name-field-persona-mail'):
        email = extract_html_str(find_class(h, 'div', 'field-name-field-persona-mail').find('a'))
    senador['email'] = email

    # Legislaturas en las que actuó
    leg_list_html = find_class(h, 'div', 'view-legislaturas-actuo')
    if leg_list_html:
        for leg_html in leg_list_html.find_all('span', class_='field-content'):
            if legislatura in extract_html_str(leg_html):
                return senador
    print('Senador %s(%s) no actuó en la legislatura seleccionada.' % (senador['nombre', 'id_senador']))
    return {}


def __import_senadores_asistencias_camara(legislatura, senador):
    asistencia_columns = ['id_senador', 'fecha', 'citado', 'asistencia', 'falta_con_aviso', 'faltas_sin_aviso',
                          'con_licencia', 'pasaje_presidencia']

    print('\tImportando asistencias a camara de %s' % senador['nombre'])
    date_from = legislaturas[legislatura]['from']
    date_to = legislaturas[legislatura]['to']

    file = get_html('https://parlamento.gub.uy/camarasycomisiones/legisladores/%s/asistenciaplenario/senadores?Fecha[min][date]=%s&Fecha[max][date]=%s' % (senador['id_senador'], date_from, date_to))
    h = BeautifulSoup(file.text, 'html.parser')
    tabla_asistencias = find_class(h, 'table', 'tablaAsunto')
    del h
    data = list()
    if tabla_asistencias:
        for html_row in tabla_asistencias.find_all('tr'):
            if html_row.next.name == 'td':
                row = list()
                row.append(senador['id_senador'])
                for html_col in html_row.children:
                    if html_col.name == 'td':
                        if 'class' in html_col.attrs and 'mifecha' in html_col.attrs['class']:
                            row.append(extract_html_date(html_col))
                        else:
                            row.append(extract_html_str(html_col))
                data.append(row)
        DataFrame(data=data, columns=asistencia_columns).to_csv('../data/asistencia_camara_%s.csv' % normalize_name_to_file(senador['nombre']))
    else:
        print('\tNo hay tabla de asistencias para %s(%s)' % (senador['nombre'], senador['id_senador']))
    return {'nombre': senador['nombre'], 'status': 'OK'}


def __import_proyectos_presentados(legislatura, senador):
    proyectos_presentados_columns = ['id_senador', 'id_ficha', 'fecha_entrada']
    print('\tImportando proyectos presentados por %s' % senador['nombre'])

    date_from = legislaturas[legislatura]['from']
    date_to = legislaturas[legislatura]['to']

    file = get_html('https://parlamento.gub.uy/camarasycomisiones/legisladores/%s/iniciativas-legislador?Fecha[min][date]=%s&Fecha[max][date]=%s' % (senador['id_senador'], date_from, date_to))
    h = BeautifulSoup(file.text, 'html.parser')
    tabla = find(h, 'tbody')
    del h
    del file
    proyectos_presentados_data = list()
    proyectos = list()
    if tabla:
        for html_row in tabla.find_all('tr'):
            proyecto_presentado_data = list()
            proyecto_presentado_data.append(senador['id_senador'])
            proyecto_presentado_data.append(extract_id(find(html_row, 'a').get('href')))
            proyecto_presentado_data.append(extract_html_date(find_class(html_row, 'td', 'views-field-Ast-FechaDeEntradaAlCuerpo')))
            proyectos_presentados_data.append(proyecto_presentado_data)

            proyectos.append({'id_ficha': extract_id(html_row.find('a').get('href')), 'fecha_entrada': extract_html_date(find_class(html_row, 'td', 'views-field-Ast-FechaDeEntradaAlCuerpo'))})

        DataFrame(data=proyectos_presentados_data, columns=proyectos_presentados_columns).to_csv('../data/proyectos_presentados_%s.csv' % normalize_name_to_file(senador['nombre']))
    return proyectos


def __import_pedidos_de_informe(legislatura, senador):
    pedidos_de_informe_columns = ['id_senador', 'titulo', 'fecha_entrada', 'id_ficha', 'organismo']
    print('\tImportando pedidos de informe de %s' % senador['nombre'])

    date_from = legislaturas[legislatura]['from']
    date_to = legislaturas[legislatura]['to']

    file = get_html('https://parlamento.gub.uy/camarasycomisiones/legisladores/%s/pedidosInf-legislador?Fecha[min][date]=%s&Fecha[max][date]=%s' % (senador['id_senador'], date_from, date_to))
    h = BeautifulSoup(file.text, 'html.parser')
    tabla = find(h, 'tbody')
    del h
    del file
    peidods_de_informe_data = list()
    if tabla:
        for html_row in tabla.find_all('tr'):
            organismos_html = html_row.find_all('li')
            for organismo_html in organismos_html:
                pedido_de_informe = list()
                pedido_de_informe.append(senador['id_senador'])
                pedido_de_informe.append(extract_html_str(find_class(html_row, 'td', 'views-field-Ast-Titulo')))
                pedido_de_informe.append(extract_html_date(find_class(html_row, 'td', 'views-field-Ast-FechaDeEntradaAlCuerpo')))
                pedido_de_informe.append(extract_id(find(html_row, 'a').get('href')))
                pedido_de_informe.append(extract_html_str(organismo_html))

                peidods_de_informe_data.append(pedido_de_informe)

        DataFrame(data=peidods_de_informe_data, columns=pedidos_de_informe_columns).to_csv('../data/pedidos_de_informe_%s.csv' % normalize_name_to_file(senador['nombre']))
    return {'id_senador': senador['id_senador'], 'status': 'OK'}


def __import_evolucion_proyectos(proyecto):
    try:
        proyecto_evoluciones_columns = ['id_ficha', 'fecha', 'cuerpo', 'tramite', 'estado']

        print('\tImportando evolución de proyecto %s' % proyecto['id_ficha'])

        file = get_html('https://parlamento.gub.uy/documentosyleyes/ficha-asunto/%s' % proyecto['id_ficha'])
        h = BeautifulSoup(file.text, 'html.parser')

        proyecto['titulo'] = find_class(h, 'div', 'views-field-Ast-Titulo').contents[2].strip()
        proyecto['tipo'] = extract_html_str(find_class(h, 'div', 'tipo-acto'))
        proyecto['estado'] = 'EN_TRAMITE'

        evolucion_proyectos = list()
        tabla_sansiones = find_class(h, 'div', 'views-field-Sanciones')
        if tabla_sansiones:
            for san_html in find(tabla_sansiones, 'tbody').find_all('tr'):

                proyecto_evolucion = list()
                proyecto_evolucion.append(proyecto['id_ficha'])
                proyecto_evolucion.append(extract_html_date(san_html.contents[0]))
                proyecto_evolucion.append(extract_html_str(san_html.contents[1]))
                proyecto_evolucion.append(extract_html_str(san_html.contents[3]))
                proyecto_evolucion.append(calculate_project_state('CSS', extract_html_str(san_html.contents[3])))
                proyecto['estado'] = calculate_project_general__state(extract_html_str(san_html.contents[3]))

                evolucion_proyectos.append(proyecto_evolucion)
            DataFrame(data=evolucion_proyectos, columns=proyecto_evoluciones_columns).to_csv('../data/evolucion_proyecto_%s.csv' % proyecto['id_ficha'])
    except AttributeError as e:
        print('Error: %s - %s' % (proyecto['id_ficha'], e))
        raise e

    return proyecto


def __import_asistencia_comisiones(legislatura, senador):
    comisiones_columns = ['id_comision', 'nombre']
    asistencia_comisiones_columns = ['id_comision', 'id_senador', 'fecha_reunion', 'citacion', 'falta_con_aviso', 'falta_sin_aviso', 'licencia', 'otras_comisiones']

    print('\tImportando asistencia a comisiones de %s' % senador['nombre'])
    file = None
    try:
        date_from = legislaturas[legislatura]['from']
        date_to = legislaturas[legislatura]['to']

        file = get_html('https://parlamento.gub.uy/camarasycomisiones/legisladores/%s/asistencia-a-comisiones?Fecha[min][date]=%s&Fecha[max][date]=%s' % (senador['id_senador'], date_from, date_to))
        h = BeautifulSoup(file.text, 'html.parser')
        tabla = find(find_class(h, 'div', 'attachment'), 'tbody')
        comisiones = list()
        if tabla:
            for row_html in tabla.find_all('tr'):
                link = find(row_html, 'a')
                id_comision = extract_id(link.get('href'))
                nombre_comision = extract_html_str(row_html)
                comision = list()
                comision.append(id_comision)
                comision.append(nombre_comision)
                comisiones.append(comision)

                asist_file = get_html('https://parlamento.gub.uy/camarasycomisiones/legisladores/%s/asistencia-a-comisiones/%s?Fecha[min][date]=%s&Fecha[max][date]=%s' % (senador['id_senador'], id_comision, date_from, date_to))
                h = BeautifulSoup(asist_file.text, 'html.parser')
                asist_tablas = h.find_all('table')
                if asist_tablas and len(asist_tablas) > 0:
                    tabla_asistencias_html = list(filter(lambda t : find(t, 'th') and find(t, 'th').text == 'Fecha De Reunión', asist_tablas))
                    tabla_asistencia_html = tabla_asistencias_html[0]
                    asistencia_a_comisiones = list()
                    for row_asist in find(tabla_asistencia_html, 'tbody').find_all('tr'):
                        asistencia_comision = list()
                        asistencia_comision.append(id_comision)
                        asistencia_comision.append(senador['id_senador'])
                        asistencia_comision.append(extract_html_date(row_asist.contents[0]))
                        asistencia_comision.append(extract_html_int(row_asist.contents[1]))
                        asistencia_comision.append(extract_html_int(row_asist.contents[3]))
                        asistencia_comision.append(extract_html_int(row_asist.contents[4]))
                        asistencia_comision.append(extract_html_int(row_asist.contents[5]))
                        asistencia_comision.append(extract_html_int(row_asist.contents[6]))
                        asistencia_a_comisiones.append(asistencia_comision)
                    DataFrame(data=asistencia_a_comisiones, columns=asistencia_comisiones_columns).to_csv('../data/asistencia_a_comisiones_%s_%s.csv' % (id_comision, senador['id_senador']))
                else:
                    print('\t\tTabla de asistencia a comisiones no existe para comision %s, %s(%s)' % (id_comision, senador['nombre'], senador['id_senador']))
                    print('Url: https://parlamento.gub.uy/camarasycomisiones/legisladores/%s/asistencia-a-comisiones/%s?Fecha[min][date]=%s&Fecha[max][date]=%s' % (senador['id_senador'], id_comision, date_from, date_to))
                    print(asist_file.text)
                    print()
            DataFrame(data=comisiones, columns=comisiones_columns).to_csv('../data/comisiones.csv')
        else:
            print('\t\tTabla no existe para %s(%s)' % (senador['nombre'], senador['id_senador']))
    except AttributeError as e:
        print('Error: %s - %s' % (senador['id_senador'], e))
        print(file.text)
        raise e
    return {'id_senador': senador['id_senador'], 'status': 'OK'}


def import_senadores_desde_asistencias(legislatura):
    print('Importando senadores desde asistencias...')

    date_from = legislaturas[legislatura]['from']
    date_to = legislaturas[legislatura]['to']

    file = get_html('https://parlamento.gub.uy/camarasycomisiones/senadores/plenario/asistencia-a-sesiones?Fecha[min][date]=%s&Fecha[max][date]=%s' % (date_from, date_to))
    h = BeautifulSoup(file.text, 'html.parser')
    senadores = list()
    for td_html in h.find_all('td', class_='views-field-Psn-NombresDeFirma'):
        link_html = find(td_html, 'a')
        if link_html:
            id = extract_id(link_html.get('href'))
            nombre = normalize_html_name(link_html)
            senadores.append({'id_senador': id, 'nombre': nombre})
    return senadores


def salvar_senadores(senadores):
    print('Guardanto datos de senadores.')
    senadores_columns = ['id_senador', 'nombre', 'email']

    senadores_data = list()
    senadores_filtrado = list()
    for senador in senadores:
        if len(senador) > 0:
            senador_data = list()
            senador_data.append(senador['id_senador'])
            senador_data.append(senador['nombre'])
            senador_data.append(senador['email'])
            senadores_data.append(senador_data)
            senadores_filtrado.append(senador)
    DataFrame(data=senadores_data, columns=senadores_columns).to_csv('../data/senadores.csv')
    return senadores_filtrado


def salvar_proyectos(proyectos):
    print('Guardanto datos de proyectos.')
    proyectos_columns = ['id_ficha', 'fecha_entrada', 'tipo', 'titulo', 'estado']

    proyectos_data = list()
    for proyecto in proyectos:
        proyecto_data = list()
        proyecto_data.append(proyecto['id_ficha'])
        proyecto_data.append(proyecto['fecha_entrada'])
        proyecto_data.append(proyecto['tipo'])
        proyecto_data.append(proyecto['titulo'])
        proyecto_data.append(proyecto['estado'])
        proyectos_data.append(proyecto_data)
    DataFrame(data=proyectos_data, columns=proyectos_columns).to_csv('../data/proyectos.csv')


if __name__ == '__main__':
    num_proc = 4
    if len(sys.argv) > 1:
        try:
            num_proc = int(sys.argv[1])
        except:
            pass
    pool = mp.Pool(processes=num_proc)
    legislatura = 'Legislatura XLVIII'

    senadores = import_senadores_desde_asistencias(legislatura)
    senadores = import_pool(pool, senadores, __import_perfil, args=(legislatura,))
    senadores = salvar_senadores(senadores)

    import_pool(pool, senadores, __import_senadores_asistencias_camara, args=(legislatura,))
    import_pool(pool, senadores, __import_pedidos_de_informe, args=(legislatura,))
    import_pool(pool, senadores, __import_asistencia_comisiones, args=(legislatura,))

    proyectos = import_pool(pool, senadores, __import_proyectos_presentados, args=(legislatura,))
    proyectos = import_pool(pool, proyectos, __import_evolucion_proyectos)
    salvar_proyectos(proyectos)

    pool.close()
    pool.join()
