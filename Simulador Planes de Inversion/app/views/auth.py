from flask import Flask, Blueprint, flash, g, redirect, render_template, request, session, url_for, jsonify
from werkzeug.security import check_password_hash, generate_password_hash

import functools
from app.mensajeflash import *

from app.models.empleado import Empleado


from flask_login import login_user, logout_user, login_required, current_user
from app import db

auth = Blueprint("auth", __name__, url_prefix="/auth")

#@auth.route("/signup", methods=["GET", "POST"])
#def signup():
    


@auth.route("/login", methods=['GET', 'POST'])
def login():

    if request.method =='POST':
        correoElectronico = request.form.get("correoElectronico")
        password = request.form.get("password")

        user = Empleado.query.filter_by(correoElectronico=correoElectronico).first()
        if user:
            if check_password_hash(user.password, password):
                flash(LOGGED_IN, category='success')
                login_user(user, remember=True)
                return redirect(url_for('MoneidAPP.dashboard'))
            else:
                flash(LOGIN_PASSINVALIDA, category='error')
        else:
            flash(LOGIN_USERINVALIDO, category='error')

    flash(MENSAJE_BIENVENIDA, category='success')       
    return render_template("auth/login.html", user=current_user)



@auth.route('/logout')
#@login_required
def logout():
    logout_user()
    flash(LOGOUT, category='success')
    return redirect(url_for('MoneidAPP.index'))