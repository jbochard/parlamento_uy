import glob
import pandas as pd
from pandas import DataFrame

legislaturas = {
    'Legislatura XLVIII': {'from': '15-02-2015', 'to': '14-02-2020'},
    'Legislatura XLVII': {'from': '15-02-2010', 'to': '14-02-2015'},
    'Legislatura XLVI': {'from': '15-02-2005', 'to': '14-02-2010'},
    'Legislatura XLV': {'from': '15-02-2000', 'to': '14-02-2005'},
    'Legislatura XLIV': {'from': '15-02-1995', 'to': '14-02-2000'},
    'Legislatura XLIII': {'from': '15-02-1990', 'to': '14-02-1995'},
    'Legislatura XLII': {'from': '15-02-1985', 'to': '14-02-1990'}
}


def consolidar_asistencias(legislatura):
    asistencia_legisladores_df = pd.read_csv('../data/%s/senadores.csv' % legislatura)

    asistencia_camaras_df = DataFrame()
    for file in glob.glob("../data/%s/asistencia_camara_*.csv" % legislatura):
        df = pd.read_csv(file)
        gb = df[['id_legislador', 'citado', 'asistencia', 'falta_con_aviso', 'faltas_sin_aviso', 'con_licencia', 'pasaje_presidencia']].groupby(['id_legislador']).sum()
        if asistencia_camaras_df.shape[0] > 0:
            asistencia_camaras_df = asistencia_camaras_df.append(gb)
        else:
            asistencia_camaras_df = gb
    asistencia_camaras_df.columns = ['id_legislador' if str(col) == 'id_legislador' else (str(col) + '_camara') for col in asistencia_camaras_df.columns]
    asistencia_legisladores_df = asistencia_legisladores_df.merge(asistencia_camaras_df, how='left', on='id_legislador')


    asistencia_comisiones_df = DataFrame()
    for file in glob.glob("../data/%s/asistencia_a_comisiones_*.csv" % legislatura):
        df = pd.read_csv(file)
        if asistencia_comisiones_df.shape[0] > 0:
            asistencia_comisiones_df = asistencia_comisiones_df.append(df)
        else:
            asistencia_comisiones_df = df
    asistencia_comisiones_df = asistencia_comisiones_df[['id_legislador', 'citacion', 'falta_con_aviso', 'falta_sin_aviso', 'licencia', 'otras_comisiones']].groupby(
        ['id_legislador']).sum()
    asistencia_comisiones_df.columns = ['id_legislador' if str(col) == 'id_legislador' else (str(col) + '_comision') for col in asistencia_comisiones_df.columns]
    asistencia_legisladores_df = asistencia_legisladores_df.merge(asistencia_comisiones_df, how='left', on='id_legislador')

    asistencia_legisladores_df.loc[:, 'asistencia_comision'] = asistencia_legisladores_df.apply(
        lambda x: x['citacion_comision'] - x['falta_con_aviso_comision'] - x['falta_sin_aviso_comision'] - x[
            'licencia_comision'], axis=1)
    asistencia_legisladores_df.loc[:, 'citaciones'] = asistencia_legisladores_df.apply(lambda x: x['citado_camara'] + x['citacion_comision'],
                                                             axis=1)
    asistencia_legisladores_df.loc[:, 'asistencia'] = asistencia_legisladores_df.apply(
        lambda x: x['asistencia_camara'] + x['asistencia_comision'], axis=1)

    asistencia_legisladores_df.drop(columns=[asistencia_legisladores_df.columns[0]], inplace=True)
    asistencia_legisladores_df.to_csv('../data/%s/asistencia_legisladores.csv' % legislatura)
    return asistencia_legisladores_df


def consolidar_presentacion_proyectos(legislatura):
    # Carga de proyectos presentados
    proyectos_presentados_df = None
    for file in glob.glob("../data/%s/proyectos_presentados_*.csv" % legislatura):
        df = pd.read_csv(file)
        if proyectos_presentados_df is not None:
            proyectos_presentados_df = proyectos_presentados_df.append(df)
        else:
            proyectos_presentados_df = df
    proyectos_presentados_df.loc[:, 'organismo'] = None

    # Carga de pedidos de informe
    pedidos_informe_df = DataFrame()
    for file in glob.glob("../data/%s/pedidos_de_informe_*.csv" % legislatura):
        df = pd.read_csv(file)
        if pedidos_informe_df.shape[0] > 0:
            pedidos_informe_df = pedidos_informe_df.append(df)
        else:
            pedidos_informe_df = df

    total_proyectos_df = pd.concat([proyectos_presentados_df, pedidos_informe_df], axis=0)

    proyectos_df = pd.read_csv('../data/%s/proyectos.csv' % legislatura)[['id_ficha', 'tipo', 'titulo']]
    total_proyectos_df = total_proyectos_df.merge(proyectos_df, how='left', on='id_ficha')

    senadores_df = pd.read_csv('../data/%s/senadores.csv' % legislatura)
    total_proyectos_df = total_proyectos_df.merge(senadores_df[['id_legislador', 'nombre']], how='left', on='id_legislador')

    total_proyectos_df.drop(columns=[str(col) for col in total_proyectos_df.columns if str(col).startswith('Unnamed')], inplace=True)
    total_proyectos_df.to_csv('../data/%s/proyectos_presentados.csv' % legislatura)


def consolidar_evolucion_tareas(legislatura):
    evol_df = DataFrame()
    for file in glob.glob("../data/%s/evolucion_proyecto_*.csv" % legislatura):
        df = pd.read_csv(file)
        if evol_df.shape[0] > 0:
            evol_df = evol_df.append(df)
        else:
            evol_df = df

    evol_df.drop(columns=[str(col) for col in evol_df.columns if str(col).startswith('Unnamed')], inplace=True)
    evol_df.to_csv('../data/%s/evolucion_proyectos.csv' % legislatura)


if __name__ == '__main__':
    legislatura = 'Legislatura XLVIII'

    senadores = consolidar_asistencias(legislatura)
    consolidar_presentacion_proyectos(legislatura)
    consolidar_evolucion_tareas(legislatura)
