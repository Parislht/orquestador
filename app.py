
from fastapi import FastAPI, HTTPException, Body
import requests

app = FastAPI()

# Nombre de servicios según docker-compose
USUARIOS_SERVICE = "http://usuarios_service:8000"
LIBROS_SERVICE = "http://libros_service:8080"
RESENA_SERVICE = "http://resena_service:3000"

@app.post("/prestamo_libro")
def prestar_libro(data: dict = Body(...)):
    id_usuario = data.get("id_user")
    id_libro = data.get("id_libro")

    # Obtener usuario y libro
    usuario_resp = requests.get(f"{USUARIOS_SERVICE}/usuarios/{id_usuario}")
    if usuario_resp.status_code != 200:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    usuario = usuario_resp.json()

    libro_resp = requests.get(f"{LIBROS_SERVICE}/libros/{id_libro}")
    if libro_resp.status_code != 200:
        raise HTTPException(status_code=404, detail="Libro no encontrado")
    libro = libro_resp.json()

    # Validaciones
    if usuario["n_prestamo"] >= 1:
        raise HTTPException(status_code=400, detail="El usuario ya tiene un préstamo activo.")
    if not libro["disponible"]:
        raise HTTPException(status_code=400, detail="El libro no está disponible.")

    # Actualizar estado del libro (disponible = false)
    requests.patch(f"{LIBROS_SERVICE}/libros/{id_libro}", json={"disponible": False})

    # Actualizar usuario (n_prestamo = 1)
    requests.patch(f"{USUARIOS_SERVICE}/usuarios/{id_usuario}", json={"n_prestamo": 1})

    return {"mensaje": "Préstamo realizado con éxito."}

@app.post("/resena_libro")
def crear_resena(data: dict = Body(...)):
    id_usuario = data.get("id_user")
    id_libro = data.get("id_libro")
    comentario = data.get("comentario")
    puntuacion = data.get("puntuacion")
    fecha = data.get("fecha")

    # Obtener usuario y libro
    usuario_resp = requests.get(f"{USUARIOS_SERVICE}/usuarios/{id_usuario}")
    if usuario_resp.status_code != 200:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    usuario = usuario_resp.json()

    libro_resp = requests.get(f"{LIBROS_SERVICE}/libros/{id_libro}")
    if libro_resp.status_code != 200:
        raise HTTPException(status_code=404, detail="Libro no encontrado")
    libro = libro_resp.json()

    # Validaciones
    if usuario["n_resena"] >= 5:
        raise HTTPException(status_code=400, detail="El usuario ya tiene el máximo de reseñas permitidas.")

    # Si puntuación libro == 0, se queda con la nueva puntuación enviada
    if libro["puntuacion"] == 0:
        requests.patch(f"{LIBROS_SERVICE}/libros/{id_libro}", json={"puntuacion": puntuacion})

    # Crear la reseña en microservicio 3
    nueva_resena = {
        "id_libro": id_libro,
        "id_usuario": id_usuario,
        "comentario": comentario,
        "puntuacion": puntuacion,
        "fecha": fecha
    }
    res = requests.post(f"{RESENA_SERVICE}/resenas", json=nueva_resena)
    if res.status_code != 201:
        raise HTTPException(status_code=500, detail="Error al registrar la reseña")

    return {"mensaje": "Reseña registrada con éxito."}

@app.post("/crear_libro")
def crear_libro(data: dict = Body(...)):
    res = requests.post(f"{LIBROS_SERVICE}/libros", json=data)
    if res.status_code != 201:
        raise HTTPException(status_code=500, detail="Error al crear libro")
    return {"mensaje": "Libro creado correctamente"}

@app.post("/crear_editorial")
def crear_editorial(data: dict = Body(...)):
    res = requests.post(f"{LIBROS_SERVICE}/editoriales", json=data)
    if res.status_code != 201:
        raise HTTPException(status_code=500, detail="Error al crear editorial")
    return {"mensaje": "Editorial creada correctamente"}

@app.post("/crear_categoria")
def crear_categoria(data: dict = Body(...)):
    res = requests.post(f"{LIBROS_SERVICE}/categorias", json=data)
    if res.status_code != 201:
        raise HTTPException(status_code=500, detail="Error al crear categoría")
    return {"mensaje": "Categoría creada correctamente"}
