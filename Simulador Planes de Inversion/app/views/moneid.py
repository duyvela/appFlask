from flask import Flask, Blueprint, flash, g, redirect, render_template, request, session, url_for, jsonify, Response, send_file, make_response

from datetime import datetime
from jinja2 import Environment
import json
from io import BytesIO
import jinja2
from fpdf import FPDF

import os, io, base64
from docxtpl import DocxTemplate, InlineImage
from babel.numbers import format_currency
import pymysql
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
from PIL import Image
from docx2pdf import convert
import subprocess
import docx2txt
import pdfkit


from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import joinedload
from werkzeug.exceptions import abort
from werkzeug.security import check_password_hash, generate_password_hash
from app.mensajeflash import *
from functools import wraps

#-----------------------------------------
#
from app.models.empleado import Empleado
from app.models.rol import Rol
from app.models.sucursales import Sucursales
from app.models.plazoFijo import PlazoFijo
from app.models.rendimientoPro import RendimientoPro
from app.models.aportacion import Aportacion

from app import db

moneidAPP = Blueprint("MoneidAPP", __name__,)

def format_currency(value):
    return "${:,.2f}".format(value)

def requires_permission(permission):
    def decorator(func):
        @wraps(func)
        def decorated_function(*args, **kwargs):
            if current_user and current_user.is_authenticated:
                if not current_user.has_permission(permission):
                    flash('No tienes permiso para acceder a esta página.')
                    session['redirected_from'] = request.url
                    return redirect(url_for('MoneidAPP.dashboard'))
                return func(*args, **kwargs)
            else:
                flash('Debes iniciar sesión para acceder a esta página.')
                return redirect(url_for('auth.login'))
        return decorated_function
    return decorator


#inicio del sistema web
@moneidAPP.route("/")
def index():
    return redirect(url_for('auth.login'))


@moneidAPP.route("/MoneidAPP/dashboard")
@login_required
def dashboard():
    return render_template("dashboard/index.html", user=current_user)

@moneidAPP.route("/MoneidaAPP/users", methods=['POST', 'GET'])
@login_required
@requires_permission("administrador")
def Users():

    listaUsers =db.session.query(Empleado).all()

    sucursal_dict ={}
    sucursal = db.session.query(Sucursales).all()
    for sucur in sucursal:
        sucursal_dict[sucur.id] = sucur.nombreSucursal

    roles_dict = {}
    roles = db.session.query(Rol).all()
    for rol in roles:
        roles_dict[rol.idRol] = rol.tipoRol

    return render_template('dashboard/users.html', listaUsers=listaUsers, roles_dict=roles_dict, sucursal_dict=sucursal_dict, user=current_user)

@moneidAPP.route("/MoneidAPP/Registros", methods=['GET', 'POST'])
@login_required
#@requires_permission("administrador")
def allRegistros():

    if current_user.has_permission("administrador"):
        listaRegistroRENPRO = db.session.query(RendimientoPro).all()
    elif current_user.has_permission("colaborador"):
        listaRegistroRENPRO = db.session.query(RendimientoPro).filter_by(idEmpleado=current_user.id).all()
 
    if current_user.has_permission("administrador"):
        listaRegistroAPOR = db.session.query(Aportacion).all()
    elif current_user.has_permission("colaborador"):
        listaRegistroAPOR = db.session.query(Aportacion).filter_by(idEmpleado=current_user.id).all()

       
    if current_user.has_permission("administrador"):
        listaRegistroPF = db.session.query(PlazoFijo).all()
    elif current_user.has_permission("colaborador"):
        listaRegistroPF = db.session.query(PlazoFijo).filter_by(idEmpleado=current_user.id).all()


    empleado_dict = {}
    sucursalEmpleado = {}

    empleado_with_sucursal = db.session.query(Empleado, Sucursales).join(Empleado.sucursal)
    for usuario, sucursal in empleado_with_sucursal:
        empleado_dict[usuario.id] = f"{usuario.username} {usuario.apellidoPAtEmpleado}"
        sucursalEmpleado[usuario.id] = f"{sucursal.nombreSucursal}"
        

    return render_template('dashboard/allRegister.html',sucursalEmpleado=sucursalEmpleado, empleado_dict=empleado_dict, listaRegistroPF=listaRegistroPF, listaRegistroRENPRO=listaRegistroRENPRO, listaRegistroAPOR=listaRegistroAPOR, user=current_user)

@moneidAPP.route("/MoneidAPP/RegistrosRendimientoProgramado", methods=['GET', 'POST'])
@login_required
def registrosRenPro():
    if current_user.has_permission("administrador"):
        listaRegistroRENPRO = db.session.query(RendimientoPro).all()
    elif current_user.has_permission("colaborador"):
        listaRegistroRENPRO = db.session.query(RendimientoPro).filter_by(idEmpleado=current_user.id).all()

    empleado_dict = {}

    empleado = db.session.query(Empleado).all()
    for usuario in empleado:
        empleado_dict[usuario.id] = usuario.username + ' '+ usuario.apellidoPAtEmpleado

    return render_template('dashboard/registrosRenPro.html', listaRegistroRENPRO=listaRegistroRENPRO, empleado_dict=empleado_dict)

@moneidAPP.route("/MoneidAPP/RegistrosAportaciones", methods=['GET', 'POST'])
@login_required
def registrosAPOR():
    if current_user.has_permission("administrador"):
        listaRegistroAPOR = db.session.query(Aportacion).all()
    elif current_user.has_permission("colaborador"):
        listaRegistroAPOR = db.session.query(Aportacion).filter_by(idEmpleado=current_user.id).all()

    empleado_dict={}
    empleado = db.session.query(Empleado).all()
    for usuario in empleado:
        empleado_dict[usuario.id] = usuario.username + ' ' + usuario.apellidoPAtEmpleado

    return render_template('dashboard/registrosAPOR.html', listaRegistroAPOR=listaRegistroAPOR, empleado_dict=empleado_dict)

@moneidAPP.route("/MoneidAPP/RegistrosPlazoFijo", methods=['GET','POST'])
@login_required
def registrosPF():
    if current_user.has_permission("administrador"):
        listaRegistroPF = db.session.query(PlazoFijo).all()
    elif current_user.has_permission("colaborador"):
        listaRegistroPF = db.session.query(PlazoFijo).filter_by(idEmpleado=current_user.id).all()

    sucursal = db.session.query(Sucursales).all()

    empleado_dict = {}
    empleado = db.session.query(Empleado).all()
    for usuario in empleado:
        empleado_dict[usuario.id] = usuario.username

    
    return render_template('dashboard/registrosPF.html', listaRegistroPF=listaRegistroPF, sucursal=sucursal, empleado_dict=empleado_dict)

@moneidAPP.route("/MoneidAPP/RegistroRendimientoProgramado/borrar/<int:idRendimientoP>")
@login_required
@requires_permission("administrador")
def deleteRegistroRENPRO(idRendimientoP):

    RegistroRENPRO_delete = RendimientoPro.query.get(idRendimientoP)

    if RegistroRENPRO_delete:
        db.session.delete(RegistroRENPRO_delete)
        db.session.commit()
    else:
        flash('Registro no encontrado.', category='error')
    return redirect(url_for('MoneidAPP.registrosRenPro'))

@moneidAPP.route("/MoneidAPP/RegistroAportacion/borrar/<int:idAportacion>")
@login_required
@requires_permission("administrador")
def deleteRegistroAPOR(idAportacion):

    RegistroAPOR_delete = Aportacion.query.get(idAportacion)

    if RegistroAPOR_delete:
        db.session.delete(RegistroAPOR_delete)
        db.session.commit()
    else:
        flash('Registro no encontrado.', category='error')
    return redirect(url_for('MoneidAPP.registrosAPOR'))

@moneidAPP.route("/MoneidAPP/RegistroPlazoFijo/borrar/<int:idPlazoFijo>")
@login_required
@requires_permission("administrador")
def deleteRegistroPF(idPlazoFijo):
    
    RegistroPF_delete = PlazoFijo.query.get(idPlazoFijo)

    if RegistroPF_delete:
        db.session.delete(RegistroPF_delete)
        db.session.commit()
    else:
        flash('Registro no encontrado.', category='error')

    return redirect(url_for("MoneidAPP.registrosPF"))

@moneidAPP.route("/MoneidAPP/addUser", methods=['POST','GET'])
@login_required
@requires_permission("administrador")
def addUser():
    sucursal = Sucursales.query.all()
    rol = Rol.query.all()
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')
        #passwordV = request.form.get('passwordV')
        apellidoPAtEmpleado = request.form.get('apellidoPAtEmpleado')
        apellidoMatEmpleado = request.form.get('apellidoMatEmpleado')
        correoElectronico = request.form.get('correoElectronico')
        idSucursalesEmpleado = request.form.get("idSucursalEmpleado")
        idRolEmpleado = request.form.get('tipoRol')
        estadoEmpleado = "Activo"
        puesto = request.form.get('puesto')
        creado = datetime.utcnow()

        email_exists = Empleado.query.filter_by(correoElectronico=correoElectronico).first()
        username_exists = Empleado.query.filter_by(username=username).first()

        if email_exists:
            flash('El email utilizado ya esta registrado.', category='error')
        elif username_exists:
            flash('El nombre de usuario no esta disponible.', category='error')
        #elif password != passwordV:
        #    flash('Las contraseñas no coinciden!', category='error')
        elif len(username) < 3:
            flash('El nombre de usuario es muy corto.', category='error')
        elif len(password) < 6:
            flash('La contraseña debe tener al menos 6 caracteres.', category='error')
        elif len(correoElectronico) < 6:
            flash("El correo electrónico es invalido.", category='error')
        else:
            new_user = Empleado(
                username,
                apellidoPAtEmpleado,
                apellidoMatEmpleado,
                generate_password_hash(password, method='sha256'),
                correoElectronico,
                idSucursalesEmpleado,
                idRolEmpleado,
                estadoEmpleado,
                puesto,
                creado  # Ahora creado contiene la fecha y hora actual
            )

            db.session.add(new_user)
            db.session.commit()
            # Sirve para que inicie sesión de manera automatica al crear un usuario
            #login_user(new_user, remember=True)
            flash('¡Usuario creado!', category='success')
            return redirect(url_for('MoneidAPP.Users'))
    return render_template("dashboard/addUser.html", user=current_user, sucursal=sucursal, ROl=rol)

@moneidAPP.route("/MoneidAPP/update/<int:user_id>", methods=['GET', 'POST'])
@login_required
@requires_permission("administrador")
def editUser(user_id):
    user = db.session.query(Empleado).filter_by(id=user_id).first()

    if user is None:
        flash('Usuario no encontrado.', category='error')
        return redirect(url_for("MoneidAPP.Users"))

    sucursa = Sucursales.query.all()
    roles = Rol.query.all()

    if request.method == "POST":
        user.username = request.form.get('username')
        user.apellidoPAtEmpleado = request.form.get('apellidoPAtEmpleado')
        user.apellidoMatEmpleado = request.form.get('apellidoMatEmpleado')
        user.correoElectronico = request.form.get('correoElectronico')
        user.password = generate_password_hash(request.form.get("password"))
        user.idSucursalesEmpleado = request.form.get('idSucursalEmpleado')
        user.idRolEmpleado = request.form.get('tipoRol')
        user.puesto = request.form.get('puesto')

        db.session.commit()
        flash('Datos de usuario actualizados.', category='success')
        return redirect(url_for('MoneidAPP.Users'))
    
    return render_template('dashboard/updateUser.html', user=current_user, user_to_edit=user, sucursa=sucursa, roles=roles)


@moneidAPP.route("/MoneidAPP/eliminar/<string:id>")
@login_required
@requires_permission("administrador")
def deleteUser(id):
    
    user_to_delete = Empleado.query.get(id)

    if user_to_delete:
        db.session.delete(user_to_delete)
        db.session.commit()
    else:
        flash('Usuario no encontrado.', category='error')

    return redirect(url_for("MoneidAPP.Users"))
      
@moneidAPP.route("/MoneidAPP/perfil")
@login_required
def perfil():

    User =db.session.query(Empleado).all()

    sucursal_dict ={}
    direc_sucur = {}
    sucursal = db.session.query(Sucursales).all()
    for sucur in sucursal:
        sucursal_dict[sucur.id] = sucur.nombreSucursal
        direc_sucur[sucur.id] = sucur.direccion

    roles_dict = {}
    roles = db.session.query(Rol).all()
    for rol in roles:
        roles_dict[rol.idRol] = rol.tipoRol
    
    if current_user.is_authenticated:
        try:
            flash(MENSAJE_USER, category='success')
            return render_template('dashboard/perfil.html',direc_sucur=direc_sucur, user=current_user, User=User,roles_dict=roles_dict,sucursal_dict=sucursal_dict)
        except Exception as ex:
            return render_template('errores/error.html', mensaje=format(ex))
        else:
            return redirect(url_for('auth.login'))
        finally:
            pass




@moneidAPP.route("/MoneidAPP/Plazo-Fijo", methods=['POST', 'GET'])
@login_required
def CALplazoFijo():
    if request.method == 'POST':

        submit_type = request.form.get('submit_type', '')

        clientName = request.form['clientName']
        telefono = request.form['telefono']

        montoinicial = float(request.form['montoinicial'])

        selected_plazos = []
        if '6meses' in request.form:
            selected_plazos.append('6 meses')
        if '12meses' in request.form:
            selected_plazos.append('12 meses')
        if '24meses' in request.form:
            selected_plazos.append('24 meses')
        if '36meses' in request.form:
            selected_plazos.append('36 meses')

        plazos_data = {
            '6 meses': {'rendimiento': 0.1265, 'OInsti': 0.0217},
            '12 meses': {'rendimiento': 0.30, 'OInsti': 0.0435},
            '24 meses': {'rendimiento': 0.7207, 'OInsti': 0.0871},
            '36 meses': {'rendimiento': 1.3176, 'OInsti': 0.115}
        }

        selected_rendimientos = {}
        selected_OInsti = {}
        selected_totalRendimientos = {}

        for plazo in selected_plazos:
            selected_rendimientos[plazo] = plazos_data[plazo]['rendimiento'] * montoinicial
            selected_OInsti[plazo] = (plazos_data[plazo]['OInsti'] * montoinicial) + montoinicial
            selected_totalRendimientos[plazo] = montoinicial + selected_rendimientos[plazo]

        formatted_result_PF = {
            'clientName': clientName,
            'telefono': telefono,
            'montoinicial': format_currency(montoinicial),
            'OInsti': {plazo: format_currency(value) for plazo, value in selected_OInsti.items()},
            'totalRendimiento': {plazo: format_currency(value) for plazo, value in selected_totalRendimientos.items()},
            'rendimiento': {plazo: format_currency(value) for plazo, value in selected_rendimientos.items()}
        }
        print(formatted_result_PF)
        selected_plazos_data = {plazo: plazos_data[plazo] for plazo in selected_plazos}

        plt.figure(figsize=(18.5/2.54, 10.5/2.54))

        plazos = list(selected_plazos_data.keys())  # Usar solo los plazos seleccionados
        bar_width = 0.45  # Ancho de las barras
        spacing = 0.05

        # Crear un arreglo de posiciones para las barras agrupadas
        posiciones = np.arange(len(plazos))

        # Crear la gráfica de barras agrupadas
        for i, plazo in enumerate(plazos):
            plt.bar(posiciones[i] - bar_width/2 - spacing/2, [selected_OInsti[plazo]], width=bar_width, color='#A3A3A3', alpha=0.5, label='Otras Instituciones' if i == 0 else '', align='center')
            plt.bar(posiciones[i] + bar_width/2 + spacing/2, [selected_totalRendimientos[plazo]], width=bar_width, color='#D7B987', label='Moneid' if i == 0 and plazo != '6meses' else '', align='center')

        plt.xlabel('Plazo Fijo')
        plt.xticks(posiciones, plazos)
        ax = plt.gca()

        # Formatear los números en el eje y como moneda con el estilo $100,000.00
        formatter = ticker.StrMethodFormatter('${x:,.2f}')
        ax.yaxis.set_major_formatter(formatter)

        for i, plazo in enumerate(plazos):
            valor_otros = selected_OInsti[plazo]
            valor_moneid = selected_totalRendimientos[plazo]
            plt.text(posiciones[i] - bar_width/2 - spacing/2, valor_otros + 0.50, f'{format_currency(valor_otros)}', ha='center', va='bottom', fontsize=8, color='black')
            plt.text(posiciones[i] + bar_width/2 + spacing/2, valor_moneid + 0.50, f'{format_currency(valor_moneid)}', ha='center', va='bottom', fontsize=8, color='black')

        plt.legend()
        plt.tight_layout()
    
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        grafica_binaria = buffer.read()
        buffer.close()

        grafica_base64 = base64.b64encode(grafica_binaria).decode('utf-8')

        if submit_type == 'calculate_and_register':
            new_registro_PF = PlazoFijo(
                nombreCliente=clientName,
                telefono=telefono,
                montoinicial=formatted_result_PF['montoinicial'],
                idEmpleado=current_user.id,
                graficas=grafica_binaria,
            )
            if '6 meses' in formatted_result_PF['rendimiento']:
                new_registro_PF.rendimiento6 = formatted_result_PF['rendimiento']['6 meses']
                new_registro_PF.totalRendimiento6 = formatted_result_PF['totalRendimiento']['6 meses']
                new_registro_PF.OInsti6 = formatted_result_PF['OInsti']['6 meses']

            if '12 meses' in formatted_result_PF['rendimiento']:
                new_registro_PF.rendimiento12 = formatted_result_PF['rendimiento']['12 meses']
                new_registro_PF.totalRendimiento12 = formatted_result_PF['totalRendimiento']['12 meses']
                new_registro_PF.OInsti12 = formatted_result_PF['OInsti']['12 meses']

            if '24 meses' in formatted_result_PF['rendimiento']:
                new_registro_PF.rendimiento24 = formatted_result_PF['rendimiento']['24 meses']
                new_registro_PF.totalRendimiento24 = formatted_result_PF['totalRendimiento']['24 meses']
                new_registro_PF.OInsti24 = formatted_result_PF['OInsti']['24 meses']

            if '36 meses' in formatted_result_PF['rendimiento']:
                new_registro_PF.rendimiento36 = formatted_result_PF['rendimiento']['36 meses']
                new_registro_PF.totalRendimiento36 = formatted_result_PF['totalRendimiento']['36 meses']
                new_registro_PF.OInsti36 = formatted_result_PF['OInsti']['36 meses']


            db.session.add(new_registro_PF)
            db.session.commit()

        return render_template('dashboard/plazoF.html',grafica_base64=grafica_base64, resul= formatted_result_PF, user=current_user, selected_plazos=selected_plazos)
    else:
        return render_template('dashboard/plazoF.html', resul=None)

@moneidAPP.route("/MoneidAPP/pdfPlazoFijo/<int:idPlazoFijo>", methods=['POST', 'GET'])
@login_required
def pdfPlazoFijo(idPlazoFijo):

    plazoPDF = PlazoFijo.query.get_or_404(idPlazoFijo)

    template_path = os.path.join(moneidAPP.root_path, '..', 'templates', 'docs', 'template_plazoFijo.docx')
    template = DocxTemplate(template_path)

    image_blob = plazoPDF.graficas
    image_stream = io.BytesIO(image_blob)

    #sucursal = db.session.query(Sucursales).all()
    idEmpleado = plazoPDF.idEmpleado
    if idEmpleado:
        empleado_info = Empleado.query.get(idEmpleado)
    if empleado_info:
        nombre_empleado = empleado_info.username
        apellido_empleado = empleado_info.apellidoPAtEmpleado
        puesto = empleado_info.puesto
    
    selected_plazos = []
    if plazoPDF.rendimiento6 is not None:
        selected_plazos.append('Plazo fijo – 6 meses')
    if plazoPDF.rendimiento12 is not None:
        selected_plazos.append('Plazo fijo – 12 meses')
    if plazoPDF.rendimiento24 is not None:
        selected_plazos.append('Plazo fijo – 24 meses')
    if plazoPDF.rendimiento36 is not None:
        selected_plazos.append('Plazo fijo – 36 meses')

    resultados = {
        'rendimiento': {
            'Plazo fijo – 6 meses': plazoPDF.rendimiento6,
            'Plazo fijo – 12 meses': plazoPDF.rendimiento12,
            'Plazo fijo – 24 meses': plazoPDF.rendimiento24,
            'Plazo fijo – 36 meses': plazoPDF.rendimiento36,
            # ... otros valores ...
        },
        'totalRendimiento': {
            'Plazo fijo – 6 meses': plazoPDF.totalRendimiento6,
            'Plazo fijo – 12 meses': plazoPDF.totalRendimiento12,
            'Plazo fijo – 24 meses': plazoPDF.totalRendimiento24,
            'Plazo fijo – 36 meses': plazoPDF.totalRendimiento36,
            # ... otros valores ...
        },
        'OInsti': {
            'Plazo fijo – 6 meses': plazoPDF.OInsti6,
            'Plazo fijo – 12 meses': plazoPDF.OInsti12,
            'Plazo fijo – 24 meses': plazoPDF.OInsti24,
            'Plazo fijo – 36 meses': plazoPDF.OInsti36,
            # ... otros valores ...
        },
        'tasa': {
            'Plazo fijo – 6 meses': '12.65%',
            'Plazo fijo – 12 meses': '30.00%',
            'Plazo fijo – 24 meses': '72.00%',
            'Plazo fijo – 36 meses': '131.76%',
        }
    }

    context = {
        'nombreCliente': plazoPDF.nombreCliente,
        'telefono': plazoPDF.telefono,
        'montoinicial': plazoPDF.montoinicial,
        'graficas': InlineImage(template, image_stream),
        'nombreEmpleado': nombre_empleado,
        'apellidoEmpleado': apellido_empleado,
        'puesto': puesto,
        'selected_plazos':selected_plazos,
        'resul':resultados
        }
    template.render(context)
 
    nameFile = f'PlazoFijo_{plazoPDF.nombreCliente}.docx'

    pdf_bytes_io = BytesIO()
    template.save(pdf_bytes_io)
    pdf_bytes = pdf_bytes_io.getvalue()

    if pdf_bytes:
        # Update the 'pdfPF' column in the 'PlazoFijo' table with the PDF data
        plazoPDF.pdfPF = pdf_bytes
        db.session.commit()

        # Serve the PDF to the user for download
        response = send_file(BytesIO(pdf_bytes), as_attachment=True, download_name=nameFile)
        response.headers["Content-Type"] = "application/pdf"
        return response
    else:
        return "Error"


@moneidAPP.route("/MoneidAPP/Rendimiento-Programado", methods=['POST', 'GET'])
@login_required
def rendimientoPro():
    if request.method =='POST':

        submit_type = request.form.get('submit_type', '')        
    
        clientName = request.form['clientName']
        telefono = request.form['telefono']
        montoInicial = float(request.form['inversion'])

        gananciaMensual = montoInicial * 0.2025 / 12
        gananciaAnual = gananciaMensual * 12
        inversionPlazoFijo = montoInicial * 0.30
        totalRendimientoProgramado = gananciaAnual + montoInicial
        totalPlazoFijo = inversionPlazoFijo + montoInicial
        diferencia = inversionPlazoFijo - gananciaAnual

        OInstiRP = montoInicial * 0.0029
        totalInsti = (OInstiRP * 12) + montoInicial

        formatted_montoinicial = format_currency(montoInicial)
        formatted_gananciaMensual = format_currency(gananciaMensual)
        formatted_gananciaAnual = format_currency(gananciaAnual)
        formatted_inversionPlazoFijo = format_currency(inversionPlazoFijo)
        formatted_totalRendimientoProgramado = format_currency(totalRendimientoProgramado)
        formatted_totalPlazoFijo = format_currency(totalPlazoFijo)
        formatted_diferencia = format_currency(diferencia)
        formatted_OInstiRP = format_currency(OInstiRP)
        formatted_totalInsti = format_currency(totalInsti)

        env = Environment()
        env.filters['format_currency'] = format_currency 

        formatted_result = {
            'clientName': clientName,
            'telefono': telefono,
            'gananciaMensual': formatted_gananciaMensual,
            'gananciaAnual': formatted_gananciaAnual,
            'inversionPlazoFijo': formatted_inversionPlazoFijo,
            'totalRendimientoProgramado': formatted_totalRendimientoProgramado,
            'totalPlazoFijo': formatted_totalPlazoFijo,
            'diferencia': formatted_diferencia,
            'montoInicial': formatted_montoinicial,
            'OInstiRP': formatted_OInstiRP,
            'totalInsti': formatted_totalInsti   
        }

        plt.figure(figsize=(18.5/2.54, 12/2.54))
        plazos = ['Rendimiento Programado Mensual']
        bar_width = 0.35  # Ancho de las barras
        spacing = 0.15

        # Crear un arreglo de posiciones para las barras agrupadas
        posiciones = np.arange(len(plazos))

        # Crear la gráfica de barras agrupadas
        plt.bar(posiciones - bar_width/2 - spacing/2, [OInstiRP], width=bar_width, color='#A3A3A3', alpha=0.5, label='Otras Instituciones')
        plt.bar(posiciones + bar_width/2 + spacing/2, [gananciaMensual], width=bar_width, color='#D7B987', label='Moneid')

        plt.xlabel('')
        plt.xticks(posiciones, plazos)
        ax = plt.gca()

        # Formatear los números en el eje y como moneda con el estilo $100,000.00
        formatter = ticker.StrMethodFormatter('${x:,.2f}')
        ax.yaxis.set_major_formatter(formatter)

        for i, valor in enumerate([OInstiRP]):
            plt.text(posiciones[i] - bar_width/2 - spacing/2, valor + 0.50, f'${valor:,.2f}', ha='center', va='bottom', fontsize=9, color='black')

        for i, valor in enumerate([gananciaMensual]):
            plt.text(posiciones[i] + bar_width/2 + spacing/2, valor + 0.50, f'${valor:,.2f}', ha='center', va='bottom', fontsize=9, color='black')


        plt.legend()
        plt.tight_layout()

       
        
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        grafica_binariaRP = buffer.read()
        buffer.close()

        grafica_base64rp = base64.b64encode(grafica_binariaRP).decode('utf-8')

        formato_moneda = formatted_result

        if submit_type == 'calculate_and_register':
            new_registro_RENPRO = RendimientoPro(
                nombreCliente=clientName,
                telefono=telefono,
                montoInicial=formato_moneda['montoInicial'],
                gananciaMensual=formato_moneda['gananciaMensual'],
                gananciaAnual=formato_moneda['gananciaAnual'],
                inversionPlazoFijo=formato_moneda['inversionPlazoFijo'],
                totalRendimientoProgramado=formato_moneda['totalRendimientoProgramado'],
                totalPlazoFijo=formato_moneda['totalPlazoFijo'],
                diferencia=formato_moneda['diferencia'],
                OInstiRP=formato_moneda['OInstiRP'],
                totalInsti=formato_moneda['totalInsti'],
                graficasRP= grafica_binariaRP,
                idEmpleado=current_user.id
            )

            db.session.add(new_registro_RENPRO)
            db.session.commit()
        return render_template('dashboard/rendimientoP.html', resultado= formatted_result, user=current_user, grafica_base64rp=grafica_base64rp) 
    else:
        return render_template('dashboard/rendimientoP.html', resultado=None)

@moneidAPP.route("/MoneidAPP/pdfRenPro/<int:idRendimientoP>", methods=['POST', 'GET'])
@login_required
def pdfRenPro(idRendimientoP):

    RenPropdf = RendimientoPro.query.get_or_404(idRendimientoP)

    template_path = os.path.join(moneidAPP.root_path, '..', 'templates', 'docs', 'template_rendimientoPro.docx')
    template = DocxTemplate(template_path)

    image_blob = RenPropdf.graficasRP
    image_stream = io.BytesIO(image_blob)

    context = {
        'nombreCliente': RenPropdf.nombreCliente,
        'telefono': RenPropdf.telefono,
        'montoinicial': RenPropdf.montoInicial,
        'gananciaMensual': RenPropdf.gananciaMensual,
        'totalRendimientoProgramado': RenPropdf.totalRendimientoProgramado,
        'OInstiRP': RenPropdf.OInstiRP,
        'totalInsti': RenPropdf.totalInsti,
        'graficasRP': InlineImage(template, image_stream)

    }

    template.render(context)

    nameFile = f'PlazoFijo_{RenPropdf.nombreCliente}.docx'

    pdf_bytes_io = BytesIO()
    template.save(pdf_bytes_io)
    pdf_bytes = pdf_bytes_io.getvalue()

    if pdf_bytes:
        # Update the 'pdfPF' column in the 'PlazoFijo' table with the PDF data
        RenPropdf.pdfRP = pdf_bytes
        db.session.commit()

        # Serve the PDF to the user for download
        response = send_file(BytesIO(pdf_bytes), as_attachment=True, download_name=nameFile)
        response.headers["Content-Type"] = "application/pdf"
        return response
    else:
        return "Error"
    
    #nameFile = f'RendimientoProgramado_{RenPropdf.nombreCliente}.docx'
    #pdf_path = os.path.join(moneidAPP.root_path, 'pdfs', nameFile)
    #template.save(pdf_path)
    #return send_file(pdf_path, as_attachment=True)


@moneidAPP.route("/MoneidAPP/aportacion", methods=['GET', 'POST'])
@login_required
def aportacion():
    if request.method == 'POST':

        submit_type = request.form.get('submit_type', '')        
        telefono = request.form['telefono']

        montoInicial = float(request.form['montoInicial'])
        aporteInicial = float(request.form['aporte'])
        plazo = request.form['validacionPlazo']
        interesAnual = float(request.form['interesAnual'])
        clientName = request.form['clientName']
        fechaInicioContrato_str = request.form['fechaInicioContrato']
        fechaAportacion_str = request.form['fechaAportacion']

        fechaAportacion1 = datetime.strptime(fechaAportacion_str, '%Y-%m-%d')
        fechaInicio = datetime.strptime(fechaInicioContrato_str, '%Y-%m-%d')
      
        duracionDelContrato = 0
        interesDiario = 0
        RendimientoGanadoPlazo = 0
        TotalRendimientoPlazo = 0
        interesBruto = 0
        interesNeto = 0
        interesGanado = 0
        totalAportacion = 0
        capitaltotal = 0
        rendimientototal = 0
        saldototal = 0

        gastosOperacion = 3

        diaDeposito = abs((fechaAportacion1 - fechaInicio).days)

        if plazo == '12 meses':
            OIRendimientoTotal = (montoInicial * 0.0435) + montoInicial
            OIaportacionTotal = (aporteInicial * 0.0435) + aporteInicial
            OIsaldototal = OIRendimientoTotal + OIaportacionTotal

            duracionDelContrato = 365
            interesDiario = interesAnual / duracionDelContrato
            RendimientoGanadoPlazo = (interesAnual * montoInicial) / 100
            TotalRendimientoPlazo = montoInicial + RendimientoGanadoPlazo

            interesBruto = (duracionDelContrato - diaDeposito + 1) * interesDiario
            interesNeto = interesBruto - gastosOperacion
            interesGanado = (interesNeto * aporteInicial) / 100
            totalAportacion = aporteInicial + interesGanado

            capitaltotal = montoInicial + aporteInicial
            rendimientototal = RendimientoGanadoPlazo + interesGanado
            saldototal = TotalRendimientoPlazo + totalAportacion


        else:
         if plazo == '24 meses':
            OIRendimientoTotal = (montoInicial * 0.0871) + montoInicial
            OIaportacionTotal = (aporteInicial * 0.0871) + aporteInicial
            OIsaldototal = OIRendimientoTotal + OIaportacionTotal

            duracionDelContrato = 730
            interesDiario = interesAnual / duracionDelContrato
            RendimientoGanadoPlazo = (interesAnual * montoInicial) / 100
            TotalRendimientoPlazo = montoInicial + RendimientoGanadoPlazo

            interesBruto = (duracionDelContrato - diaDeposito + 1) * interesDiario
            interesNeto = interesBruto - gastosOperacion
            interesGanado = (interesNeto * aporteInicial) / 100
            totalAportacion = aporteInicial + interesGanado

            capitaltotal = montoInicial + aporteInicial
            rendimientototal = RendimientoGanadoPlazo + interesGanado
            saldototal = TotalRendimientoPlazo + totalAportacion

            if diaDeposito >=181:
                interesBi = interesAnual - 6.5
                interesDiario = interesBi / duracionDelContrato
                RendimientoGanadoPlazo = (interesAnual * montoInicial) / 100
                TotalRendimientoPlazo = montoInicial + RendimientoGanadoPlazo

                interesBruto = (duracionDelContrato - diaDeposito + 1) * interesDiario
                interesNeto = interesBruto - gastosOperacion
                interesGanado = (interesNeto * aporteInicial) / 100
                totalAportacion = aporteInicial + interesGanado

                capitaltotal = montoInicial + aporteInicial
                rendimientototal = RendimientoGanadoPlazo + interesGanado
                saldototal = TotalRendimientoPlazo + totalAportacion

            if diaDeposito >= 366:    
                interesBi = interesAnual - 12
                interesDiario = interesBi / duracionDelContrato
                RendimientoGanadoPlazo = (interesAnual * montoInicial) / 100
                TotalRendimientoPlazo = montoInicial + RendimientoGanadoPlazo

                interesBruto = (duracionDelContrato - diaDeposito + 1) * interesDiario
                interesNeto = interesBruto - gastosOperacion
                interesGanado = (interesNeto * aporteInicial) / 100
                totalAportacion = aporteInicial + interesGanado 

                capitaltotal = montoInicial + aporteInicial
                rendimientototal = RendimientoGanadoPlazo + interesGanado
                saldototal = TotalRendimientoPlazo + totalAportacion
                          
         else:
             if plazo == '36 meses':
                OIRendimientoTotal = (montoInicial * 0.115) + montoInicial
                OIaportacionTotal = (aporteInicial * 0.115) + aporteInicial
                OIsaldototal = OIRendimientoTotal + OIaportacionTotal

                duracionDelContrato = 1095
                interesDiario = interesAnual / duracionDelContrato
                RendimientoGanadoPlazo = (interesAnual * montoInicial) / 100
                TotalRendimientoPlazo = montoInicial + RendimientoGanadoPlazo

                interesBruto = (duracionDelContrato - diaDeposito + 1) * interesDiario
                interesNeto = interesBruto - gastosOperacion
                interesGanado = (interesNeto * aporteInicial) / 100
                totalAportacion = aporteInicial + interesGanado

                capitaltotal = montoInicial + aporteInicial
                rendimientototal = RendimientoGanadoPlazo + interesGanado
                saldototal = TotalRendimientoPlazo + totalAportacion

                if diaDeposito >=181:
                    interesTri = interesAnual - 23
                    interesDiario = interesTri / duracionDelContrato
                    RendimientoGanadoPlazo = (interesAnual * montoInicial) / 100
                    TotalRendimientoPlazo = montoInicial + RendimientoGanadoPlazo

                    interesBruto = (duracionDelContrato - diaDeposito + 1) * interesDiario
                    interesNeto = interesBruto - gastosOperacion
                    interesGanado = (interesNeto * aporteInicial) / 100
                    totalAportacion = aporteInicial + interesGanado

                    capitaltotal = montoInicial + aporteInicial
                    rendimientototal = RendimientoGanadoPlazo + interesGanado
                    saldototal = TotalRendimientoPlazo + totalAportacion

                if diaDeposito >= 366:
                    interesTri = interesAnual - 44
                    interesDiario = interesTri / duracionDelContrato
                    RendimientoGanadoPlazo = (interesAnual * montoInicial) / 100
                    TotalRendimientoPlazo = montoInicial + RendimientoGanadoPlazo

                    interesBruto = (duracionDelContrato - diaDeposito + 1) * interesDiario
                    interesNeto = interesBruto - gastosOperacion
                    interesGanado = (interesNeto * aporteInicial) / 100
                    totalAportacion = aporteInicial + interesGanado

                    capitaltotal = montoInicial + aporteInicial
                    rendimientototal = RendimientoGanadoPlazo + interesGanado
                    saldototal = TotalRendimientoPlazo + totalAportacion


        env = Environment()
        env.filters['format_currency'] = format_currency 

        formatted_result = {
            'aporteInicial': format_currency(aporteInicial),
            'fechaInicio': fechaInicio.strftime('%d/%m/%Y'),
            'fechaAportacion1': fechaAportacion1.strftime('%d/%m/%Y'),
            'interesNeto': "{:.3f}%".format(interesNeto),
            'interesGanado': format_currency(interesGanado),
            'totalAportacion': format_currency(totalAportacion),
            'diaDeposito': diaDeposito,
            'interesAnual': "{:.3f}%".format(interesAnual),
            'montoInicial': format_currency(montoInicial),
            'TotalRendimientoPlazo': format_currency(TotalRendimientoPlazo),
            'RendimientoGanadoPlazo': format_currency(RendimientoGanadoPlazo),
            'capitaltotal': format_currency(capitaltotal),
            'rendimientototal': format_currency(rendimientototal),
            'saldototal': format_currency(saldototal),
            'plazo': plazo,
            'clientName': clientName,
            'OIRendimientoTotal': format_currency(OIRendimientoTotal),
            'OIaportacionTotal': format_currency(OIaportacionTotal),
            'OIsaldototal': format_currency(OIsaldototal)
        }

        plt.figure(figsize=(18.5/2.54, 12/2.54))
        plazos = ['Inversion inicial', 'Aportacion', 'Total']
        bar_width = 0.40  # Ancho de las barras
        spacing = 0.05

        # Crear un arreglo de posiciones para las barras agrupadas
        posiciones = np.arange(len(plazos))

        # Crear la gráfica de barras agrupadas
        plt.bar(posiciones - bar_width/2 - spacing/2, [OIRendimientoTotal, OIaportacionTotal, OIsaldototal], width=bar_width, color='#A3A3A3', alpha=0.5, label='Otras Instituciones')
        plt.bar(posiciones + bar_width/2 + spacing/2, [TotalRendimientoPlazo, totalAportacion, saldototal], width=bar_width, color='#D7B987', label='MONEID')
        plt.xlabel('')
        plt.xticks(posiciones, plazos)
        ax = plt.gca()

        # Formatear los números en el eje y como moneda con el estilo $100,000.00
        formatter = ticker.StrMethodFormatter('${x:,.2f}')
        ax.yaxis.set_major_formatter(formatter)

        for i, valor in enumerate([OIRendimientoTotal, OIaportacionTotal, OIsaldototal]):
            plt.text(posiciones[i] - bar_width/2 - spacing/2, valor + 1000, f'${valor:,.2f}', ha='center', va='bottom', fontsize=9, color='black')

        for i, valor in enumerate([TotalRendimientoPlazo, totalAportacion, saldototal]):
            plt.text(posiciones[i] + bar_width/2 + spacing/2, valor + 1000, f'${valor:,.2f}', ha='center', va='bottom', fontsize=9, color='black')


        plt.legend()
        plt.tight_layout()

       
        
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        grafica_binariaAPOR = buffer.read()
        buffer.close()

        grafica_base64apor = base64.b64encode(grafica_binariaAPOR).decode('utf-8')


        formatted_montoInicial = format_currency(montoInicial)
        formatted_aporteInicial = format_currency(aporteInicial)
        formatted_interesGanado = format_currency(interesGanado)
        formatted_totalAportacion = format_currency(totalAportacion)
        formatted_TotalRendimientoPlazo = format_currency(TotalRendimientoPlazo)
        formatted_RendimientoGanadoPlazo = format_currency(RendimientoGanadoPlazo)
        formatted_capitaltotal = format_currency(capitaltotal)
        formatted_rendimientototal = format_currency(rendimientototal)
        formatted_saldototal = format_currency(saldototal)
        formatted_OIRendimientoTotal = format_currency(OIRendimientoTotal)
        formatted_OIaportacionTotal = format_currency(OIaportacionTotal)
        formatted_OIsaldototal = format_currency(OIsaldototal)

        if submit_type == 'calculate_and_register':
            new_aportacion = Aportacion(
                telefono=telefono,
                montoInicial=formatted_montoInicial,
                aporteInicial=formatted_aporteInicial,
                plazo=plazo,
                interesAnual="{:.3f}%".format(interesAnual),
                nombreCliente=clientName,
                fechaInicioContrato=fechaInicio,
                fechaAportacion=fechaAportacion1,
                interesDiario=interesDiario,
                interesBruto=interesBruto,
                interesNeto="{:.3f}%".format(interesNeto),
                interesGanado=formatted_interesGanado,
                totalAportacion=formatted_totalAportacion,
                diaDeposito=diaDeposito,
                TotalRendimientoPlazo=formatted_TotalRendimientoPlazo,
                RendimientoGanadoPlazo=formatted_RendimientoGanadoPlazo,
                capitaltotal=formatted_capitaltotal,
                rendimientototal=formatted_rendimientototal,
                saldototal=formatted_saldototal,
                idEmpleado=current_user.id,
                graficasAPOR= grafica_binariaAPOR,
                OIRendimientoTotal=formatted_OIRendimientoTotal,
                OIaportacionTotal=formatted_OIaportacionTotal,
                OIsaldototal=formatted_OIsaldototal
                )
            
            db.session.add(new_aportacion)
            db.session.commit()
        
        

        return render_template('dashboard/aportacion.html', result= formatted_result, grafica_base64apor=grafica_base64apor) 
    else:
        return render_template('dashboard/aportacion.html', result=None)
    


@moneidAPP.route("/MoneidAPP/pdfAPOR/<int:idAportacion>", methods=['POST', 'GET'])
@login_required
def pdfAPOR(idAportacion):

    aporta = Aportacion.query.get_or_404(idAportacion)

    template_path = os.path.join(moneidAPP.root_path, '..', 'templates', 'docs', 'template_aportacion.docx')
    template = DocxTemplate(template_path)

    image_blob = aporta.graficasAPOR
    image_stream = io.BytesIO(image_blob)

    context = {
        'nombreCliente': aporta.nombreCliente,
        'telefono': aporta.telefono,
        'aporteInicial': aporta.aporteInicial,
        'fechaInicio': aporta.fechaInicioContrato,
        'fechaAportacion1': aporta.fechaAportacion,
        'interesNeto': aporta.interesNeto,
        'interesGanado': aporta.interesGanado,
        'totalAportacion': aporta.totalAportacion,
        'diaDeposito': aporta.diaDeposito,
        'interesAnual': aporta.interesAnual,
        'montoInicial': aporta.montoInicial,
        'TotalRendimientoPlazo': aporta.TotalRendimientoPlazo,
        'RendimientoGanadoPlazo': aporta.RendimientoGanadoPlazo,
        'capitaltotal': aporta.capitaltotal,
        'rendimientototal': aporta.rendimientototal,
        'saldototal': aporta.saldototal,
        'plazo': aporta.plazo,
        'graficasAPOR': InlineImage(template, image_stream),
        'OIRendimientoTotal': aporta.OIRendimientoTotal,
        'OIaportacionTotal': aporta.OIaportacionTotal,
        'OIsaldototal': aporta.OIsaldototal
    }

    template.render(context)

    nameFile = f'PlazoFijo_{aporta.nombreCliente}.docx'

    pdf_bytes_io = BytesIO()
    template.save(pdf_bytes_io)
    pdf_bytes = pdf_bytes_io.getvalue()

    if pdf_bytes:
        # Update the 'pdfPF' column in the 'PlazoFijo' table with the PDF data
        aporta.pdfAPOR = pdf_bytes
        db.session.commit()

        # Serve the PDF to the user for download
        response = send_file(BytesIO(pdf_bytes), as_attachment=True, download_name=nameFile)
        response.headers["Content-Type"] = "application/pdf"
        return response
    else:
        return "Error"

    #nameFile = f'Aportacion_{aporta.nombreCliente}.docx'    
    #pdf_path = os.path.join(moneidAPP.root_path, 'pdfs', nameFile)
    #template.save(pdf_path)
    #return send_file(pdf_path, as_attachment=True)