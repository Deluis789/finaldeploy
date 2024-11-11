from django.contrib import admin
from .models import Usuarios, CalleAv, Urbanizaciones, SolicitudVecino, Solicitudes, FichaOperativa
# Register your models here.
@admin.register(Usuarios)
class UsuariosAdmin(admin.ModelAdmin):
    list_display = ('codigo_usuario', 'nombres', 'apellido_paterno','apellido_materno', 'ci', 'calle_av', 'numero_vivienda')
    search_fields = ('nombres', 'apellido_paterno', 'codigo_usuario', 'ci')
admin.site.register(CalleAv)
admin.site.register(Urbanizaciones)
admin.site.register(SolicitudVecino)
admin.site.register(Solicitudes)
admin.site.register(FichaOperativa)
