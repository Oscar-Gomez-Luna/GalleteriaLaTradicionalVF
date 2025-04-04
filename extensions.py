from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from functools import wraps
from flask import redirect, url_for, flash
from flask_login import current_user
from flask import flash, redirect, url_for

db = SQLAlchemy()
csrf = CSRFProtect()

from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user

def role_required(*roles):
    """Decorador para restringir acceso basado en roles y redirigir a cada rol a su módulo."""
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for("usuarios.login"))  # Si no está autenticado, va al login
            
            if current_user.rol in roles:
                return f(*args, **kwargs)  # Permite acceso si el rol es válido
            
            # Redirige a cada rol a su módulo correspondiente
            flash("No tienes permiso para acceder a esta página.", "danger")
            if current_user.rol == "ADMS":
                return redirect(url_for("galletas.galletas"))
            elif current_user.rol == "CAJA":
                return redirect(url_for("venta.ventas"))
            elif current_user.rol == "PROD":
                return redirect(url_for("produccion.produccion"))
            elif current_user.rol == "CLIE":
                return redirect(url_for("portal_cliente.portal_cliente"))
            else:
                return redirect(url_for("usuarios.index"))  # Rol no reconocido
        return wrapped
    return decorator