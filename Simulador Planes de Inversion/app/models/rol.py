from app import db

class Rol(db.Model):
    __tablename__ = "roles"
    idRol = db.Column(db.Integer(), primary_key=True, autoincrement=True, nullable=False)
    tipoRol = db.Column(db.String(50))

    def __init__(self, tipoRol) -> None:
        self.tipoRol = tipoRol
    
    def __repr__(self) -> str:
        return f"User: {self.tipoRol}"
