from app import db
from datetime import datetime
import pytz

class PlazoFijo(db.Model):
    __tablename__ = "plazofijo"
    idPlazoFijo = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombreCliente = db.Column(db.String(30), nullable=False)
    telefono = db.Column(db.String(20), nullable=False)
    montoinicial = db.Column(db.String(50), nullable=False)
    rendimiento6 = db.Column(db.String(50))
    rendimiento12 = db.Column(db.String(50))
    rendimiento24 = db.Column(db.String(50))
    rendimiento36 = db.Column(db.String(50))
    totalRendimiento6 = db.Column(db.String(50))
    totalRendimiento12 = db.Column(db.String(50))
    totalRendimiento24 = db.Column(db.String(50))
    totalRendimiento36 = db.Column(db.String(50))
    idEmpleado = db.Column(db.Integer, db.ForeignKey("empleados.id"), nullable=False)
    fechaRegistro = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    OInsti6 = db.Column(db.String(45))
    OInsti12 = db.Column(db.String(45))
    OInsti24 = db.Column(db.String(45))
    OInsti36 = db.Column(db.String(45))

    graficas = db.Column(db.LargeBinary)

    empleado = db.relationship('Empleado', foreign_keys=[idEmpleado])

    def  __repr__(self):
        return f"PlazoFijo(idPlazoFijo={self.idPlazoFijo}, nombreCliente='{self.nombreCliente}', empleado_id={self.idEmpleado})"

    def get_current_datetime_central(self):
        central_timezone = pytz.timezone('America/Mexico_City')
        return datetime.now(central_timezone)