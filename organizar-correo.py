from classes.correo import Correo
from classes.logger import Logger


# Conectar al servidor de correo
correo = Correo() 

#Obtener etiquetas y filtros del correo
diccionario_filtros = correo.crear_diccionario_filtros()


try:
    #Obtener los mensajes del correo de la bandeja de entrada
    correo.seleccionar_bandeja("INBOX")
    
    #Total de mensajes en la bandeja de entrada
    total_mensajes = correo.total_mensajes()
    
    if total_mensajes == 0:
        correo.logger.log("No hay mensajes en la bandeja de entrada")
        raise Exception("No hay mensajes en la bandeja de entrada")
        exit()
        
    mensajes_movidos = 0
    
    for etiqueta,filtro in diccionario_filtros.items():
        correo.logger.log(f"Etiqueta: {etiqueta} - Filtro: {filtro}")
        
        #Obtener los mensajes con su filtro correspondiente
        id_mensajes = correo.filtrar_correo(filtro)
        #Si no hay mensajes con el filtro, se continua con el siguiente filtro
        if len(id_mensajes) == 0:
            correo.logger.log(f"No hay mensajes con el filtro {filtro}")
            continue
        #Mover los mensajes a la carpeta correspondiente
        correo.mover_correos("INBOX", etiqueta, id_mensajes)
        #Marcar los mensajes como no leidos
        correo.marcar_como_no_leidos(id_mensajes)
        mensajes_movidos += len(id_mensajes)
        
        correo.logger.log(f"Total de mensajes movidos: {mensajes_movidos} de {total_mensajes}")
        
    if mensajes_movidos != total_mensajes:
        correo.logger.warning("No se movieron todos los mensajes")
        raise Exception("No se movieron todos los mensajes")
  
except Exception as e:
    correo.logger.error(f"Error: {e}")
finally:
    # Desconectar del servidor de correo
    correo.desconectar_del_correo()
