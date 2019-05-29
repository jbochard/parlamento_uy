import re, os
import pandas as pd
from queue import Queue, Empty
from threading import Thread
from time import sleep

from db_scraping import DBScraping
from workers.legislaturaWork import LegislaturaWork

def worker(idx, task_queue):
    while True:
        try:
            next_task = task_queue.get(timeout=10)
            next_task.tasks = task_queue
            next_task()
        except Empty :
            break
    print("Worker %s terminado." % idx)


if __name__ == '__main__':
    dbScraping = DBScraping()

    DBScraping().create_table('legislaturas', {'pk id_legislatura': int, 'legislatura': str, 'date_from': str, 'date_to': str})
    DBScraping().insert('legislaturas', { 'id_legislatura': 6, 'legislatura': 'Legislatura XLVIII', 'date_from': '15-02-2015', 'date_to': '14-02-2020'})    
    DBScraping().insert('legislaturas', { 'id_legislatura': 5, 'legislatura': 'Legislatura XLVII', 'date_from': '15-02-2010', 'date_to': '14-02-2015'})    
    DBScraping().insert('legislaturas', { 'id_legislatura': 4, 'legislatura': 'Legislatura XLVI', 'date_from': '15-02-2005', 'date_to': '14-02-2010'})    
    DBScraping().insert('legislaturas', { 'id_legislatura': 3, 'legislatura': 'Legislatura XLV', 'date_from': '15-02-2000', 'date_to': '14-02-2005'})    
    DBScraping().insert('legislaturas', { 'id_legislatura': 2, 'legislatura': 'Legislatura XLIV', 'date_from': '15-02-1995', 'date_to': '14-02-2000'})    
    DBScraping().insert('legislaturas', { 'id_legislatura': 1, 'legislatura': 'Legislatura XLIII', 'date_from': '15-02-1990', 'date_to': '14-02-1995'})    
    DBScraping().insert('legislaturas', { 'id_legislatura': 0, 'legislatura': 'Legislatura XLII', 'date_from': '15-02-1985', 'date_to': '14-02-1990'})

    tasks = Queue()
    num_consumers = 6
    print('Creando %s consumidores' % num_consumers)
    consumers = [Thread(target=worker, args=(i, tasks,)) for i in range(num_consumers)]

    legislatura_scrap_id = 6
    legislatura = DBScraping().find('legislaturas', {'id_legislatura': legislatura_scrap_id})

    base_dir =  '%s/data' % (os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    tasks.put(LegislaturaWork(legislatura['id_legislatura'], legislatura['date_from'], legislatura['date_to'], legislatura['legislatura'], base_dir))
    
    for w in consumers:
        w.start()

    for w in consumers:
        w.join()

    legisladores_df = dbScraping.to_dataframe('legisladores')
    proyectos_df = dbScraping.to_dataframe('proyectos')
    asistencia_plenario_df = dbScraping.to_dataframe('asistencia_plenario')
    asistencia_comision_df = dbScraping.to_dataframe('asistencia_comisiones')
    actuacion_parlamentaria_df = dbScraping.to_dataframe('actuacion_parlamentaria')
    proyectos_presentados_df = dbScraping.to_dataframe('proyectos_presentados')

    asistencia_df = pd.concat([asistencia_plenario_df[['id_legislador', 'asistencias', 'citaciones', 'faltas_con_aviso', 'faltas_sin_aviso', 'licencia']], asistencia_comision_df[['id_legislador', 'asistencias', 'citaciones', 'faltas_con_aviso', 'faltas_sin_aviso', 'licencia']]])
    asistencia_df = asistencia_df.groupby('id_legislador').sum()
    asistencia_df = asistencia_df.merge(legisladores_df[['id_legislador', 'nombre', 'cuerpo', 'lema']], on='id_legislador')

    proyectos_presentados_df = proyectos_presentados_df.merge(proyectos_df, on='id_proyecto', how='left')
    proyectos_presentados_df = proyectos_presentados_df[proyectos_presentados_df['tipo'].isin(['PEDIDO DE INFORMES', 'PROYECTO DE DECLARACION', 'PROYECTO DE LEY', 'PROYECTO DE MINUTA DE COMUNICACION','PROYECTO DE RESOLUCION'])]
    proyectos_presentados_df = proyectos_presentados_df[['id_legislador', 'id_proyecto']].drop_duplicates().groupby('id_legislador').size().reset_index(name='proyectos_total')
    proyectos_presentados_df = proyectos_presentados_df.merge(legisladores_df[['id_legislador', 'nombre', 'cuerpo', 'lema']], on='id_legislador')

    informante_comision_df = actuacion_parlamentaria_df[actuacion_parlamentaria_df['tipo'].isin(['INTERVIENE', 'INFORMA', 'EXPONE'])]
    informante_comision_df = informante_comision_df.groupby('id_legislador').size().reset_index(name='informes_total')
    informante_comision_df = informante_comision_df.merge(legisladores_df[['id_legislador', 'nombre', 'cuerpo', 'lema']], on='id_legislador')

    indice_senadores_df = asistencia_df[['nombre', 'cuerpo', 'lema', 'id_legislador', 'asistencias', 'citaciones']]
    indice_senadores_df = indice_senadores_df.merge(proyectos_presentados_df[['id_legislador', 'proyectos_total']], on='id_legislador')
    indice_senadores_df = indice_senadores_df.merge(informante_comision_df[['id_legislador', 'informes_total']], on='id_legislador')

    dbScraping.from_dataframe('indice_legisladores', indice_senadores_df, {'pk id_legislador': int})

    dbScraping.export_to_csv(base_dir)
    dbScraping.db_export_to_sqlite(drop=True)
