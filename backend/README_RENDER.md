# Despliegue en Render.com

## Pasos para desplegar el backend Flask en Render

1. Crea una cuenta gratuita en [Render.com](https://render.com).

2. Crea un nuevo Web Service:
   - Conecta tu repositorio GitHub donde está la carpeta `backend`.
   - Selecciona la rama `main`.
   - En "Root Directory" pon `backend`.
   - En "Build Command" pon:
     ```
     pip install -r requirements.txt
     ```
   - En "Start Command" pon:
     ```
     python app.py
     ```
   - Render detectará automáticamente que es un proyecto Python y usará la versión especificada en `runtime.txt`.

3. Crea el servicio y espera a que Render construya y despliegue la aplicación.

4. Una vez desplegado, Render te proporcionará una URL pública para acceder a tu aplicación.

## Notas

- La base de datos SQLite se almacenará en el contenedor, por lo que para producción se recomienda usar una base de datos gestionada.
- Las imágenes subidas se almacenan en la carpeta `uploads` dentro del contenedor, que es efímera. Para producción, considera usar almacenamiento en la nube.
- Para desarrollo y pruebas, esta configuración es suficiente y funcional.
