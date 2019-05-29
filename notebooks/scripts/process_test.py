from queue import Queue
from db_scraping import DBScraping
import pandas as pd
import os

def test_database():
    DBScraping().create_table('legisladores', { 'pk id_legislador': int, 'cuerpo': str, 'email': str, 'lema': str, 'nombre': str})
    DBScraping().create_index('legisladores', 'idx', ['nombre', 'lema'])
    DBScraping().insert('legisladores', { 'id_legislador': 1, 'cuerpo': 'CSS', 'lema': 'FRENTE AMPLIO', 'nombre': 'Bochard, Juan'})
    print(DBScraping().exists_idx('legisladores', 'idx', {'lema': 'FRENTE AMPLIO', 'nombre': 'Bochard, Juan'}))
    DBScraping().db_export_to_sqlite(test=True)

def test_db_from_dataframe():
    base_dir =  '%s/data' % (os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    df = pd.read_csv('%s/%s' % (base_dir, 'actuacion_parlamentaria.csv'))
    DBScraping().from_dataframe('test', df, {'pk id': int})
    print()
    
if __name__ == '__main__':
    test_database()
    test_db_from_dataframe()