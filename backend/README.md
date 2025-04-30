# Affiliate Platform Backend - Flask

## Despliegue en Railway

1. Crea un proyecto en Railway y conecta tu repositorio GitHub que contenga la carpeta `backend`.
2. Configura el comando de inicio en Railway como:

```
python app.py
```

3. Railway detectará automáticamente el entorno Python y usará `requirements.txt` para instalar dependencias.
4. El servidor escuchará en el puerto definido por la variable de entorno `PORT`. Flask usará el puerto 3000 por defecto, pero Railway asigna un puerto dinámico, por lo que debes modificar `app.py` para usar `PORT` de entorno (ya está configurado para 3000, se puede ajustar).
5. Sube el proyecto a GitHub y despliega desde Railway.

## Ejecución local

1. Instala dependencias:

```
pip install -r requirements.txt
```

2. Ejecuta el servidor:

```
python app.py
```

3. Accede a `http://localhost:3000/master.html` para usar la aplicación.

## Notas

- Las imágenes subidas se almacenan en la carpeta `uploads`.
- La base de datos SQLite se crea en el archivo `database.sqlite`.
- Asegúrate de que la carpeta `uploads` tenga permisos de escritura.
