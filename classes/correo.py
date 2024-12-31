import socket  # Importación necesaria para manejar socket.gaierror
import configparser
import imaplib
from typing import Tuple
from logger import Logger



# Usar el Logger para registrar los eventos
logger = Logger("automatizacion_correo")


def cargar_configuracion(ruta: str) -> configparser.ConfigParser:
    """
    Carga y valida el archivo de configuración.
    """
    config = configparser.ConfigParser()
    config.read(ruta)

    if not config.has_section("login") or \
       not all(key in config["login"] for key in ["username", "password", "imap_server"]):
        logger.error("Archivo de configuracion incompleto o inexistente.")
        raise ValueError("Archivo de configuracion incompleto o inexistente.")

    return config


class Correo:
    def __init__(self, config: configparser.ConfigParser):
        """
        Inicializa la conexión IMAP utilizando los valores de configuración.
        """
        self.username = config["login"]["username"].strip()
        self.password = config["login"]["password"].strip()
        self.imap_server = config["login"]["imap_server"].strip()

        try:
            self.imap = imaplib.IMAP4_SSL(self.imap_server)
            logger.log("Conexion al servidor IMAP establecida.")
        except socket.gaierror as e:
            logger.error(f"Error al resolver el servidor IMAP: {self.imap_server}. Detalles: {e}")
            raise ValueError(f"Error al resolver el servidor IMAP: {self.imap_server}. Detalles: {e}")
        except Exception as e:
            logger.error(f"Error al inicializar la conexion IMAP: {e}")
            raise ValueError(f"Error al inicializar la conexion IMAP: {e}")

    def conectar_al_correo(self, opcion: str) -> None:
        """
        Conecta al correo y ejecuta la operacion indicada.
        """
        try:
            self.imap.login(self.username, self.password)
            logger.log("Autenticacion exitosa.")

            
            if opcion != "":
                #Opciones con las que cuenta el programa    
                match(opcion):
                    case "Total sin leer":
                        self.obtener_total_correos_sin_leer()
            
            else:
                logger.warning(f"Opcion no reconocida: {opcion}")
                
            
        except imaplib.IMAP4.error as e:
            logger.error(f"Error de autenticacion o conexion: {e}")
        except Exception as e:
            logger.error(f"Error inesperado: {e}")
        finally:
            self._cerrar_conexion()

    def obtener_total_correos_sin_leer(self) -> None:
        """
        Obtiene el número total de correos no leídos en la bandeja de entrada.
        """
        if not self._seleccionar_bandeja("inbox"):
            return

        status, messages = self.filtrar_correos("UNSEEN")
        if status != "OK":
            logger.error("Error al buscar correos no leídos.")
            return

        email_ids = messages[0].split()
        logger.log(f"Tienes {len(email_ids)} mensajes sin leer.")

    def filtrar_correos(self, etiqueta: str) -> Tuple[str, list]:
        """
        Filtra correos según la etiqueta proporcionada.
        """
        try:
            status, messages = self.imap.search(None, etiqueta)
            if status != "OK":
                logger.error(f"Error al buscar correos con la etiqueta '{etiqueta}'.")
                return status, []
            return status, messages
        except Exception as e:
            logger.error(f"Error al filtrar correos: {e}")
            return "ERROR", []

    def _seleccionar_bandeja(self, bandeja: str) -> bool:
        """
        Selecciona una bandeja de correo.
        """
        try:
            status, _ = self.imap.select(bandeja)
            if status != "OK":
                logger.error(f"No se pudo seleccionar la bandeja: {bandeja}.")
                return False
            return True
        except Exception as e:
            logger.error(f"Error al seleccionar la bandeja '{bandeja}': {e}")
            return False

    def _cerrar_conexion(self) -> None:
        """
        Cierra la conexión con el servidor IMAP si está autenticado.
        """
        try:
            if self.imap.state == "AUTH":
                self.imap.logout()
                logger.log("Conexion IMAP cerrada.")
        except Exception as e:
            logger.error(f"Error al cerrar la conexion: {e}")


# Ejecución del programa principal
if __name__ == "__main__":
    try:
        config = cargar_configuracion("./config.ini")
        correo = Correo(config)
        correo.conectar_al_correo("Total sin leer")
        correo._cerrar_conexion()
    except ValueError as e:
        logger.error(f"Error de configuracion: {e}")
    except Exception as e:
        logger.error(f"Error inesperado: {e}")
