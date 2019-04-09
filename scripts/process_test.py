from scripts.web_scraping import __import_evolucion_proyectos


def test_evolucion_proyecto(legislatura, id_proyecto):
    proyecto = {
        'id_ficha': id_proyecto
    }
    __import_evolucion_proyectos(legislatura, proyecto)


if __name__ == '__main__':
    legislatura = 'Legislatura XLVIII'
    test_evolucion_proyecto(legislatura, 134850)