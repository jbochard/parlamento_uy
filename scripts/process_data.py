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
    senadores_df = pd.read_csv('../data/%s/senadores.csv' % legislatura)

    asist_df = DataFrame()
    for file in glob.glob("../data/%s/asistencia_camara*.csv" % legislatura):
        df = pd.read_csv(file)
        gb = df[['id_senador', 'citado', 'asistencia', 'falta_con_aviso', 'faltas_sin_aviso', 'con_licencia', 'pasaje_presidencia']].groupby(['id_senador']).sum()
        if asist_df.shape[0] > 0:
            asist_df = asist_df.append(gb)
        else:
            asist_df = gb
    asist_df.columns = ['id_senador' if str(col) == 'id_senador' else (str(col) + '_camara') for col in asist_df.columns]
    senadores_df = senadores_df.merge(asist_df, how='left', on='id_senador')


    asist_df = DataFrame()
    for file in glob.glob("../data/%s/asistencia_a_comisiones*.csv" % legislatura):
        df = pd.read_csv(file)
        if asist_df.shape[0] > 0:
            asist_df = asist_df.append(df)
        else:
            asist_df = df
    asist_df = asist_df[['id_senador', 'citacion', 'falta_con_aviso', 'falta_sin_aviso', 'licencia', 'otras_comisiones']].groupby(
        ['id_senador']).sum()
    asist_df.columns = ['id_senador' if str(col) == 'id_senador' else (str(col) + '_comision') for col in asist_df.columns]
    senadores_df = senadores_df.merge(asist_df, how='left', on='id_senador')
    senadores_df.drop(columns=[senadores_df.columns[0]], inplace=True)
    senadores_df.to_csv('../data/%s/senado_asistencia.csv' % legislatura)
    return senadores_df


def consolidar_trabajo(legislatura):
    trabajo_df = DataFrame()
    for file in glob.glob("../data/%s/pedidos_de_informe*.csv" % legislatura):
        df = pd.read_csv(file)
        if trabajo_df.shape[0] > 0:
            trabajo_df = trabajo_df.append(df)
        else:
            trabajo_df = df

    trabajo_df['tipo'] = 'PEDIDO DE INFORME'

    proyectos_presentados_df = DataFrame()
    for file in glob.glob("../data/%s/proyectos_presentados*.csv" % legislatura):
        df = pd.read_csv(file)
        if proyectos_presentados_df.shape[0] > 0:
            proyectos_presentados_df = proyectos_presentados_df.append(df)
        else:
            proyectos_presentados_df = df

    proyectos_df = pd.read_csv('../data/%s/proyectos.csv' % legislatura)
    proyectos_presentados_df = proyectos_presentados_df.merge(proyectos_df[['id_ficha', 'tipo', 'titulo']], how='left', on='id_ficha')
    proyectos_presentados_df['organismo'] = 'CSS'

    trabajo_df = trabajo_df.append(proyectos_presentados_df[['Unnamed: 0', 'id_senador', 'titulo', 'fecha_entrada', 'id_ficha', 'organismo', 'tipo']])

    senadores_df = pd.read_csv('../data/%s/senadores.csv' % legislatura)
    trabajo_df = trabajo_df.merge(senadores_df[['id_senador', 'nombre']], how='left', on='id_senador')

    trabajo_df.drop(columns=[str(col) for col in trabajo_df.columns if str(col).startswith('Unnamed')], inplace=True)
    trabajo_df.to_csv('../data/%s/senado_trabajo.csv' % legislatura)


def consolidar_evolucion_tareas(legislatura):
    proyectos_df = pd.read_csv('../data/%s/proyectos.csv' % legislatura)

    evol_df = DataFrame()
    for file in glob.glob("../data/%s/evolucion_proyecto*.csv" % legislatura):
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
    consolidar_trabajo(legislatura)
    consolidar_evolucion_tareas(legislatura)
