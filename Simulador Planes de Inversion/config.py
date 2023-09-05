class Config:
    #Configuracion de flask
    SECRET_KEY = "6600ce5144dbde31215930a1accd73aa829a68b4deb8d4b2eb7e0fc9bce60953"
    DEBUG = True
    TESTING = False
    # Configuracion de la DB
    SQLALCHEMY_TRACK_MODIFCATIONS = False
    SQLALCHEMY_DATABASE_URI =("mysql+pymysql://root:Daz00575#@localhost:3306/moneidapp")
    

class ProductionConfig(Config):
    DEBUG = True
    TESTING = False

class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = True

config = {
    "production": ProductionConfig,
    "development": DevelopmentConfig,
    "default": DevelopmentConfig,
}    