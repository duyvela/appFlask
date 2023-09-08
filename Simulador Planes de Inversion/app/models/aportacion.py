from app import db
from datetime import datetime
import pytz

class Aportacion(db.Model):
    __tablename__ = "aportacion"
    idAportacion = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombreCliente = db.Column(db.String(30), nullable=False)
    telefono = db.Column(db.String(20), nullable=False)
    montoInicial = db.Column(db.String(50), nullable=False)
    aporteInicial = db.Column(db.String(50), nullable=False)
    plazo = db.Column(db.String(20), nullable=False)
    interesAnual = db.Column(db.String(50), nullable=False)
    fechaInicioContrato = db.Column(db.Date, nullable=False)
    fechaAportacion = db.Column(db.Date, nullable=False)
    diaDeposito = db.Column(db.Integer, nullable=False)
    interesDiario = db.Column(db.String(10), nullable=False)
    RendimientoGanadoPlazo = db.Column(db.String(50), nullable=False)
    TotalRendimientoPlazo = db.Column(db.String(50), nullable=False)
    interesBruto = db.Column(db.String(50), nullable=False)
    interesNeto = db.Column(db.String(50), nullable=False)
    interesGanado = db.Column(db.String(50), nullable=False)
    totalAportacion = db.Column(db.String(50), nullable=False)
    capitaltotal = db.Column(db.String(50), nullable=False)
    rendimientototal = db.Column(db.String(50), nullable=False)
    saldototal = db.Column(db.String(50), nullable=False)
    fechaRegistro = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    idEmpleado = db.Column(db.Integer, db.ForeignKey("empleados.id"), nullable=False)
    graficasAPOR = db.Column(db.LargeBinary)
    OIRendimientoTotal = db.Column(db.String(45), nullable=False)
    OIaportacionTotal = db.Column(db.String(45), nullable=False)
    OIsaldototal = db.Column(db.String(45), nullable=False)

    pdfAPOR = db.Column(db.LargeBinary)


    empleado = db.relationship('Empleado', foreign_keys=[idEmpleado])

    def __repr__(self):
        return f"Aportacion(idAportacion={self.idAportacion}, nombreCliente='{self.nombreCliente}, empleado_id={self.idEmpleado})"
    
    def get_current_datetime_central(self):
        central_timezone = pytz.timezone('America/Mexico_City')
        return datetime.now(central_timezone)