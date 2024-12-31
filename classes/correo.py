import socket  # Importación necesaria para manejar socket.gaierror
import configparser
import imaplib
import email
from email.header import decode_header
from typing import Tuple, List
from classes.logger import Logger




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
    def __init__(self):
        self.config = cargar_configuracion("config.ini")
        self.username = self.config["login"]["username"].strip()
        self.password = self.config["login"]["password"].strip()
        self.imap_server = self.config["login"]["imap_server"].strip()
        self.imap = self.conectar_al_correo()


    def conectar_al_correo(self) -> object:
        #Conectar al servidor IMAP
        try:
            imap = imaplib.IMAP4_SSL(self.imap_server)
            logger.log("Conexion al servidor IMAP establecida.")
        except socket.gaierror as e:
            logger.error(f"Error al resolver el servidor IMAP: {self.imap_server}. Detalles: {e}")
            raise ValueError(f"Error al resolver el servidor IMAP: {self.imap_server}. Detalles: {e}")
        except Exception as e:
            logger.error(f"Error al inicializar la conexion IMAP: {e}")
            raise ValueError(f"Error al inicializar la conexion IMAP: {e}")

        #Autenticacion al correo
        try:
            imap.login(self.username, self.password)
            logger.log("Autenticacion exitosa.")               
        except imaplib.IMAP4.error as e:
            logger.error(f"Error de autenticacion o conexion: {e}")
        except Exception as e:
            logger.error(f"Error inesperado: {e}")

        return imap

    def desconectar_del_correo(self) -> None:
        """
        Cierra la conexión con el servidor de correo.
        """
        self.imap.logout()
        logger.log("Conexion IMAP cerrada.")

    def seleccionar_bandeja(self, bandeja: str) -> object:
        """
        Selecciona una bandeja de correo.
        """
        status, mensajes = self.imap.select(bandeja)
        if status != "OK":
            logger.error(f"Error al seleccionar la bandeja de correo: {bandeja}. Detalles: {mensajes}")
        else:
            logger.log(f"Bandeja de correo seleccionada: {bandeja}")

        return self.imap

    def filtrar_correo(self, etiqueta: str) -> list:
        """
        Filtra correos según la etiqueta proporcionada.
        """
        try:
            status, mensajes = self.imap.search(None, etiqueta)
            if status != "OK":
                logger.error(f"Error al buscar correos con la etiqueta '{etiqueta}'.")
                return "ERROR", []
        except Exception as e:
            logger.error(f"Error al buscar correos con la etiqueta '{etiqueta}'. Detalles: {e}")
            return "ERROR", []

        logger.log(f"Total de correos {etiqueta}: {len(mensajes[0].split())}")
        return mensajes
    def decodificar_correos(self, mensaje: Tuple) -> Tuple[str, str, str]:
        """
        Decodifica el mensaje y extrae el asunto y el cuerpo del correo en latin1.
        Si el correo es multipart/alternative, solo devuelve el HTML.
        """
        if isinstance(mensaje, tuple):
            # Decodificar el mensaje
            msg = email.message_from_bytes(mensaje[1])

            # Obtener el asunto
            subject, encoding = decode_header(msg["Subject"])[0]

            # Verificar si el asunto es de tipo bytes y decodificarlo
            if isinstance(subject, bytes):
                try:
                    subject = subject.decode(encoding or "latin1")
                except Exception as e:
                    logger.warning(f"Error al decodificar el asunto: {e}")
                    subject = "Error al decodificar el asunto"
            elif isinstance(subject, str):
                # Si el asunto ya es de tipo string, no necesitamos decodificarlo
                pass
            else:
                logger.warning("El asunto tiene un formato inesperado.")
                subject = "Asunto no disponible"

            # Obtener el remitente y decodificarlo si es necesario
            from_ = msg.get("From")
            if isinstance(from_, bytes):
                try:
                    from_ = from_.decode(encoding or "latin1")
                except Exception as e:
                    logger.error(f"Error al decodificar el remitente: {e}")
                    from_ = "Error al decodificar el remitente"

            # Inicializamos 'body' como None para manejarlo más adelante
            body = "Cuerpo no disponible"

            if msg.is_multipart():

                # Si el correo es multipart/alternative, primero buscamos el HTML
                for part in msg.walk():
                    content_type = part.get_content_type()

                    # Si encontramos una parte HTML, la priorizamos
                    if content_type == "text/html":
                        try:
                            body = part.get_payload(decode=True).decode("latin1", errors="replace")
                            break  # Salimos del bucle al encontrar el HTML
                        except Exception as e:
                            logger.warning(f"Error al decodificar el cuerpo HTML. Detalles: {e}")

                    # Si encontramos texto plano solo después de no haber encontrado HTML, lo procesamos
                    elif content_type == "text/plain":
                        try:
                            body = part.get_payload(decode=True).decode("latin1", errors="replace")
                            break
                        except Exception as e:
                            logger.warning(f"Error al decodificar el cuerpo de texto. Detalles: {e}")

            else:
                # Si no es multipart, simplemente decodificamos el cuerpo
                try:
                    body = msg.get_payload(decode=True).decode("latin1", errors="replace")
                    
                except Exception as e:
                    logger.error(f"Error al decodificar el cuerpo del mensaje. Detalles: {e}")
            
            correo = {
                "asunto": subject,
                "remitente": from_,
                "cuerpo": body
            }
            logger.log(f"Correo decodificado: {correo}")
            return correo

    def obtener_correos(self, mensajes: list) -> List[dict]:
        """
        Obtiene los correos sin leer.
        """
        todos_los_mensajes = {}
        mensajes = mensajes[0].split()
        for num in mensajes:
            status, mensaje_data = self.imap.fetch(num, "(RFC822)")
            if status == "OK":
                logger.log(f"Obteniendo correo sin leer: {num.decode('utf-8')}")
                dict_correo = self.decodificar_correos(mensaje_data[0])
                
                todos_los_mensajes[num.decode('utf-8')] = dict_correo
            else:
                logger.error(f"Error al obtener el correo sin leer. Detalles: {mensaje_data}")

        return todos_los_mensajes
            
    def obtener_todos_noleidos(self) -> None:
        """
        Obtiene todos los correos no enviados.
        """
        # Seleccionar la bandeja de entrada
        self.seleccionar_bandeja("inbox")

        # Obtener los correos sin leer
        mensajes = self.filtrar_correo("UNSEEN")
        
        no_leidos = self.obtener_correos(mensajes)
        
        return no_leidos