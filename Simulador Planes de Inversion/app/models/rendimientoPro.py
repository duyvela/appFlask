from app import db
from datetime import datetime
import pytz

class RendimientoPro(db.Model):
    __tablename__ ="rendimientoprogramado"
    idRendimientoP = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombreCliente = db.Column(db.String(30), nullable=False)
    telefono = db.Column(db.String(20), nullable=False)
    montoInicial = db.Column(db.String(20), nullable=False)
    gananciaMensual = db.Column(db.String(20), nullable= False)
    OInstiRP = db.Column(db.String(20), nullable= False)
    totalInsti = db.Column(db.String(20), nullable= False)
    gananciaAnual = db.Column(db.String(20), nullable=False)
    inversionPlazoFijo = db.Column(db.String(20), nullable=False)
    totalRendimientoProgramado = db.Column(db.String(20), nullable=False)
    totalPlazoFijo = db.Column(db.String(20), nullable=False)
    diferencia = db.Column(db.String(20), nullable=False)
    idEmpleado = db.Column(db.Integer, db.ForeignKey("empleados.id"), nullable=False)
    fechaRegistro = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    graficasRP = db.Column(db.LargeBinary)
    pdfRP = db.Column(db.LargeBinary)


    empleado = db.Relationship('Empleado', foreign_keys=[idEmpleado])

    def __repr__(self):
        return f"RendimientoPRO(idRendimientoP={self.idRendimientoP}, nombreCliente='{self.nombreCliente}', empleado_id={self.idEmpleado}, fechaRegistro = {self.get_current_datetime_central()})"
    
    def get_current_datetime_central(self):
        central_timezone = pytz.timezone('America/Mexico_City')
        return datetime.now(central_timezone)