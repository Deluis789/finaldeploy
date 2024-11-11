import string
import random
from django.db import models
from django.contrib.auth.models import User, Group
    
class CalleAv(models.Model):
    nombre = models.CharField(max_length=100, null=False, blank=False)
    descripcion = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = "Calle/Avenida"
        verbose_name_plural = "Calles/Avenidas"

    def __str__(self):
        return self.nombre
    
class Urbanizaciones(models.Model):
    gid = models.AutoField(primary_key=True)
    field_gid = models.DecimalField(db_column='__gid', max_digits=10, decimal_places=0, blank=True, null=True)  # Field renamed because it contained more than one '_' in a row. Field renamed because it started with '_'.
    nombre = models.CharField(max_length=50, blank=True, null=True)
    c_dist_mun = models.DecimalField(max_digits=10, decimal_places=0, blank=True, null=True)
    rta = models.CharField(max_length=15, blank=True, null=True)
    fecha_rta = models.CharField(max_length=15, blank=True, null=True)
    rm = models.CharField(max_length=15, blank=True, null=True)
    fecha_rm = models.CharField(max_length=15, blank=True, null=True)
    fecha_aniv = models.CharField(max_length=50, blank=True, null=True)
    nom_presid = models.CharField(max_length=50, blank=True, null=True)
    poblacion = models.DecimalField(max_digits=10, decimal_places=0, blank=True, null=True)
    obs = models.CharField(max_length=100, blank=True, null=True)
    gid_urb = models.DecimalField(max_digits=10, decimal_places=0, blank=True, null=True)
    area_m2 = models.DecimalField(max_digits=10, decimal_places=0, blank=True, null=True)
    telefono = models.CharField(max_length=50, blank=True, null=True)
    geom = models.TextField(blank=True, null=True)  # This field type is a guess.

    class Meta:
        managed = False
        db_table = 'urbanizaciones'
    
    def __str__(self):
        return self.nombre

class Usuarios(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='usuarios')  # Relación con User
    nombres = models.CharField(max_length=50, null=False, blank=False)
    apellido_paterno = models.CharField(max_length=50, null=False, blank=False)
    apellido_materno = models.CharField(max_length=50, null=False, blank=False)
    ci = models.CharField(max_length=10, null=False, blank=False)  # CI como CharField
    calle_av = models.ForeignKey('CalleAv', on_delete=models.RESTRICT, null=False, blank=False)
    urbanizaciones = models.ForeignKey('Urbanizaciones', on_delete=models.RESTRICT, null=False, blank=False)
    numero_vivienda = models.CharField(max_length=10)
    rol = models.ManyToManyField(Group, blank=True)
    codigo_usuario = models.CharField(max_length=6, unique=True, blank=True, null=True)  # Añade este campo

    def save(self, *args, **kwargs):
        # Genera el código de usuario si no existe
        if not self.codigo_usuario:
            self.codigo_usuario = self._generate_unique_code()

        # Actualiza los campos first_name, last_name y username del usuario relacionado
        self.user.first_name = self.nombres
        self.user.last_name = self.apellido_paterno
        self.user.username = self.ci  # Usa el CI como username
        self.user.save()  # Guarda los cambios en el modelo User

        # Llama al método save() del modelo base
        super().save(*args, **kwargs)

    def _generate_unique_code(self):
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        while Usuarios.objects.filter(codigo_usuario=code).exists():
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        return code

    def __str__(self):
        return self.codigo_usuario

class SolicitudVecino(models.Model):
    urbanizaciones = models.ForeignKey(Urbanizaciones, on_delete=models.RESTRICT, null=False, blank=False)
    codigo_vecino = models.CharField(max_length=10, unique=True, blank=True, null=True)  # Campo para el código generado
    distrito = models.DecimalField(max_digits=10, decimal_places=0, blank=True, null=True)  # Cambiado a DecimalField
    ubicacion_geografica = models.CharField(max_length=100, help_text="Formato: Latitud, Longitud")
    foto = models.ImageField(upload_to='imagenes_vecinos/', blank=False, null=False) 
    nombres = models.CharField(max_length=100)
    apellido_paterno = models.CharField(max_length=100)
    apellido_materno = models.CharField(max_length=100)
    cedula_identidad = models.CharField(max_length=20, unique=True)
    celular = models.CharField(max_length=15)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        # Genera el código de solicitud si no existe
        if not self.codigo_vecino:
            self.codigo_vecino = self._generate_unique_code()
        
        # Si se proporciona urbanizaciones, asignar el c_dist_mun a distrito
        if self.urbanizaciones:
            self.distrito = self.urbanizaciones.c_dist_mun  # No se requiere conversión si es DecimalField
            
        super().save(*args, **kwargs)

    def _generate_unique_code(self):
        # Genera un código aleatorio de 10 caracteres
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
        while SolicitudVecino.objects.filter(codigo_vecino=code).exists():
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
        return code

    def __str__(self):
        return f"{self.codigo_vecino} - {self.nombres}"

class Solicitudes(models.Model):
    urbanizaciones = models.ForeignKey(Urbanizaciones, on_delete=models.RESTRICT, null=False, blank=False)
    codigo_vecino = models.ForeignKey(SolicitudVecino, on_delete=models.RESTRICT, null=False, blank=False)
    distrito = models.CharField(max_length=10, blank=True, null=True)
    ubicacion_geografica = models.CharField(max_length=100, help_text="Formato: Latitud, Longitud")
    nombres = models.CharField(max_length=100)
    apellido_paterno = models.CharField(max_length=100)
    apellido_materno = models.CharField(max_length=100)
    cedula_identidad = models.CharField(max_length=20, unique=True)
    designacion = models.OneToOneField(User, on_delete=models.CASCADE, related_name='solicitud_designacion')
    estado = models.CharField(max_length=50, choices=[('realizado', 'Realizado'), ('aprobado', 'Aprobado'), ('rechazado', 'Rechazado'), ('desecho', 'Desecho')])

    def __str__(self):
        return f'{self.codigo_vecino} - {self.estado}'


class FichaOperativa(models.Model):
    codigo = models.ForeignKey('Solicitudes', on_delete=models.RESTRICT, null=False, blank=False)  # Relación con Solicitudes
    fecha = models.DateField()
    distrito = models.CharField(max_length=10, blank=False, null=False)
    urbanizacion = models.CharField(max_length=100, blank=False, null=False)
    latitud_longitud = models.CharField(max_length=100, help_text="Formato: Latitud, Longitud")
    tecnico = models.CharField(max_length=50, blank=False, null=False)
    ubicacion_direccion = models.CharField(max_length=100, blank=False, null=False)
    cuadrilla = models.CharField(max_length=100, blank=False, null=False)
    maquinaria = models.CharField(max_length=100, blank=True, null=True)
    operador = models.CharField(max_length=100, blank=True, null=True)
    concepto = models.CharField(max_length=100)
    volumen = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=200)
    fotoInicio = models.ImageField(upload_to='fichas_operativas/', blank=False, null=False)
    fotoDesarollo = models.ImageField(upload_to='fichas_operativas/', blank=False, null=False)
    fotoCulminado = models.ImageField(upload_to='fichas_operativas/', blank=False, null=False)
    
    estado = models.CharField(max_length=50, choices=[('finalizado', 'Finalizado'), ('proceso', 'En proceso'), ('abandono', 'Abandonado')])

    def __str__(self):
        return f'{self.codigo} - {self.estado}'