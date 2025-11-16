# 🛒 Sistema de Venta 
![Python 3.12+](https://img.shields.io/badge/Python-3.12+-blue.svg)
![Django 5.0+](https://img.shields.io/badge/Django-5.0+-green.svg)

## 🚀 Descripción del Proyecto
Este es un **Sistema de Venta** integral desarrollado con **Django**, diseñado para la administración de productos, clientes y ventas.

El proyecto se enfoca en la **robustez** y la **seguridad**, implementando:
1.  **Trazabilidad de Stock:** Control detallado de movimientos e inventario mínimo.
2.  **Autenticación Avanzada:** Gestión de usuarios con `django-allauth` y permisos basados en grupos (`stock`, `ventas`, `admin`).
3.  **Contenedorización:** Despliegue en producción utilizando **Docker** y **PostgreSQL**.
4.   Generación de **Comprobantes PDF** (`xhtml2pdf`). 

---
## 🛠️ Tecnologías Utilizadas

* **Backend:** Python 3.13.5, Django 5.0+
* **Base de Datos (Producción):** PostgreSQL 15
* **Front-end:** Bootstrap 4 (vía `crispy-forms`)
* **Seguridad:** `django-allauth`
* **Documentación:** `xhtml2pdf` (para comprobantes)
* **Contenerización:** Docker y `docker-compose`

---

## ⚙️ Instalación y Despliegue con Docker

El proyecto utiliza Docker para asegurar un entorno de ejecución consistente.

### 1. Requerimientos Previos
Asegúrate de tener instalado **Docker Desktop** (para Windows/Mac) o **Docker Engine** (para Linux).

### 2. Configuración Inicial
1.  **Clonar el repositorio:**
    ```bash
    git clone https://github.com/AbdiasMQ/Practico-final-
    cd systemventas
    ```
2.  **Crear archivo `.env`:** Copia el archivo de variables de entorno de ejemplo (`.env.ejemplo`) y complétalo con las credenciales de PostgreSQL (las usadas en `docker-compose.yml`).
    ```bash
    cp .env.example .env 
    ```

### 3. Levantar Contenedores
Este comando construye la imagen de la aplicación (`Dockerfile`), crea la red y levanta el servicio web y la base de datos (`db`).
```bash
docker-compose up --build -d

```
## 💾 Inicialización y Carga de Base de Datos

Una vez que los contenedores (`web` y `db`) estén levantados con `docker-compose up --build -d`, es fundamental aplicar la estructura de la base de datos (migraciones) y cargar los datos iniciales.

### Comandos de Inicialización

Todos estos comandos deben ejecutarse dentro del contenedor `web`:

```bash
# 1. Aplicar las migraciones para crear las tablas
docker-compose exec web python manage.py migrate

# 2. Crear superusuario (para acceder al /admin)
docker-compose exec web python manage.py createsuperuser

# 3. Cargar datos de prueba de clientes y productos
docker-compose exec web python manage.py loaddata backup_convertido.json

```
## 🔑 Autenticación y Permisos

El sistema implementa un robusto control de acceso utilizando **`django-allauth`** para la gestión de cuentas y el sistema nativo de **Grupos y Permisos** de Django para la autorización.

### Estructura de Grupos y Permisos

| Grupo | Apps/Permisos Asignados | Alcance Funcional |
| :--- | :--- | :--- |
| **admin** | Permisos totales (Superusuario). | Acceso administrativo completo. |
| **stock** | Permisos de la App **productos**. | Gestión de inventario, creación/edición de productos y movimientos de stock. |
| **ventas** | Permisos de las Apps **clientes** y **ventas**. | Gestión de clientes, registro de ventas y generación de comprobantes PDF. |

> **Nota de Seguridad:** Un usuario en el grupo **'ventas'** que intente acceder a una URL de modificación de stock recibirá un error **HTTP 403 (Prohibido)**.
