# 📦 Event Club - Sistema de Gestión de Inventario y Eventos

Una solución integral y ligera diseñada para la gestión logística de alquileres, control de inventario en tiempo real y reportes operativos. Ideal para empresas de eventos que necesitan sincronización inmediata entre el equipo de ventas, bodega y campo.

## ✨ Características Principales

* **Panel de Administración:** Visualización de stock global, control de artículos dañados y agenda interactiva (FullCalendar).
* **Gestión de Ventas:** Interfaz intuitiva para registrar pedidos, calcular totales automáticamente y asignar métodos de pago.
* **Monitor de Campo:** Vista optimizada para empleados con actualización automática (Live Polling) para entregas y retiros sin refrescar la página.
* **Reportes PDF:** Generación instantánea de comprobantes individuales y reportes de caja diarios con balance de ingresos.
* **Base de Datos Segura:** Implementación robusta con SQLite para un manejo de datos rápido y confiable.

##  Tecnologías Utilizadas

* **Backend:** Python 3.x + Flask
* **Frontend:** Bootstrap 5, JavaScript (ES6+), FullCalendar API
* **PDF Engine:** jsPDF & AutoTable
* **Base de Datos:** SQLite3

##  Instalación y Ejecución

Sigue estos pasos para poner en marcha el proyecto en tu entorno local:

### 1. Clonar el repositorio
git clone [https://github.com/tu-usuario/event-club.git](https://github.com/tu-usuario/event-club.git)
cd event-club

## Instalar dependencias
Asegúrate de tener Python instalado. Se recomienda usar un entorno virtual:

Bash
pip install flask
3. Configurar la Base de Datos
El sistema inicializa automáticamente la base de datos eventos.db al ejecutarse por primera vez si no existe.

4. Ejecutar la aplicación
Bash
python app.py
La aplicación estará disponible en: http://127.0.0.1:5000

 Estructura del Proyecto
app.py: Servidor Flask y rutas de la API.

templates/: Archivos HTML (index, vendedor, empleado).

static/: Archivos CSS, imágenes y scripts JS personalizados.

eventos.db: Base de Datos SQLite (se genera automáticamente).
