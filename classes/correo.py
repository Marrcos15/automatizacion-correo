import socket  # Importación necesaria para manejar socket.gaierror
import configparser
import imaplib
import email
from email.header import decode_header
from typing import Tuple, List
from classes.logger import Logger


class Correo:
    """
    Clase para interactuar con un servidor de correo IMAP.
    """
    def __init__(self):
        self.logger = Logger("automatizacion_correo")
        self.config = self.cargar_configuracion("config.ini")
        self.username = self.config["login"]["username"].strip()
        self.password = self.config["login"]["password"].strip()
        self.imap_server = self.config["login"]["imap_server"].strip()
        self.imap = self.conectar_al_correo()
        
        
        #Etiquetas
        self.arbol_etiquetas = {
            'banco' : ['openbank', 'santander'],
            'busqueda-de-trabajo': ['infojobs', 'linkedin', 'tecnoempleo'],
            'plataformas-juegos' : ['steam', 'ea', 'chess.com'],
            'plataformas-programacion' : ['github', 'google', 'make', 'notion'],
            'pruebas': [],
            'redes-sociales' : ['facebook', 'instagram'],
            'trabajo': ['nominas'],
            'plataformas': ['netflix','spotify']
        }
        self.filtro_etiquetas = {
            'openbank': {
                'remitente': 'openbank',
                'asunto': '',
                'cuerpo': '',
            },
            'santander': {
                'remitente': 'santander',
                'asunto': '',
                'cuerpo': '',
            },
            'infojobs': {
                'remitente': 'infojobs',
                'asunto': '',
                'cuerpo': '',
            },
            'linkedin': {
                'remitente': 'linkedin',
                'asunto': '',
                'cuerpo': '',
            },
            'tecnoempleo': {
                'remitente': 'tecnoempleo',
                'asunto': '',
                'cuerpo': '',
            },
            'steam': {
                'remitente': 'steam',
                'asunto': '',
                'cuerpo': '',
            },
            'ea': {
                'remitente': 'ea',
                'asunto': '',
                'cuerpo': '',
            },
            'chess.com': {
                'remitente': 'chess.com',
                'asunto': '',
                'cuerpo': '',
            },
            'github': {
                'remitente': 'github',
                'asunto': '',
                'cuerpo': '',
            },
            'google': {
                'remitente': 'google',
                'asunto': '',
                'cuerpo': '',
            },
            'make': {
                'remitente': 'make',
                'asunto': '',
                'cuerpo': '',
            },
            'notion': {
                'remitente': 'notion',
                'asunto': '',
                'cuerpo': '',
            },
            'nominas': {
                'remitente': 'nominas',
                'asunto': '',
                'cuerpo': '',
            },
            'facebook': {
                'remitente': 'facebook',
                'asunto': '',
                'cuerpo': '',
            },
            'instagram': {
                'remitente': 'instagram',
                'asunto': '',
                'cuerpo': '',
            },
            'netflix': {
                'remitente': 'netflix',
                'asunto': '',
                'cuerpo': '',
            },
            'spotify': {
                'remitente': 'spotify',
                'asunto': '',
                'cuerpo': '',
            }
        }
        
    def cargar_configuracion(self, ruta: str) -> configparser.ConfigParser:
        """
        Carga y valida el archivo de configuración.
        
        :param ruta: Ruta del archivo de configuración.
        """
        config = configparser.ConfigParser()
        config.read(ruta)

        if not config.has_section("login") or \
           not all(key in config["login"] for key in ["username", "password", "imap_server"]):
            self.logger.error("Archivo de configuracion incompleto o inexistente.")
            raise ValueError("Archivo de configuracion incompleto o inexistente.")

        return config


    def conectar_al_correo(self) -> object:
        """
        Conecta al servidor de correo IMAP y se autentica
        con las credenciales proporcionadas.
        
        :return: Objeto de conexión IMAP.
        """
        #Conectar al servidor IMAP
        try:
            imap = imaplib.IMAP4_SSL(self.imap_server)
            self.logger.log("Conexion al servidor IMAP establecida.")
        except socket.gaierror as e:
            self.logger.error(f"Error al resolver el servidor IMAP: {self.imap_server}. Detalles: {e}")
            raise ValueError(f"Error al resolver el servidor IMAP: {self.imap_server}. Detalles: {e}")
        except Exception as e:
            self.logger.error(f"Error al inicializar la conexion IMAP: {e}")
            raise ValueError(f"Error al inicializar la conexion IMAP: {e}")

        #Autenticacion al correo
        try:
            imap.login(self.username, self.password)
            self.logger.log("Autenticacion exitosa.")               
        except imaplib.IMAP4.error as e:
            self.logger.error(f"Error de autenticacion o conexion: {e}")
        except Exception as e:
            self.logger.error(f"Error inesperado: {e}")

        return imap

    def desconectar_del_correo(self) -> None:
        """
        Cierra la conexión al servidor de correo de forma segura.

        """
        self.logger.log("Desconectando del servidor de correo.")
        try:
            if self.imap is not None:
                # Verifica si la conexión sigue activa
                if self.imap.state == 'SELECTED' or self.imap.state == 'AUTH':
                    self.imap.logout()
                else:
                    self.logger.log("La conexión IMAP ya estaba cerrada.")
        except Exception as e:
            self.logger.error(f"Error al intentar desconectar: {e}")

    def seleccionar_bandeja(self, bandeja: str) -> object:
        """
        Selecciona una bandeja de correo.
        
        :param bandeja: Nombre de la bandeja de correo a seleccionar.
        """
        status, mensajes = self.imap.select(bandeja)
        if status != "OK":
            self.logger.error(f"Error al seleccionar la bandeja de correo: {bandeja}. Detalles: {mensajes}")
        else:
            self.logger.log(f"Bandeja de correo seleccionada: {bandeja}")

        return self.imap

    def filtrar_correo(self, filtro: str) -> list:
        """
        Filtra correos según la etiqueta proporcionada.
        
        :param filtro: Filtro de búsqueda de correos.
        :return: Lista de IDs de mensajes que cumplen con el filtro en bytes (b'5').
        """
        try:
            status, mensajes = self.imap.search(None, filtro)
            if status != "OK":
                self.logger.error(f"Error al buscar correos con la etiqueta '{filtro}'.")
                return []
        except Exception as e:
            self.logger.error(f"Error al buscar correos con la etiqueta '{filtro}'. Detalles: {e}")
            return []

        self.logger.log(f"Total de correos {filtro}: {len(mensajes[0].split())}")
        list_idmensajes = mensajes[0].split()

        return list_idmensajes
    
    def decodificar_correos(self, mensaje: Tuple) -> Tuple[str, str, str]:
        """
        Decodifica el mensaje y extrae el asunto y el cuerpo del correo en latin1.
        Si el correo es multipart/alternative, solo devuelve el HTML.
        
        :param mensaje: Tupla con el mensaje decodificado.
        :return: Tupla con el asunto, remitente y cuerpo del correo.
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
                    self.logger.warning(f"Error al decodificar el asunto: {e}")
                    subject = "Error al decodificar el asunto"
            elif isinstance(subject, str):
                # Si el asunto ya es de tipo string, no necesitamos decodificarlo
                pass
            else:
                self.logger.warning("El asunto tiene un formato inesperado.")
                subject = "Asunto no disponible"

            # Obtener el remitente y decodificarlo si es necesario
            from_ = msg.get("From")
            if isinstance(from_, bytes):
                try:
                    from_ = from_.decode(encoding or "latin1")
                except Exception as e:
                    self.logger.error(f"Error al decodificar el remitente: {e}")
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
                            self.logger.warning(f"Error al decodificar el cuerpo HTML. Detalles: {e}")

                    # Si encontramos texto plano solo después de no haber encontrado HTML, lo procesamos
                    elif content_type == "text/plain":
                        try:
                            body = part.get_payload(decode=True).decode("latin1", errors="replace")
                            break
                        except Exception as e:
                            self.logger.warning(f"Error al decodificar el cuerpo de texto. Detalles: {e}")

            else:
                # Si no es multipart, simplemente decodificamos el cuerpo
                try:
                    body = msg.get_payload(decode=True).decode("latin1", errors="replace")
                    
                except Exception as e:
                    self.logger.error(f"Error al decodificar el cuerpo del mensaje. Detalles: {e}")
            
            # Crear un diccionario con los datos del correo
            correo = {
                "asunto": subject,
                "remitente": from_,
                "cuerpo": body
            }
            
            return correo

    def obtener_correos(self, mensajes: list) -> List[dict]:
        """
        Obtiene los correos y los deja sin leer.
        
        :param mensajes: Lista de IDs de mensajes a obtener.
        :return: Lista de diccionarios con los correos decodificados.
        """
        todos_los_mensajes = {}

        for num in mensajes:
            status, mensaje_data = self.imap.fetch(num, "(BODY.PEEK[])")
            if status == "OK":
                dict_correo = self.decodificar_correos(mensaje_data[0])
                # Agregar el correo decodificado al diccionario
                todos_los_mensajes[num.decode('utf-8')] = dict_correo
            else:
                self.logger.error(f"Error al obtener el correo sin leer. Detalles: {mensaje_data}")

        return todos_los_mensajes
            
    def obtener_todos_noleidos(self) -> List[dict]:
        """
        Obtiene todos los correos no enviados.
        
        :return: Lista de diccionarios con los correos no leidos.
        """
        # Seleccionar la bandeja de entrada
        self.seleccionar_bandeja("inbox")

        # Obtener los correos sin leer
        mensajes = self.filtrar_correo("UNSEEN")

        no_leidos = self.obtener_correos(mensajes)
        return no_leidos
    
    def listar_etiquetas(self) -> List[str]:
        """
        Lista todas las etiquetas (carpetas) disponibles en la cuenta IMAP.

        :param imap: Objeto de conexión IMAP.
        :return: Lista de etiquetas con sus nombres y detalles.
        """
        try:
            status, folders = self.imap.list()
            if status != "OK":
                self.logger.warning("No se pudieron obtener las etiquetas.")
                return []

            etiquetas = []
            for folder in folders:
                # Decodificar la respuesta
                parts = folder.decode().split(' "/" ')
                if len(parts) == 2:
                    etiquetas.append(parts[1].strip('"'))  # Nombre de la etiqueta

            return etiquetas
    
        except Exception as e:
            print(f"Error al listar etiquetas: {e}")
            return []
    
    def eliminar_correos(self, mensajes: list) -> bool:
        """
        Elimina los correos proporcionados.
        
        :param mensajes: Lista de IDs de mensajes a eliminar
        :return: True si los mensajes se eliminaron correctamente.
        """
        for num in mensajes:
            status, _ = self.imap.store(num, '+FLAGS', '\\Deleted')
            if status != "OK":
                self.logger.error(f"No se pudo eliminar el mensaje {num}")

        # Expurgar (eliminar físicamente) los mensajes marcados como eliminados
        self.imap.expunge()
        return True
    
    
    def mover_correos(self, origen: str, destino: str, id_mensajes: list) -> None:
        """
        Mueve correos de una etiqueta a otra.

        :param origen: Nombre de la etiqueta (carpeta) origen.
        :param destino: Nombre de la etiqueta (carpeta) destino.
        :param id_mensajes: Lista de IDs de mensajes a mover.
        """
        try:
            # Obtener etiquetas
            etiquetas = self.listar_etiquetas()

            # Verificar que la etiqueta destino existe
            destino_utf7 = destino.encode('utf-7').decode('ascii')
            if destino_utf7 not in etiquetas:
                self.logger.error(f"La carpeta destino '{destino}' no existe.")
                return

            # Seleccionar la carpeta origen
            status, _ = self.imap.select(origen)
            if status != "OK":
                self.logger.error(f"No se pudo seleccionar la carpeta '{origen}'")
                return

            self.logger.log(f"Se seleccionó la carpeta '{origen}'")
            
            # Mover los mensajes a la carpeta destino
            for mensaje_id in id_mensajes:
                self.logger.debug(f"Intentando copiar mensaje {mensaje_id} a '{destino_utf7}'")

                status, response = self.imap.copy(mensaje_id, destino)
                if status != "OK":
                    self.logger.warning(f"No se pudo copiar el mensaje {mensaje_id} a '{destino}'")
                    continue

                self.logger.debug(f"Se copió el mensaje {mensaje_id} a '{destino}'")

            # Eliminar los mensajes de la carpeta origen
            if self.eliminar_correos(id_mensajes):
                # Eliminar el mensaje de la carpeta origen
                self.logger.log(f"Se eliminó los mensajes {id_mensajes} de '{origen}'")
            else:
                self.logger.warning(f"No se pudieron eliminar los mensajes {id_mensajes} de '{origen}'")

        except Exception as e:
            self.logger.warning(f"Error al mover correos: {e}")
                
    def marcar_como_no_leidos(self, id_mensajes: list) -> None:
        """
        Marca los mensajes como no leídos.

        :param id_mensajes: Lista de IDs de mensajes a marcar como no leidos.
        """
        for mensaje_id in id_mensajes:
            # Marcar el mensaje como no leído quitando la bandera '\Seen'
            status, _ = self.imap.store(mensaje_id, '-FLAGS', '\\Seen')
            if status != "OK":
                self.logger.error(f"No se pudo marcar como no leído el mensaje {mensaje_id}")
            else:
                self.logger.debug(f"Se marcó como no leído el mensaje {mensaje_id}")
                
            
        
            
    def crear_diccionario_filtros(self) -> dict:
        """
        Crea un diccionario con el filtro de cada etiqueta hija.

        :param arbol_etiquetas: Diccionario del árbol de etiquetas.
        :param filtro_etiquetas: Diccionario de filtros para las etiquetas.
        :return: Diccionario con los filtros de cada etiqueta hija.
        """
        diccionario_filtros = {}

        for etiqueta_padre, etiquetas_hijas in self.arbol_etiquetas.items():
            for etiqueta_hija in etiquetas_hijas:
                
                filtro = ""
                if etiqueta_hija not in self.filtro_etiquetas:
                    self.logger.warning(f"No se encontró el filtro para la etiqueta '{etiqueta_hija}'")
                else:
                    self.logger.debug(f"Filtro encontrado para la etiqueta '{etiqueta_hija}'")
                    filtros_etiqueta = self.filtro_etiquetas[etiqueta_hija]
                    
                    # Crear el filtro para la etiqueta hija
                    if filtros_etiqueta["remitente"]:
                        filtro += f"FROM {filtros_etiqueta['remitente']} "
                    
                    if filtros_etiqueta["asunto"]:
                        filtro += f"SUBJECT {filtros_etiqueta['asunto']} "
                    
                    if filtros_etiqueta["cuerpo"]:
                        filtro += f"BODY {filtros_etiqueta['cuerpo']} "
                
                if etiqueta_hija in self.filtro_etiquetas:
                    diccionario_filtros[f"{etiqueta_padre}/{etiqueta_hija}"] = filtro.strip()
                    
        return diccionario_filtros
    
    def total_mensajes(self) -> int:
        """
        Obtiene el total de mensajes en la bandeja de entrada.
        
        :return: Número total de mensajes en la bandeja de entrada.
        """
        status, mensajes = self.imap.search(None, "ALL")
        if status != "OK":
            self.logger.error("Error al obtener el total de mensajes.")
            return 0

        total_mensajes = len(mensajes[0].split())
        self.logger.log(f"Total de mensajes en la bandeja de entrada: {total_mensajes}")
        return total_mensajes