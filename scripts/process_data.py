import glob
import pandas as pd
from pandas import DataFrame


def consolidar_asistencias():
    senadores_df = pd.read_csv('../data/senadores.csv')

    asist_df = DataFrame()
    for file in glob.glob("../data/asistencia_camara*.csv"):
        df = pd.read_csv(file)
        gb = df[['id_senador', 'citado', 'asistencia', 'falta_con_aviso', 'faltas_sin_aviso', 'con_licencia', 'pasaje_presidencia']].groupby(['id_senador']).sum()
        if asist_df.shape[0] > 0:
            asist_df = asist_df.append(gb)
        else:
            asist_df = gb
    asist_df.columns = ['id_senador' if str(col) == 'id_senador' else (str(col) + '_camara') for col in asist_df.columns]
    senadores_df = senadores_df.merge(asist_df, how='left', on='id_senador')


    asist_df = DataFrame()
    for file in glob.glob("../data/asistencia_a_comisiones*.csv"):
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
    senadores_df.to_csv('../data/senado_asistencia.csv')
    return senadores_df


def consolidar_trabajo():
    trabajo_df = DataFrame()
    for file in glob.glob("../data/pedidos_de_informe*.csv"):
        df = pd.read_csv(file)
        if trabajo_df.shape[0] > 0:
            trabajo_df = trabajo_df.append(df)
        else:
            trabajo_df = df

    trabajo_df['tipo'] = 'PEDIDO DE INFORME'
    trabajo_df['estado'] = 'REALIZADO'

    proyectos_presentados_df = DataFrame()
    for file in glob.glob("../data/proyectos_presentados*.csv"):
        df = pd.read_csv(file)
        if proyectos_presentados_df.shape[0] > 0:
            proyectos_presentados_df = proyectos_presentados_df.append(df)
        else:
            proyectos_presentados_df = df

    proyectos_df = pd.read_csv('../data/proyectos.csv')
    proyectos_presentados_df = proyectos_presentados_df.merge(proyectos_df[['id_ficha', 'tipo', 'titulo', 'estado']], how='left', on='id_ficha')
    proyectos_presentados_df['organismo'] = 'CSS'

    trabajo_df = trabajo_df.append(proyectos_presentados_df[['Unnamed: 0', 'id_senador', 'titulo', 'fecha_entrada', 'id_ficha', 'organismo', 'tipo', 'estado']])

    senadores_df = pd.read_csv('../data/senadores.csv')
    trabajo_df = trabajo_df.merge(senadores_df[['id_senador', 'nombre']], how='left', on='id_senador')

    trabajo_df.drop(columns=[str(col) for col in trabajo_df.columns if str(col).startswith('Unnamed')], inplace=True)
    trabajo_df.to_csv('../data/senado_trabajo.csv')


if __name__ == '__main__':
    senadores = consolidar_asistencias()
    consolidar_trabajo()

