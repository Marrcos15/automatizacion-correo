# Automatización de Correo

Este proyecto tiene como objetivo automatizar el proceso de filtrado de correos electrónicos utilizando Python. 

La iniciativa surge de la necesidad de implementar un sistema que gestione y clasifique automáticamente los mensajes recibidos en una cuenta de correo principal. Esta cuenta centraliza la correspondencia, ya que recibe los mensajes redirigidos desde otras dos cuentas asociadas. El proyecto busca optimizar el tiempo y mejorar la organización del flujo de correos mediante reglas personalizadas de filtrado y clasificación.

A continuación, se detallan las librerías necesarias para que el proyecto funcione correctamente.

## Librerías necesarias

Para instalar las librerías necesarias, puedes utilizar `pip`. A continuación se muestra una lista de las librerías requeridas:

- `smtplib`: Librería estándar de Python para enviar correos electrónicos.
- `email`: Librería estándar de Python para gestionar el contenido del correo.
- `dotenv`: Para cargar variables de entorno desde un archivo `.env`.
- `schedule`: Para programar tareas en Python.

## Instalación

Puedes instalar las librerías necesarias ejecutando el siguiente comando:

```bash
git clone https://github.com/Marrcos15/automatizacion-correo.git
cd repositorio
```

## Configuración

1. Crea un archivo `config.ini` en el directorio raíz del proyecto con las siguientes variables:

```
[login]
username = exasmple@gmail.com
password = password_imap
imap_server = imap.gmail.com
```

2. Asegúrate de que el archivo `config.ini` esté en tu `.gitignore` para no compartir tus credenciales.

3. Ajusta el archivo `etiquetas.json` a tu gusto según tus necesidades de filtrado

## Uso

Ejecuta el script principal para iniciar la automatización del envío de correos:

```bash
python -m scripts.organizar_correo.py
```