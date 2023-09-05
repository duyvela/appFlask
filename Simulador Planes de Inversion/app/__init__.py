from flask import Flask, Blueprint, flash, g, redirect, render_template, request, session, url_for, jsonify
from flask_wtf.csrf import CSRFProtect
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_manager



# Crea instancia Flask app
app = Flask(__name__)

# carga configuracion
app.config.from_object("config.DevelopmentConfig")

# Inicia CSRF protection
csrf = CSRFProtect()
csrf.init_app(app)

# Inicia la database
db = SQLAlchemy(app)

# Inicializa el login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

# Registra blueprints
from app.views.auth import auth
from app.views.moneid import moneidAPP
app.register_blueprint(auth)
app.register_blueprint(moneidAPP)

# Import los models despues de inicializar la base de datos
from app.models.empleado import Empleado

# Crea las tablas de la base de datos
with app.app_context():
    db.create_all()

# Implement the user loader function for Flask-Login
@login_manager.user_loader 
def load_user(id):
    return Empleado.query.get(id)

# Excepciones u errores
def pagina_no_encontrada(error):
    return render_template("errores/404.html", mensaje=format(Exception)), 404

def pagina_no_autorizada(error):
    return redirect(url_for("auth.login", mensaje=format(Exception)), 401)

app.register_error_handler(401, pagina_no_autorizada)

app.register_error_handler(404, pagina_no_encontrada)