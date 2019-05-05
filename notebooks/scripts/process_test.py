from queue import Queue

from workers.legisladorActuacionParlamentariaWork import LegisladorActuacionParlamentariaWorker
from workers.legisladorAsistenciaComisionesWork import LegisladorAsistenciaComisionesWorker
from workers.senadoresAsistenciaPlenarioWork import SenadoresAsistenciaPlenarioWorker
from workers.proyectoWork import ProyectoWorker

legislatura = 'Legislatura XLVIII'
date_from = '15-02-2015'
date_to = '14-02-2020'


def test_senadores_AsistenciaComisiones(id_legislador, id_comision):
    LegisladorAsistenciaComisionesWorker(legislatura, date_from, date_to, id_legislador, id_comision).execute()


def test_senadores_AsistenciaPlenario(id_legislador):
    SenadoresAsistenciaPlenarioWorker(legislatura, date_from, date_to, id_legislador).execute()


def test_senadores_ActuacionParlamentaria(id_legislador, pag):
    tmp = LegisladorActuacionParlamentariaWorker(legislatura, date_from, date_to, id_legislador, pag)
    tmp.tasks = Queue()
    tmp.execute()
    print(tmp.tasks)


def test_senadores_proyectos(id_proyecto):
    tmp = ProyectoWorker(legislatura, date_from, date_to, id_proyecto)
    tmp.tasks = Queue()
    tmp.execute()
    print(tmp.tasks)


if __name__ == '__main__':
    test_senadores_ActuacionParlamentaria(5131, 0)
