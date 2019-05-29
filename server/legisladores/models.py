# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class ActuacionParlamentaria(models.Model):
    id_legislador = models.ForeignKey('Legisladores', models.DO_NOTHING, db_column='id_legislador', blank=True, null=True)
    id_legislatura = models.IntegerField(blank=True, null=True)
    tipo = models.TextField(blank=True, null=True)
    fecha = models.TextField(blank=True, null=True)
    detalle = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'actuacion_parlamentaria'


class AsistenciaComisiones(models.Model):
    id_comision = models.IntegerField(blank=True, null=True)
    id_legislador = models.ForeignKey('Legisladores', models.DO_NOTHING, db_column='id_legislador', blank=True, null=True)
    id_legislatura = models.TextField(blank=True, null=True)
    fecha = models.TextField(blank=True, null=True)
    citaciones = models.IntegerField(blank=True, null=True)
    asistencias = models.IntegerField(blank=True, null=True)
    faltas_con_aviso = models.IntegerField(blank=True, null=True)
    faltas_sin_aviso = models.IntegerField(blank=True, null=True)
    licencia = models.IntegerField(blank=True, null=True)
    otras_comisiones = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'asistencia_comisiones'


class AsistenciaPlenario(models.Model):
    id_legislador = models.ForeignKey('Legisladores', models.DO_NOTHING, db_column='id_legislador', blank=True, null=True)
    id_legislatura = models.IntegerField(blank=True, null=True)
    camara = models.TextField(blank=True, null=True)
    fecha = models.TextField(blank=True, null=True)
    citaciones = models.IntegerField(blank=True, null=True)
    asistencias = models.IntegerField(blank=True, null=True)
    faltas_con_aviso = models.IntegerField(blank=True, null=True)
    faltas_sin_aviso = models.IntegerField(blank=True, null=True)
    licencia = models.IntegerField(blank=True, null=True)
    pasaje_presidencia = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'asistencia_plenario'


class Comisiones(models.Model):
    id_comision = models.AutoField(primary_key=True, blank=True, null=False)
    nombre = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'comisiones'


class Convocatoria(models.Model):
    id_legislador = models.ForeignKey('Legisladores', models.DO_NOTHING, db_column='id_legislador', blank=True, null=True)
    id_legislatura = models.IntegerField(blank=True, null=True)
    fecha_ini = models.TextField(blank=True, null=True)
    camara = models.TextField(blank=True, null=True)
    lema = models.TextField(blank=True, null=True)
    departamento = models.TextField(blank=True, null=True)
    sublema = models.TextField(blank=True, null=True)
    fecha_fin = models.TextField(blank=True, null=True)
    titular = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'convocatoria'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class EvolucionProyectos(models.Model):
    id_proyecto = models.IntegerField(blank=True, null=True)
    id_legislatura = models.IntegerField(blank=True, null=True)
    tipo = models.TextField(blank=True, null=True)
    fecha = models.TextField(blank=True, null=True)
    cuerpo = models.TextField(blank=True, null=True)
    detalle = models.TextField(blank=True, null=True)
    id_comision = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'evolucion_proyectos'


class IndiceLegisladores(models.Model):
    nombre = models.TextField(blank=True, null=True)
    cuerpo = models.TextField(blank=True, null=True)
    lema = models.TextField(blank=True, null=True)
    id_legislador = models.AutoField(primary_key=True, blank=True, null=False)
    asistencias = models.IntegerField(blank=True, null=True)
    citaciones = models.IntegerField(blank=True, null=True)
    proyectos_total = models.IntegerField(blank=True, null=True)
    informes_total = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'indice_legisladores'


class Legisladores(models.Model):
    id_legislador = models.AutoField(primary_key=True, blank=True, null=False)
    nombre = models.TextField(blank=True, null=True)
    cuerpo = models.TextField(blank=True, null=True)
    email = models.TextField(blank=True, null=True)
    lema = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'legisladores'


class Legislaturas(models.Model):
    id_legislatura = models.AutoField(primary_key=True, blank=True, null=False)
    legislatura = models.TextField(blank=True, null=True)
    date_from = models.TextField(blank=True, null=True)
    date_to = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'legislaturas'


class Proyectos(models.Model):
    id_proyecto = models.AutoField(primary_key=True, blank=True, null=False)
    origen = models.TextField(blank=True, null=True)
    tipo = models.TextField(blank=True, null=True)
    titulo = models.TextField(blank=True, null=True)
    presentado_por = models.TextField(blank=True, null=True)
    evolucion = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'proyectos'


class ProyectosPresentados(models.Model):
    id_proyecto = models.IntegerField(blank=True, null=True)
    id_legislador = models.ForeignKey(Legisladores, models.DO_NOTHING, db_column='id_legislador', blank=True, null=True)
    id_legislatura = models.IntegerField(blank=True, null=True)
    fecha = models.TextField(blank=True, null=True)
    organismo = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'proyectos_presentados'

