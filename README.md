# Parlamento UY

Este proyecto extrae data de las páginas del parlamento uruguayo acerca de las asistencias y proyectos presentados por
los distintos parlamentarios.

https://parlamento.gub.uy/

## Estructura de directorios

* **scripts/web_scrapping.py:** Script python que extrae la data desde el sitio del parlamento.
* **scripts/process_data.py:**  Script que consolida ciertos archivos de datos obtenidos del scraping.
* **scripts/utils.py:** Scripts con funciones utilitarias para la extracción de datos.
* **parlamento.ipynb:** IPython notebook que muestra parte de la información extraída.

La construcción del índice que se uilitza para "evaluar" a cada parlamentario así como las dimensiones consideradas 
siguen la metodología considerada en el siguiente estudio del Instituto de Ciencia Política de la Facultad de Ciencias
Sociales en Montevideo, Uruguay

Link del estudio:
  [https://parlamentosite.wordpress.com/2019/03/04/esfuerzo-parlamentario-los-senadores/]