# 🛒 Sistema de Venta 
![Python 3.12+](https://img.shields.io/badge/Python-3.12+-blue.svg)
![Django 5.0+](https://img.shields.io/badge/Django-5.0+-green.svg)

## 🚀 Descripción del Proyecto
Este es un **Sistema de Venta** integral desarrollado con **Django**, diseñado para la administración de productos, clientes y ventas.

El proyecto se enfoca en la **robustez** y la **seguridad**, implementando:
1.  **Trazabilidad de Stock:** Control detallado de movimientos e inventario mínimo.
2.  **Autenticación Avanzada:** Gestión de usuarios con `django-allauth` y permisos basados en grupos (`stock`, `ventas`, `admin`).
3.  **Contenedorización:** Despliegue en producción utilizando **Docker** y **PostgreSQL**.

---

## ✨ Características y Funcionalidades Clave

| Módulo | Descripción | Funcionalidades Notables |
| :--- | :--- | :--- |
| **Productos** | Gestión del producto y el inventario. | Alerta automática de **Stock Mínimo**. Registro de `MovimientoStock` (Entrada/Salida). |
| **Ventas** | Registro de transacciones y generador de pdf. | Cálcula el total de una venta. Generación de **Comprobantes PDF** (`xhtml2pdf`). 
| **Clientes** | Base de datos de clientes. | Validación de unicidad de **DNI**. Vistas con paginación y búsqueda. |
| **Seguridad** | Control de acceso basado en roles. | Uso de `LoginRequiredMixin` y `PermissionRequiredMixin`. Implementación de Grupos para roles (`stock`, `ventas`, 'admin). |
| **Infraestructura** | Entorno de desarrollo/producción. | **Dockerización** de la aplicación y la BD **PostgreSQL** mediante `docker-compose`. |

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
