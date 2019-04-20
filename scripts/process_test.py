from queue import Queue

from scripts.workers.senadoresActuacionParlamentariaWork import SenadoresActuacionParlamentariaWorker
from scripts.workers.senadoresAsistenciaComisionesWork import SenadoresAsistenciaComisionesWorker
from scripts.workers.senadoresAsistenciaPlenarioWork import SenadoresAsistenciaPlenarioWorker
from scripts.workers.senadoresProyectoWork import SenadoresProyectoWorker

legislatura = 'Legislatura XLVIII'
date_from = '15-02-2015'
date_to = '14-02-2020'


def test_senadores_AsistenciaComisiones(id_senador, id_comision):
    SenadoresAsistenciaComisionesWorker(legislatura, date_from, date_to, id_senador, id_comision).execute()


def test_senadores_AsistenciaPlenario(id_senador):
    SenadoresAsistenciaPlenarioWorker(legislatura, date_from, date_to, id_senador).execute()


def test_senadores_ActuacionParlamentaria(id_senador, pag):
    tmp = SenadoresActuacionParlamentariaWorker(legislatura, date_from, date_to, id_senador, pag)
    tmp.tasks = Queue()
    tmp.execute()
    print(tmp.tasks)


def test_senadores_proyectos(id_proyecto):
    tmp = SenadoresProyectoWorker(legislatura, date_from, date_to, id_proyecto)
    tmp.tasks = Queue()
    tmp.execute()
    print(tmp.tasks)


if __name__ == '__main__':
    test_senadores_proyectos(125032)
