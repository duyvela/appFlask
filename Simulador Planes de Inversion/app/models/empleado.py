from app import db
from datetime import datetime
from flask_login import UserMixin, AnonymousUserMixin
from app.models.rol import Rol
import pytz

class Empleado(UserMixin, AnonymousUserMixin, db.Model):
    __tablename__ = "empleados"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    username = db.Column(db.String(20), nullable=False)
    apellidoPAtEmpleado = db.Column(db.String(25))
    apellidoMatEmpleado = db.Column(db.String(25))
    password = db.Column(db.Text)
    correoElectronico = db.Column(db.String(150), unique=True, nullable=False)
    estadoEmpleado = db.Column(db.String(8))
    
    idRolEmpleado = db.Column(db.Integer, db.ForeignKey("roles.idRol"))
    idSucursalesEmpleado = db.Column(db.Integer, db.ForeignKey("sucursales.id"))
    creado = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    puesto = db.Column(db.String(100), nullable=True)

    rol = db.relationship('Rol', foreign_keys=[idRolEmpleado])
    sucursal = db.relationship('Sucursales', foreign_keys=[idSucursalesEmpleado])


    def __init__(self, username, apellidoPAtEmpleado, apellidoMatEmpleado, password, correoElectronico, idSucursalesEmpleado, idRolEmpleado, estadoEmpleado,puesto, creado ) -> None:
        self.username = username
        self.apellidoPAtEmpleado = apellidoPAtEmpleado
        self.apellidoMatEmpleado = apellidoMatEmpleado
        self.password = password
        self.correoElectronico = correoElectronico
        self.estadoEmpleado = estadoEmpleado
        self.creado = creado
        self.idSucursalesEmpleado = idSucursalesEmpleado
        self.idRolEmpleado = idRolEmpleado
        self.puesto = puesto
        
    def has_permission(self, permission_name):
        #print(f"Tipo de rol del usuario: {self.rol.tipoRol}")
        #print(f"Permiso requerido: {permission_name}")
        return self.rol.tipoRol == permission_name


    def __repr__(self) -> str:
        return f"User: {self.username} {self.correoElectronico}"
    
    def get_current_datetime_central(self):
        central_timezone = pytz.timezone('America/Mexico_City')
        return datetime.now(central_timezone)