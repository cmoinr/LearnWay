import datetime
import pytz

def obtener_fecha_venezuela():
    """Obtiene la fecha actual en la zona horaria de Venezuela en formato YYYY-MM-DD."""
    zona_horaria_venezuela = pytz.timezone('America/Caracas')
    fecha_utc = datetime.datetime.now(datetime.UTC)  # Obtiene la fecha UTC actual
    fecha_venezuela = fecha_utc.replace(tzinfo=pytz.utc).astimezone(zona_horaria_venezuela)
    return fecha_venezuela.strftime('%Y-%m-%d')

# Ejemplo de uso
print(f"Fecha actual en Venezuela: {obtener_fecha_venezuela()}")