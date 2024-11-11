from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django import template
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.template import loader
from django.urls import reverse
from .models import Usuarios, CalleAv, Urbanizaciones, SolicitudVecino, Solicitudes, FichaOperativa
from django.contrib.auth.models import Group, User

#pagina vistas--------------------->>>>>>>>>>>>>>>><
def index(request):
    return render(request, 'pagina/inicio.html', {})

def geoportal(request):
    return render(request, 'pagina/geoportal.html', {})
# Create your views here.
def login_view(request):
    # Si el usuario ya está autenticado, redirigir a 'inicio'
    if request.user.is_authenticated:
        return redirect('inicio')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Autenticar al usuario
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # Login exitoso
            login(request, user)
            return redirect('inicio')
        else:
            # Credenciales inválidas
            messages.error(request, 'Usuario o contraseña incorrectos.')

    return render(request, 'home/auth-login.html')  # Renderizar la plantilla de login

@login_required
def inicio(request):
    return render(request, 'home/index.html', {})


def listar(request):
    usuariosListados = Usuarios.objects.all()
    return render(request, "home/tabla-usuarios.html", {"usuarios": usuariosListados})

def registrarUsuarios(request):
    if request.method == 'POST':
        # Obtener campos del formulario
        nombres = request.POST.get('nombres')
        apellido_paterno = request.POST.get('apellido_paterno')
        apellido_materno = request.POST.get('apellido_materno')
        rol_id = request.POST.get('rol')  # ID del rol
        user_id = request.POST.get('user')  # ID del usuario
        ci = request.POST.get('ci')  # Cédula de identidad
        urbanizacion_id = request.POST.get('urbanizaciones')  # ID de urbanización
        calle_av_name = request.POST.get('calle_avenida')  # Nombre de la calle
        numero_vivienda = request.POST.get('numero_vivienda')  # Número de vivienda

        # Obtener el grupo (rol) desde la base de datos
        grupo = Group.objects.get(id=rol_id)

        # Obtener el usuario desde la base de datos
        user = User.objects.get(id=user_id)

        # Obtener la urbanización desde la base de datos usando el ID
        urbanizacion = Urbanizaciones.objects.get(gid=urbanizacion_id)

        # Crear o obtener la instancia de CalleAv
        calle_av, created = CalleAv.objects.get_or_create(
            nombre=calle_av_name,
            defaults={'descripcion': ''}
        )

        # Crear el registro de usuario en la base de datos
        usuario = Usuarios.objects.create(
            nombres=nombres,
            apellido_paterno=apellido_paterno,
            apellido_materno=apellido_materno,
            user=user,
            ci=ci,
            calle_av=calle_av,
            urbanizaciones=urbanizacion,
            numero_vivienda=numero_vivienda
        )

        # Generar el código de usuario
        codigo_usuario = usuario._generate_unique_code()  # Llama al método del modelo
        usuario.codigo_usuario = codigo_usuario  # Asigna el código generado
        usuario.save()  # Guarda el usuario para que tenga un ID

        # Asigna el rol (grupo) al usuario
        usuario.rol.add(grupo)  

        # Aquí pasamos los grupos de todos los usuarios, no solo del recién creado
        grupos = Group.objects.all()  # Obtener todos los grupos (roles) disponibles
        users = User.objects.all()  # Obtener todos los usuarios disponibles

        return render(request, 'home/agregar-usuarios.html', {
            'zonas_urb': Urbanizaciones.objects.all(),  # Obtener todas las urbanizaciones para el formulario
            'usuario': usuario,  # Pasar el usuario creado a la plantilla
            'grupos': grupos,  # Pasar todos los grupos disponibles
            'users': users,  # Pasar todos los usuarios disponibles
            'codigo_usuario': codigo_usuario,  # Pasar el código de usuario generado
        })
    else:
        # Si no es un POST, renderiza el formulario (opcional)
        zonas_urb = Urbanizaciones.objects.all()  # Obtén todas las urbanizaciones para el formulario
        grupos = Group.objects.all()  # Obtener todos los grupos
        users = User.objects.all()  # Obtener todos los usuarios
        return render(request, 'home/agregar-usuarios.html', {
            'zonas_urb': zonas_urb,
            'grupos': grupos,
            'users': users,  # Asegúrate de pasar todos los usuarios
        })

from django.contrib import messages

def eliminarUsuarios(request, ci):
    try:
        # Obtener el usuario por su username (que es el CI)
        user = User.objects.get(username=ci)
        user.delete()
        messages.success(request, "Usuario eliminado con éxito.")
    except User.DoesNotExist:
        messages.error(request, "El usuario no existe.")
    except Exception as e:
        messages.error(request, f"Error al eliminar el usuario: {str(e)}")
    
    return redirect('listarUsuarios')  # Redirige a la lista de usuarios

def edicionUsuarios(request, ci):
    # Obtener el usuario correspondiente al CI
    usuario = Usuarios.objects.get(ci=ci)
    
    # Obtener todos los grupos de roles disponibles
    grupos = Group.objects.all()
    
    # Obtener todos los usuarios
    users = User.objects.all()
    
    # Obtener todas las zonas urbanas
    urbanizaciones = Urbanizaciones.objects.all()
    
    # Pasar estos datos al contexto
    return render(request, "home/editarusuarios.html", {
        "usuario": usuario,
        "grupos": grupos,
        "users": users,
        "urbanizaciones": urbanizaciones
    })

from django.shortcuts import render, get_object_or_404, redirect
def editarUsuarios(request):
    # Obtener datos del formulario
    nombres = request.POST['nombres']
    apellido_paterno = request.POST['apellido_paterno']
    apellido_materno = request.POST['apellido_materno']
    rol_id = request.POST.get('rol')
    user_id = request.POST.get('user')  # ID del usuario a editar
    ci = request.POST['ci']
    urbanizacion_id = request.POST.get('urbanizaciones') 
    calle_av_name = request.POST['calle_avenida']
    numero_vivienda = request.POST['numero_vivienda']

    # Obtener el usuario existente
    user = get_object_or_404(User, id=user_id)
    
    # Actualizar datos del usuario
    user.first_name = nombres
    user.last_name = apellido_paterno + " " + apellido_materno
    user.username = ci  # Si quieres que el CI sea el username
    user.save()

    # Actualizar grupo (rol)
    grupo = get_object_or_404(Group, id=rol_id)
    user.groups.clear()  # Limpiar grupos antiguos
    user.groups.add(grupo)  # Agregar nuevo rol

    # Actualizar zona urbana
    urbanizacion = get_object_or_404(Urbanizaciones, gid=urbanizacion_id)

    # Actualizar o crear la calle
    calle_av, created = CalleAv.objects.get_or_create(
        nombre=calle_av_name,
        defaults={'descripcion': '',}
    )

    # Actualizar información del modelo Usuarios
    usuario = get_object_or_404(Usuarios, user=user)
    usuario.urbanizaciones = urbanizacion
    usuario.calle_av = calle_av
    usuario.numero_vivienda = numero_vivienda
    usuario.save()

    return redirect('listarUsuarios')  # Redirigir a la lista de usuarios


# SolicitudVecino vistas----------------------------------

def listarVecinos(request):
    vecinosListados = SolicitudVecino.objects.all()
    return render(request, "home/tabla-vecino.html", {"vecinos": vecinosListados})

def registrarVecinos(request):
    codigo_vecino = None  # Variable para almacenar el código generado

    if request.method == 'POST':
        urbanizacion_id = request.POST.get('urbanizacion')
        ubicacion_geografica = request.POST.get('ubicacion')
        foto = request.FILES.get('imagen')
        nombres = request.POST.get('nombres')
        apellido_paterno = request.POST.get('apellido_paterno')
        apellido_materno = request.POST.get('apellido_materno')
        cedula_identidad = request.POST.get('cedula_identidad')
        celular = request.POST.get('celular')

        # Obtener la urbanización desde la base de datos
        urbanizacion = Urbanizaciones.objects.get(gid=urbanizacion_id)

        # Generar un nuevo código de vecino
        codigo_vecino = SolicitudVecino()._generate_unique_code()  # Genera el código sin guardar el objeto

        # Crear el registro de solicitud en la base de datos
        solicitud = SolicitudVecino.objects.create(
            urbanizaciones=urbanizacion,
            codigo_vecino=codigo_vecino,  # Asigna el código generado
            ubicacion_geografica=ubicacion_geografica,
            foto=foto,
            nombres=nombres,
            apellido_paterno=apellido_paterno,
            apellido_materno=apellido_materno,
            cedula_identidad=cedula_identidad,
            celular=celular
        )

        # Guarda la solicitud para ejecutar la lógica en el método save
        solicitud.save()

        # Redirigir o renderizar la respuesta
        return render(request, 'pagina/formvecino.html', {
            'solicitud': solicitud,
        })
    else:
        # Si no es un POST, generamos un nuevo código vecino
        codigo_vecino = SolicitudVecino()._generate_unique_code()  # Genera el código para mostrar en el formulario

        # Obtener todas las urbanizaciones para el formulario
        urbanizaciones = Urbanizaciones.objects.all()
        return render(request, 'pagina/formvecino.html', {
            'urbanizaciones': urbanizaciones,
            'codigo_vecino': codigo_vecino,  # Pasar el código generado a la plantilla
        })

def eliminarSolicitudVecino(request, codigo_vecino):
    try:
        # Obtener la solicitud vecino por su código único
        solicitud_vecino = get_object_or_404(SolicitudVecino, codigo_vecino=codigo_vecino)
        solicitud_vecino.delete()
        messages.success(request, "Solicitud de vecino eliminada con éxito.")
    except Exception as e:
        messages.error(request, f"Error al eliminar la solicitud de vecino: {str(e)}")
    
    return redirect('listarVecinos')


# Solicitudes ------->>>>>>>>>>>>>>

from django.http import JsonResponse
# Vista para manejar el formulario principal
def formulario_solicitud(request):
    vecinos = SolicitudVecino.objects.all()
    zonas_urb = Urbanizaciones.objects.all()
    designaciones = User.objects.all()

    estado_opciones = Solicitudes._meta.get_field('estado').choices
    
    if request.method == 'POST':
        # Aquí puedes procesar los datos y guardar la solicitud
        # Recoge los datos del formulario manualmente, por ejemplo:
        codigo_vecino_id = request.POST.get('codigo_vecino')
        distrito = request.POST.get('distrito')
        nombres = request.POST.get('nombres')
        ubicacion_geografica = request.POST.get('ubicacion_geografica') 
        apellido_paterno = request.POST.get('apellido_paterno')
        apellido_materno = request.POST.get('apellido_materno')
        estado = request.POST.get('estado')
        cedula_identidad = request.POST.get('cedula_identidad')
        designacion_id = request.POST.get('designacion')
        
                # Crea una nueva instancia de Solicitudes
        solicitud = Solicitudes(
            urbanizaciones_id=request.POST.get('urbanizaciones'),  # Asegúrate de que este campo esté en tu formulario
            codigo_vecino_id=codigo_vecino_id,
            distrito=distrito,
            ubicacion_geografica=ubicacion_geografica,  # Agregado
            nombres=nombres,  # No es necesario si se guarda desde 'codigo_vecino'
            apellido_paterno=apellido_paterno,  # No es necesario si se guarda desde 'codigo_vecino'
            apellido_materno=apellido_materno,  # No es necesario si se guarda desde 'codigo_vecino'
            cedula_identidad=cedula_identidad,  # Agregado
            designacion_id=designacion_id,  # Relación con el User
            estado=estado
        )
        solicitud.save()

        # Guardar en la base de datos si es necesario

    return render(request, 'home/agregar-solicitudes.html', {
        'vecinos': vecinos,
        'zonas_urb': zonas_urb,
        'designaciones': designaciones,
        'estado_opciones': estado_opciones,
    })

# Vista para manejar el AJAX que devuelve los datos del vecino
def obtener_datos_vecino(request, vecino_id):
    vecino = get_object_or_404(SolicitudVecino, id=vecino_id)
    data = {
        'nombres': vecino.nombres,
        'apellido_paterno': vecino.apellido_paterno,
        'apellido_materno': vecino.apellido_materno,
        'cedula_identidad': vecino.cedula_identidad,
        'ubicacion_geografica': vecino.ubicacion_geografica,
        'distrito': vecino.distrito,
    }
    return JsonResponse(data)

def listarSolicitudes(request):
    solicitudesListados = Solicitudes.objects.all()
    return render(request, "home/tabla-solicitudes.html", {"solicitud": solicitudesListados})

def eliminarSolicitudes(request, codigo_vecino):
    try:
        # Obtener la solicitud vecino por su código único
        solicitudes = get_object_or_404(Solicitudes, codigo_vecino=codigo_vecino)
        solicitudes.delete()
        messages.success(request, "Solicitud de vecino eliminada con éxito.")
    except Exception as e:
        messages.error(request, f"Error al eliminar la solicitud de vecino: {str(e)}")
    
    return redirect('listarSolicitudes')


# Fichas Operativas ------->>>>>>>>>>>>>>

def formulario_ficha(request):
    solicitudes = Solicitudes.objects.all()
    estado_opciones = FichaOperativa._meta.get_field('estado').choices
    designaciones = Usuarios.objects.all()

    if request.method == 'POST':
        codigo_id = request.POST.get('codigo')
        solicitud = get_object_or_404(Solicitudes, id=codigo_id)

        # Obtén los datos del formulario
        fecha = request.POST.get('fecha')
        distrito = solicitud.distrito
        urbanizacion = solicitud.urbanizaciones.nombre
        ubicacion_direccion = request.POST.get('ubicacion_direccion')
        latitud_longitud = request.POST.get('latitud_longitud')  # Asegúrate de capturar esto
        tecnico_id = request.POST.get('designacion')  # Captura el id del técnico seleccionado
        cuadrilla = request.POST.get('cuadrilla')
        maquinaria = request.POST.get('maquinaria')
        operador = request.POST.get('operador')
        concepto = request.POST.get('concepto')
        volumen = request.POST.get('volumen')
        fotoInicio = request.FILES.get('imagenInicio')
        fotoDesarollo = request.FILES.get('imagenDesarollo')
        fotoCulminado = request.FILES.get('imagenCulminado')
        estado = request.POST.get('estado')

        try:
            # Crear una nueva instancia de FichaOperativa
            ficha = FichaOperativa(
                codigo=solicitud,
                fecha=fecha,
                distrito=distrito,
                urbanizacion=urbanizacion,
                ubicacion_direccion=ubicacion_direccion,
                latitud_longitud=latitud_longitud,  # Asegúrate de usar este valor
                tecnico=tecnico_id,  # Guarda el id del técnico o usa el nombre según lo necesites
                cuadrilla=cuadrilla,
                maquinaria=maquinaria,
                operador=operador,
                concepto=concepto,
                volumen=volumen,
                fotoInicio=fotoInicio,
                fotoDesarollo=fotoDesarollo,
                fotoCulminado=fotoCulminado,
                estado=estado
            )
            ficha.save()
        except Exception as e:
            print(f"Error al guardar FichaOperativa: {e}")

    return render(request, 'home/agregar-fichas.html', {
        'solicitudes': solicitudes,
        'estado_opciones': estado_opciones,
        'designaciones': designaciones,
    })


# Vista para manejar el AJAX que devuelve los datos de solicitudes
def obtener_datos_solicitudes(request, codigo_id):
    solicitud = get_object_or_404(Solicitudes, id=codigo_id)
    data = {
        'distrito': solicitud.distrito,
        'urbanizacion': solicitud.urbanizaciones.nombre,
        'latitud_longitud': solicitud.ubicacion_geografica,  # Asegúrate de que esto esté disponible
        'tecnico': f"{solicitud.designacion.first_name} {solicitud.designacion.last_name}",
    }
    return JsonResponse(data)

def listarFichas(request):
    fichasListados = FichaOperativa.objects.all()
    return render(request, "home/tabla-fichas.html", {"fichas": fichasListados})

def eliminarFichas(request, codigo):
    try:
        # Obtener la solicitud vecino por su código único
        fichas = get_object_or_404(FichaOperativa, id=codigo)
        fichas.delete()
        messages.success(request, "Solicitud de vecino eliminada con éxito.")
    except Exception as e:
        messages.error(request, f"Error al eliminar la solicitud de vecino: {str(e)}")
    
    return redirect('listarSolicitudes')


#Reportes-----------------------------

# from django.shortcuts import render
# from django.http import HttpResponse
# from django.template.loader import render_to_string
# from xhtml2pdf import pisa
# from django.templatetags.static import static
# from .models import FichaOperativa
# import os
# from django.conf import settings

# def generar_reporte_pdf(request, ficha_id):
#     # Obtener la ficha operativa por su ID
#     ficha = FichaOperativa.objects.get(id=ficha_id)

#     # Convertir las rutas estáticas a absolutas
#     logo1_url = request.build_absolute_uri(static('assets/images/logo-alto.png'))
#     logo2_url = request.build_absolute_uri(static('assets/images/escudo.jpg'))
    
#     # Se asume que las fotos también están en el directorio de estáticos
#     foto_inicio_url = request.build_absolute_uri(ficha.fotoInicio.url)
#     foto_desarrollo_url = request.build_absolute_uri(ficha.fotoDesarollo.url)
#     foto_culminado_url = request.build_absolute_uri(ficha.fotoCulminado.url)

#     # Preparar los contextos necesarios para la plantilla
#     context = {
#         'ficha': ficha,
#         'logo1_url': logo1_url,
#         'logo2_url': logo2_url,
#         'foto_inicio_url': foto_inicio_url,
#         'foto_desarrollo_url': foto_desarrollo_url,
#         'foto_culminado_url': foto_culminado_url,
#     }

#     # Renderizar la plantilla a un string
#     html = render_to_string('home/reporte-ficha.html', context)

#     # Crear un objeto de respuesta HTTP para la descarga del archivo PDF
#     response = HttpResponse(content_type='application/pdf')
#     response['Content-Disposition'] = f'attachment; filename="reporte_ficha_{ficha_id}.pdf"'

#     # Usar xhtml2pdf para convertir el HTML a PDF
#     pisa_status = pisa.CreatePDF(html, dest=response)

#     # Verificar si hubo algún error durante la conversión
#     if pisa_status.err:
#         return HttpResponse('Error al generar el PDF', status=500)

#     return response

from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Table, TableStyle, Paragraph, Image, Spacer
from reportlab.lib.units import inch
from .models import FichaOperativa
import os

def generate_report(request, ficha_id):
    try:
        # Obtener la instancia de la ficha operativa
        ficha = FichaOperativa.objects.get(id=ficha_id)
    except FichaOperativa.DoesNotExist:
        return HttpResponse("Ficha Operativa no encontrada.", status=404)

    # Configurar la respuesta HTTP para la descarga del archivo PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="reporte_{ficha.codigo}.pdf"'

    # Crear el objeto canvas para dibujar el PDF
    p = canvas.Canvas(response, pagesize=letter)
    width, height = letter  # Tamaño de la página

    # Configuración de la fuente
    p.setFont("Helvetica", 10)

    # Agregar logos en las esquinas superiores
    logo_size = 50
    if ficha.fotoInicio and os.path.exists(ficha.fotoInicio.path):
        p.drawImage(ficha.fotoInicio.path, 40, height - logo_size - 40, width=logo_size, height=logo_size)
    if ficha.fotoCulminado and os.path.exists(ficha.fotoCulminado.path):
        p.drawImage(ficha.fotoCulminado.path, width - 40 - logo_size, height - logo_size - 40, width=logo_size, height=logo_size)

    # Título del reporte
    p.setFont("Helvetica-Bold", 16)
    p.drawCentredString(width / 2, height - 100, "Ficha Operativa Reporte")
    p.setLineWidth(1)
    p.line(40, height - 105, width - 40, height - 105)

    # Tabla principal con datos
    p.setFont("Helvetica", 10)
    data = [
        ["Código:", ficha.codigo],
        ["Distrito:", ficha.distrito],
        ["Fecha:", ficha.fecha.strftime('%d/%m/%Y')],
        ["Urbanización:", ficha.urbanizacion],
        ["Ubicación:", ficha.ubicacion_direccion],
        ["Latitud-Longitud:", ficha.latitud_longitud],
        ["Técnico:", ficha.tecnico],
        ["Cuadrilla:", ficha.cuadrilla],
        ["Estado:", ficha.estado],
        ["Maquinaria:", ficha.maquinaria or 'N/A'],
        ["Operador:", ficha.operador or 'N/A'],
        ["Concepto:", ficha.concepto],
        ["Volumen:", ficha.volumen],
        ["Descripción:", ficha.descripcion],
    ]

    table = Table(data, colWidths=[100, 300])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    table.wrapOn(p, width, height)
    table.drawOn(p, 40, height - 200)

    # Espacio antes de la galería de fotos
    y_position = height - 350

    # Título para la galería de fotos
    p.setFont("Helvetica-Bold", 12)
    p.drawString(40, y_position, "Fotos del Proceso:")
    y_position -= 20

    # Insertar las fotos en una sola fila horizontal
    photo_width = 150
    photo_height = 100
    photos = [
        ('Inicio', ficha.fotoInicio.path if ficha.fotoInicio and os.path.exists(ficha.fotoInicio.path) else None),
        ('Desarrollo', ficha.fotoDesarollo.path if ficha.fotoDesarollo and os.path.exists(ficha.fotoDesarollo.path) else None),
        ('Culminado', ficha.fotoCulminado.path if ficha.fotoCulminado and os.path.exists(ficha.fotoCulminado.path) else None),
    ]
    
    x_position = (width - (photo_width * len(photos) + 20 * (len(photos) - 1))) / 2
    for title, path in photos:
        if path:
            p.drawImage(path, x_position, y_position - photo_height, width=photo_width, height=photo_height)
            p.setFont("Helvetica", 10)
            p.drawCentredString(x_position + photo_width / 2, y_position - photo_height - 15, title)
        else:
            p.setFont("Helvetica", 10)
            p.drawCentredString(x_position + photo_width / 2, y_position - photo_height - 15, f"{title}: No disponible")
        x_position += photo_width + 20  # Espacio entre fotos

    y_position -= photo_height + 60

    # Tabla de pie de página para Firma y Observaciones
    p.setFont("Helvetica-Bold", 12)
    p.drawString(40, y_position, "Firma y Observaciones:")
    y_position -= 20

    footer_data = [
        ['Firma:', 'Sello:'],
        ['', '']
    ]
    footer_table = Table(footer_data, colWidths=[200, 200])
    footer_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
        ('LINEABOVE', (0, 1), (-1, 1), 1, colors.black),
    ]))
    footer_table.wrapOn(p, width, y_position)
    footer_table.drawOn(p, 40, y_position - 30)

    # Finalizar el documento
    p.showPage()
    p.save()

    return response



