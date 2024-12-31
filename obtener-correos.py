from classes.correo import Correo

# Conectar al servidor de correo
correo = Correo()

# Seleccionar la bandeja de entrada
bandeja_entrada = correo.seleccionar_bandeja("inbox")

# Obtener los correos sin leer
mensajes = correo.filtrar_correo("UNSEEN")
correo.obtener_correos(mensajes)

# Desconectar del servidor de correo
correo.desconectar_del_correo()
