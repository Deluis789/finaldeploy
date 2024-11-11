from django.urls import path
from apps.home import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('inicio/', views.inicio, name='inicio'),
    path('listarUsuarios/', views.listar, name='listarUsuarios'),
    path('registrarUsuarios/', views.registrarUsuarios, name='registrarUsuarios'),
    path('eliminarUsuarios/<str:ci>/', views.eliminarUsuarios, name='eliminarUsuarios'),
    path('edicionUsuarios/<str:ci>', views.edicionUsuarios, name='edicionUsuarios'),
    path('editarUsuarios/', views.editarUsuarios, name='editarUsuarios'),
    
    path('listarVecinos/', views.listarVecinos, name='listarVecinos'),
    path('registrarVecinos/', views.registrarVecinos, name='registrarVecinos'),
    path('eliminarSolicitudVecino/<str:codigo_vecino>/', views.eliminarSolicitudVecino, name='eliminarSolicitudVecino'),
    
    path('solicitud/nueva/', views.formulario_solicitud, name='formulario_solicitud'),
    path('obtener-datos-vecino/<int:vecino_id>/', views.obtener_datos_vecino, name='obtener_datos_vecino'),
    path('listarSolicitudes/', views.listarSolicitudes, name='listarSolicitudes'),
    path('eliminarSolicitudes/<str:codigo_vecino>/', views.eliminarSolicitudes, name='eliminarSolicitudes'),
    
    path('ficha/', views.formulario_ficha, name='formulario_ficha'),
    path('obtener_datos/<int:codigo_id>/', views.obtener_datos_solicitudes, name='obtener_datos_solicitudes'),
    path('listarFichas/', views.listarFichas, name='listarFichas'),
    path('eliminarFichas/<int:codigo>/', views.eliminarFichas, name='eliminarFichas'),
    
    # path('reporte/', views.reporte, name='reporte'),
    # path('ficha/<int:ficha_id>/reporte/', views.generar_reporte_pdf, name='generar_reporte_pdf'),
    path('reporte/ficha_operativa/<int:ficha_id>/', views.generate_report, name='generate_report'),
]
