# model/dashboard_model.py
from extensions import db
from datetime import datetime, timedelta
from model.venta import Venta
from model.detalle_venta import DetalleVentaGalletas
from model.lote_galleta import LoteGalletas
from model.galleta import Galleta
from model.tipo_galleta import TipoGalleta

def get_ventas_diarias():
    """
    Obtiene las ventas diarias de los últimos 7 días
    lista de fechas y una lista de totales
    """
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=7)

    # obtener las ventas diarias
    result = (db.session.query(Venta.fecha, db.func.sum(Venta.total).label('total_ventas'))
              .filter(Venta.fecha.between(start_date, end_date))
              .group_by(Venta.fecha)
              .order_by(Venta.fecha)
              .all())

    fechas = [row[0].strftime('%Y-%m-%d') for row in result]
    totales = [float(row[1]) for row in result]
    return fechas, totales

def get_productos_mas_vendidos():
    """
    Obtiene los 5 productos más vendidos
    lista de nombres de productos y una lista de cantidades vendidas
    """
    # Usar el ORM para obtener los productos más vendidos
    result = (db.session.query(Galleta.galleta, db.func.sum(DetalleVentaGalletas.cantidad).label('cantidad_vendida'))
              .join(LoteGalletas, LoteGalletas.galleta_id == Galleta.id_galleta)
              .join(DetalleVentaGalletas, DetalleVentaGalletas.lote_id == LoteGalletas.id_lote)
              .group_by(Galleta.galleta)
              .order_by(db.desc('cantidad_vendida'))
              .limit(5)
              .all())

    nombres = [row[0] for row in result]
    cantidades = [int(row[1]) for row in result]
    return nombres, cantidades

def get_presentaciones_mas_vendidas():
    """
    Obtiene las presentaciones más vendidas
    lista de nombres de presentaciones y una lista de cantidades vendidas
    """
    #presentaciones más vendidas
    result = (db.session.query(TipoGalleta.nombre, db.func.sum(DetalleVentaGalletas.cantidad).label('cantidad_vendida'))
              .join(Galleta, Galleta.tipo_galleta_id == TipoGalleta.id_tipo_galleta)
              .join(LoteGalletas, LoteGalletas.galleta_id == Galleta.id_galleta)
              .join(DetalleVentaGalletas, DetalleVentaGalletas.lote_id == LoteGalletas.id_lote)
              .group_by(TipoGalleta.nombre)
              .order_by(db.desc('cantidad_vendida'))
              .all())

    nombres = [row[0] for row in result]
    cantidades = [int(row[1]) for row in result]
    return nombres, cantidades
