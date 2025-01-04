import os
import logging
from datetime import datetime
import sys  # Import necesario para manejar codificación

class Logger:
    def __init__(self, programa: str):
        """
        Inicializa el Logger para crear el archivo de log en la carpeta `logs`.
        """
        self.programa = programa
        self.carpeta_logs = "logs"

        # Crear la carpeta logs si no existe
        if not os.path.exists(self.carpeta_logs):
            os.makedirs(self.carpeta_logs)

        # Crear el nombre del archivo de log con fecha y hora
        self.archivo_log = os.path.join(
            self.carpeta_logs, f"{self.programa}_{datetime.now().strftime('%Y-%m-%d')}.log"
        )

        # Crear un log formatter que incluya el campo 'programa' y 'tipo'
        formatter = logging.Formatter('%(asctime)s [%(levelname)s]: %(message)s',
                                      datefmt='%Y-%m-%d %H:%M:%S')

        # Crear un handler para el archivo de log
        file_handler = logging.FileHandler(self.archivo_log, encoding="utf-8")
        file_handler.setFormatter(formatter)

        # Crear un handler para la consola
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)

        # Configurar el logger
        self.logger = logging.getLogger(self.programa)
        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

        # Crear un filtro para agregar el programa al log
        log_filter = logging.Filter()
        log_filter.filter = self._add_programa
        self.logger.addFilter(log_filter)

    def _add_programa(self, record):
        """
        Añade el atributo 'programa' al registro del log.
        """
        record.programa = self.programa
        return True

    def log(self, mensaje: str) -> None:
        """
        Escribe un mensaje en el archivo de log con el formato de fecha y hora.
        """
        self.logger.info(mensaje)

    def error(self, mensaje: str) -> None:
        """
        Escribe un mensaje de error en el archivo de log.
        """
        self.logger.error(mensaje)

    def warning(self, mensaje: str) -> None:
        """
        Escribe un mensaje de advertencia en el archivo de log.
        """
        self.logger.warning(mensaje)

    def debug(self, mensaje: str) -> None:
        """
        Escribe un mensaje de depuración en el archivo de log.
        """
        self.logger.debug(mensaje)

    def critical(self, mensaje: str) -> None:
        """
        Escribe un mensaje crítico en el archivo de log.
        """
        self.logger.critical(mensaje)
