from app import db

class Sucursales(db.Model):
    __tablename__ = "sucursales"
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True, nullable=False)
    nombreSucursal = db.Column(db.String(40))
    direccion = db.Column(db.String(100))
    telefono = db.Column(db.String(25))

    def __init__(self, nombreSucursal, direccion, telefono) -> None:
      self.nombreSucursal = nombreSucursal 
      self.direccion = direccion
      self.telefono = telefono
    
    def __repr__(self) -> str:
       return f"User: {self.nombreSucursal} {self.direccion}"
    