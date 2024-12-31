from classes.correo import Correo

# Conectar al servidor de correo
correo = Correo()

# Obtener los mensajes del correo
mensajes = correo.obtener_todos_noleidos()


# Desconectar del servidor de correo
correo.desconectar_del_correo()
