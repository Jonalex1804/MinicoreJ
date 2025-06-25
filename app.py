from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from datetime import datetime
import os

app = Flask(__name__, template_folder='template')

# Configuración de base de datos
app.config['SECRET_KEY'] = 'clave123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/minicore'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# MODELOS
class Usuario(db.Model):
    __tablename__ = 'usuarios'
    idusuarios = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))
    apellido = db.Column(db.String(100))
    ventas = db.relationship('Venta', backref='usuario')

class Venta(db.Model):
    __tablename__ = 'ventas'
    idventas = db.Column(db.Integer, primary_key=True)
    idusuario = db.Column(db.Integer, db.ForeignKey('usuarios.idusuarios'))
    monto = db.Column(db.Float)
    fecha = db.Column(db.Date)

# Comisión por tramos
def calcular_comision(total):
    if total >= 1000:
        return total * 0.15
    elif total >= 800:
        return total * 0.10
    elif total >= 600:
        return total * 0.08
    elif total >= 500:
        return total * 0.06
    else:
        return 0

# Insertar datos quemados si no existen
def insertar_datos_de_prueba():
    if Usuario.query.count() == 0:
        usuarios = [
            Usuario(nombre="Juan", apellido="Pérez"),
            Usuario(nombre="Ana", apellido="Martínez"),
            Usuario(nombre="Carlos", apellido="Gómez"),
            Usuario(nombre="Lucía", apellido="Sánchez"),
            Usuario(nombre="Pedro", apellido="Ramírez")
        ]
        db.session.add_all(usuarios)
        db.session.commit()

    if Venta.query.count() == 0:
        ventas = [
            Venta(idusuario=1, monto=120.50, fecha='2025-06-01'),
            Venta(idusuario=1, monto=380.00, fecha='2025-06-02'),
            Venta(idusuario=2, monto=150.00, fecha='2025-06-03'),
            Venta(idusuario=2, monto=500.00, fecha='2025-06-05'),
            Venta(idusuario=3, monto=75.00, fecha='2025-06-07'),
            Venta(idusuario=3, monto=95.00, fecha='2025-06-09'),
            Venta(idusuario=4, monto=300.00, fecha='2025-06-10'),
            Venta(idusuario=4, monto=600.00, fecha='2025-06-12'),
            Venta(idusuario=5, monto=210.00, fecha='2025-06-15'),
            Venta(idusuario=5, monto=800.00, fecha='2025-06-17')
        ]
        db.session.add_all(ventas)
        db.session.commit()

@app.route('/')
def home():
    return render_template('formulario_busqueda.html')

@app.route('/comisiones', methods=['POST'])
def mostrar_comisiones():
    fecha_inicio = datetime.strptime("2025-06-01", "%Y-%m-%d")
    fecha_fin = datetime.strptime("2025-07-01", "%Y-%m-%d")

    resultados = (
        db.session.query(
            Usuario.nombre,
            Usuario.apellido,
            func.sum(Venta.monto).label('total_ventas')
        )
        .join(Venta)
        .filter(Venta.fecha.between(fecha_inicio, fecha_fin))
        .group_by(Usuario.idusuarios)
        .all()
    )

    # Agregamos la comisión calculada
    resumen = []
    for r in resultados:
        comision = calcular_comision(r.total_ventas)
        resumen.append({
            "nombre": r.nombre,
            "apellido": r.apellido,
            "total_ventas": r.total_ventas,
            "comision": comision
        })

    return render_template('comision.html', comision=resumen)

# MAIN
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        insertar_datos_de_prueba()
    app.run(debug=True)
