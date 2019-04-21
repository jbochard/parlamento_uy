# Parlamento UY

Este proyecto extrae data de las páginas del parlamento uruguayo acerca de las asistencias y proyectos presentados por
los distintos parlamentarios.

https://parlamento.gub.uy/

_Nota:_ La construcción del índice que se uilitza para "evaluar" a cada parlamentario así como las dimensiones consideradas 
siguen la metodología considerada en el siguiente estudio del Instituto de Ciencia Política de la Facultad de Ciencias
Sociales en Montevideo, Uruguay

Link del estudio:
  [https://parlamentosite.wordpress.com/2019/03/04/esfuerzo-parlamentario-los-senadores/]
  
## Estructura de directorios

* **scripts/web_scrapping.py:** Script python que extrae la data desde el sitio del parlamento.
* **scripts/utils.py:** Scripts con funciones utilitarias para la extracción de datos.
* **scripts/db_scraping.py:** Script que permite almacenar la info recolectada.
* **parlamento.ipynb:** IPython notebook que muestra parte de la información extraída.

## Archivos almacenados

#### actuacion_parlamentaria  

Recoge la información de la actuación parlamentaria de cada legislador.<br>

##### Columnas

* id_legislador: Id del legislador en cuestión.
* fecha: Fecha en la que se realizó la actuación.
* tipo: Catálogo de ciertas actuaciones de interés como ser, intervenciones, discursos, etc
* detalle: Texto que describe la actuación realizada por el legislador.

##### Extracción: 
https://parlamento.gub.uy/camarasycomisiones/legisladores/5246/actuacion-legislador


#### asistencia_comisiones  

Recoge la información de la asistencia de cada legislador a las distintas comisiones de las que participa.<br>

##### Columnas

* id_legislador: Id del legislador
* id_comision: Id de la comisión
* fecha: Fecha en la que asistió o se requirió su asistencia
* citaciones: 1 si el legislador fue citado para participar de la comisión, 0 si no.
* asistencias: 1 si el legislador asistió a dicha comisión 0 si no lo hizo
* faltas_con_aviso: 1 si el legislador faltó con aviso a la convocatoria, 0 si no lo hizo
* faltas_sin_aviso: 1 si el legislador faltó sin aviso a la convocatoria, 0 si no lo hizo
* licancia: 1 si el legislador se encontraba de licencia al momento de la convocatoria, 0 si no lo estaba
* otras_comisiones: 1 si el legislador se encontraba en otra comisión al momento de la convocatoria, 0 si no 

##### Extracción: 
https://parlamento.gub.uy/camarasycomisiones/legisladores/5246/asistencia-a-comisiones/331

#### asistencia_plenario  

Recoge la información de la asistencia de cada legislador al plenario.<br>

##### Columnas

* id_legislador: Id del legislador
* fecha: Fecha en la que asistió o se requirió su asistencia
* citaciones: 1 si el legislador fue citado, 0 si no.
* asistencias: 1 si el legislador asistió al plenario, 0 si no lo hizo
* faltas_con_aviso: 1 si el legislador faltó con aviso a la convocatoria, 0 si no lo hizo
* faltas_sin_aviso: 1 si el legislador faltó sin aviso a la convocatoria, 0 si no lo hizo
* licancia: 1 si el legislador se encontraba de licencia al momento de la convocatoria, 0 si no lo estaba
* pasaje_presidencia: 1 si el legislador se encontraba en presidencia al momento de la convocatoria, 0 si no 

##### Extracción: 
https://parlamento.gub.uy/camarasycomisiones/legisladores/5246/asistenciaplenario/senadores


#### comisiones  

Recoge info de las distintas comisiones parlamentarias.<br>

##### Columnas

* id_comision: Id de la comisión
* nombre: Nombre de la comisión

##### Extracción: 
Surge de la recopilación de la asistencia a las distintas comisiones de los legisladores.


#### pedidos_informe  

Recoge la información de los pedidos de informe realizados por los legisladores.

##### Columnas

* id_proyecto: Id de la ficha del pedido de informe realizado
* id_legislador: Id del legislador que realiza el pedido de informe 
* fecha: Fecha en la que se realiza el pedido de informe
* organismo: Organismo al que se le solicita la información

##### Extracción: 
https://parlamento.gub.uy/camarasycomisiones/legisladores/5246/pedidosInf-legislador

#### proyectos_presentados  

Recoge la información de los proyectos de ley, declaraciones, etc realizados por los legisladores.

##### Columnas

* id_proyecto: Id de la ficha del proyecto presentado
* id_legislador: Id del legislador que presenta el proyecto
* fecha: Fecha en la que se presenta el proyecto

##### Extracción: 
https://parlamento.gub.uy/camarasycomisiones/legisladores/5246/iniciativas-legislador


#### legisladores  

Recoge info de los legisladores<br>

##### Columnas

* id_legislador: Id del legislador
* email: Mail de contacto del legislador
* lema: Lema al que pertenece
* nombre: Nombre y apellido del legislador

##### Extracción: 
https://parlamento.gub.uy/camarasycomisiones/legisladores/5246

#### proyectos  

Recoge info los proyectos (léase pedidos de informe, proyectos de ley, declaraciones, etc) presentados en el parlamento.<br>

##### Columnas

* id_proyecto: Id de la ficha del proyecto presentado
* tipo: Tipo de proyecto:
DECLARACION, LEY, MINUTA DE COMUNICACION, PEDIDO DE INFORMES, PROYECTO DE DECLARACION, PROYECTO DE LEY, PROYECTO DE MINUTA DE COMUNICACION, PROYECTO DE RESOLUCION, RESOLUCION
* titulo: Título del proyecto 
* origen: Origen del mismo: Asamblea General, Comisión Administrativa, Comisión Permanente, Cámara Representantes, Cámara Senadores
* presentado_por: Legisladores que presentan el proyecto
* entrada_A.G.: Fecha en la que entró a Asamblea General
* entrada_C.P.: Fecha en la que entra a Comisión Permanente
* entrada_CRR: Fecha en la que entra a Cámara de Representantes
* entrada_CSS: Fecha en la que entra a Cámara de Senadores
* sanciona_A.G.: Fecha en la que la Asamblea General sanciona 
* sanciona_CRR: Fecha en al que la Cámara de Representantes sanciona
* sanciona_CSS: Fecha en la que la Cámara de Senadores sanciona
* sanciona_PE: Fecha en la que el Poder Ejecutivo sanciona.
* num_comisiones: Número de comisiones por las que pasa la ficha
* num_sesiones: Número de sesiones en las que se trató el proyecto.

##### Extracción: 
https://parlamento.gub.uy/documentosyleyes/ficha-asunto/123564


