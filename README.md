# course-info-python

API REST desarrollada con **FastAPI**, usando el módulo `sqlite3` incorporado

de Python (sin ORM). Implementa gestión de **Cursos**, **Autores** y

**Calificaciones (Grades)**, con autenticación y autorización mediante

**JWT**.

Repositorio: [https://github.com/Radagart/INTSISTP1](https://github.com/Radagart/INTSISTP1)

Proyecto base: [https://gitlab.com/agimenezpy/course-info-python](https://gitlab.com/agimenezpy/course-info-python)

## Requisitos

- Python 3.11 o superior

- pip

## Instalación

```bash

python -m venv .venv

# Windows

.venv\Scripts\Activate.ps1

# macOS / Linux

source .venv/bin/activate

pip install -r requirements.txt

```

## Ejecución

```bash

uvicorn app.main:app --reload

```

La API queda disponible en `http://127.0.0.1:8000`.

Documentación interactiva (Swagger UI): `http://127.0.0.1:8000/docs`

Por defecto la app guarda los datos en `./courses.db`. Se puede cambiar la

ubicación con la variable de entorno:

```bash

COURSE_INFO_DATABASE=/ruta/a/courses.db uvicorn app.main:app --reload

```

### Clave secreta para JWT (producción)

Para firmar los tokens JWT se usa una clave secreta. En desarrollo se usa un

valor por defecto, pero en un entorno real **se debe definir**:

```bash

COURSE_INFO_SECRET_KEY="una-clave-secreta-propia-y-larga" uvicorn app.main:app --reload

```

## Pruebas

```bash

pytest

```

## Endpoints principales

### Autenticación `/auth`)

| Método | Ruta             | Descripción                                  | Requiere token |

|--------|------------------|-----------------------------------------------|:--------------:|

| POST   | `/auth/register` | Registra un nuevo usuario                     | No             |

| POST   | `/auth/login`    | Inicia sesión y devuelve un token JWT         | No             |

`/auth/login` recibe `username` y `password` como formulario

`application/x-www-form-urlencoded`), siguiendo el estándar OAuth2 usado por

FastAPI. Devuelve:

```json

{

  "access_token": "<token>",

  "token_type": "bearer"

}

```

### Cursos `/courses`)

| Método | Ruta                        | Requiere token |

|--------|-----------------------------|:--------------:|

| GET    | `/courses`                  | No             |

| GET    | `/courses/{course_id}`      | No             |

| POST   | `/courses/`                 | **Sí**         |

| PUT    | `/courses/{course_id}`      | **Sí**         |

| DELETE | `/courses/{course_id}`      | **Sí**         |

| POST   | `/courses/{course_id}/notes`| **Sí**         |

### Autores `/authors`)

| Método | Ruta                  | Requiere token |

|--------|-----------------------|:--------------:|

| GET    | `/authors`             | No             |

| GET    | `/authors/{handle}`    | No             |

### Calificaciones `/grades`)

| Método | Ruta                   | Requiere token |

|--------|------------------------|:--------------:|

| GET    | `/grades`              | No             |

| GET    | `/grades/{grade_id}`   | No             |

| POST   | `/grades/`             | **Sí**         |

| PUT    | `/grades/{grade_id}`   | **Sí**         |

| DELETE | `/grades/{grade_id}`   | **Sí**         |

## Cómo probar la autenticación en Swagger

1. Ir a `http://127.0.0.1:8000/docs`.

2. Registrar un usuario con `POST /auth/register` `username` y `password`).

3. Hacer clic en el botón **Authorize** (arriba a la derecha) e ingresar el

   mismo `usernamepassword`.

4. A partir de ese momento, todos los endpoints protegidos van a incluir el

   token automáticamente en cada petición.

## Notas de diseño de seguridad

- Las contraseñas nunca se guardan en texto plano: se almacenan hasheadas

  con `bcrypt` (a través de `passlib`).

- Los tokens JWT se firman con el algoritmo `HS256` y expiran a los 30

  minutos.

- Se protegieron únicamente los endpoints que modifican datos `POST`,

  `PUT`, `DELETE`); los `GET` permanecen públicos, siguiendo un criterio

  habitual en APIs REST (lectura abierta, escritura autenticada).

  ## Evidencias de funcionamiento

En la carpeta `evidencias/` se incluyen capturas de pantalla que muestran:

- Documentación Swagger con los endpoints de Courses, Authors y Grades.
- Pruebas del CRUD de Grades (creación, lectura, actualización, borrado).
- Registro de usuario y obtención de token JWT mediante login.
- Verificación de que los endpoints de escritura requieren autenticación
  (401 sin token, 204 con token válido).
- Ejecución de la suite de tests automáticos (`pytest`).