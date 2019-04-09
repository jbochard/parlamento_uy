# Parlamento UY

Este proyecto extrae data de las páginas del parlamento uruguayo acerca de las asistencias y proyectos presentados por
los distintos parlamentarios.

https://parlamento.gub.uy/

## Estructura de directorios

* **scripts/web_scrapping.py:** Script python que extrae la data desde el sitio del parlamento.
* **scripts/process_data.py:**  Script que consolida ciertos archivos de datos obtenidos del scraping.
* **scripts/utils.py:** Scripts con funciones utilitarias para la extracción de datos.
* **parlamento.ipynb:** IPython notebook que muestra parte de la información extraída.

## Estructura de datos

Los datos extraídos se encuentran en la carpeta **data** organizados en subdirectorios por legislatura. 
Los archivos que se encuentran son:

* **asistencia_a_comisiones_\*:** Lista la asistencia de un legislador a una comisión determinada.<br>
  Ej: https://parlamento.gub.uy/camarasycomisiones/legisladores/5165/asistencia-a-comisiones/73
* **asistencia_camara_\*:** Lista la asistencia de un legislador a cada cámara.<br>
  Ej: https://parlamento.gub.uy/camarasycomisiones/legisladores/5165/asistenciaplenario/senadores
* **evolucion_proyecto_\*:** Evolución en parlamento de cada proyecto.<br>
  Ej: https://parlamento.gub.uy/documentosyleyes/ficha-asunto/927/tramite
* **pedidos_de_informe_camy_antognazza_\*:** Lista los pedidos de informe realizados por cada legislador.<br>
  Ej: https://parlamento.gub.uy/camarasycomisiones/legisladores/5165/pedidosInf-legislador
* **proyectos_presentados\*:** Lista de proyectos presentados por cada legislador.<br>
  Ej: https://parlamento.gub.uy/camarasycomisiones/legisladores/5165/iniciativas-legislador
* **senadores:** Lista los senadores (sería más bien personas que participaron de cámara de senadores, incluye suplentes)<br>
  Ej: https://parlamento.gub.uy/camarasycomisiones/senadores/plenario/asistencia-a-sesiones
* **comisiones:** Lista las distintas comisiones existenes.<br>
  Ej: https://parlamento.gub.uy/camarasycomisiones/legisladores/5165/asistencia-a-comisiones
