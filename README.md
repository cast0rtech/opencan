# ⚡ SolarHub EMS

> Monitor de telemetría y gestor energético local para inversores **Fronius**, **Huawei SUN2000**, **SMA**, **SolarEdge** y sistemas **Victron Energy (Cerbo GX / Venus OS)** mediante Modbus TCP/RTU. Ligero, reactivo y empaquetado para arquitecturas **x86_64**, **ARM64** y **ARMv7** (Raspberry Pi, Debian, RHEL/Rocky, Ubuntu y Windows).

[![Docker Multi-Arch](https://img.shields.io/badge/docker-multi--arch%20(amd64%2C%20arm64%2C%20armv7)-blue?logo=docker)](#)
[![Python](https://img.shields.io/badge/python-3.11+-yellow?logo=python)](#)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

---

## 📋 Características

- **Adquisición Asíncrona:** Worker Modbus no bloqueante con reconexión automática y tolerancia a fallos.
- **Soporte Multi-Fabricante:** Drivers polimórficos para Fronius, Huawei SUN2000, SMA (Speedwire), SolarEdge (SunSpec) y Victron GX (Systemcalc / VE.Bus).
- **Dashboard en Tiempo Real:** Interfaz web industrial con actualización continua mediante WebSockets (baja latencia).
- **Consumo Mínimo de Recursos:** Optimizado para microordenadores (Raspberry Pi 3/4/5) y servidores locales.
- **Portabilidad Total:** Contenedor Docker listo para producción compatible con políticas SELinux (RHEL/Rocky/Fedora) y Debian/Ubuntu.

---

## 🌟 Key Highlights of this Setup

- **SELinux & Permission Resilience:** The `:Z` flags in `docker-compose.yml` make the container work seamlessly out of the box on Red Hat Enterprise Linux, Rocky Linux, and Fedora without permission errors on the volumes.
- **Resource Constraints:** Strict CPU and memory limits (512M cap) ensure the container remains lightweight on low-power devices such as the Raspberry Pi 3/4.
- **Independent Device Architecture:** Each of the 5 inverters has its own definition with manufacturer-specific communication requirements (e.g., SolarEdge's common port 1502, SMA's Unit ID 3, and Victron's multi-unit dispatching across 100 and 228). If one device goes offline, the remaining four will continue polling without delay.

---

## 🛠 Requisitos Previos

### 1. Inversor Fronius
- Conexión a la red local (vía Ethernet o Wi-Fi con Datamanager o Pilot).
- En la interfaz local del inversor (`http://<IP_FRONIUS>`):
  1. Ve a **Comunicación** → **Modbus**.
  2. Protocolo: selecciona **Modbus TCP**.
  3. Tipo de datos: selecciona **SunSpec (float)** o **SunSpec (int + SF)** según prefieras.
  4. Puerto por defecto: `502`.

### 2. Inversor Huawei SUN2000
- Conectado a la LAN mediante **SDongleA-05** (Fast Ethernet o WLAN) o conexión RS-485 directa a SmartLogger/Gateway.
- Habilitar Modbus TCP en la app FusionSolar (con cuenta de instalador):
  1. Conéctate a la Wi-Fi local del inversor/dongle.
  2. **Configuración de parámetros** → **Conexión de red** → **Modbus TCP**.
  3. Establecer en **Habilitar (Ilimitado)** o restringir a la IP del servidor donde corre esta aplicación.
  4. Puerto por defecto: `502` (o `6607` si te conectas a la Wi-Fi interna del inversor).

---

## 🚀 Despliegue Rápido con Docker

La forma recomendada de ejecutar SolarHub en cualquier distribución Linux (Debian, Raspberry Pi OS, Ubuntu, RHEL) o PC de escritorio.

### 1. Clonar el repositorio
```bash
git clone https://github.com/tu-usuario/solarhub-ems.git
cd solarhub-ems
```

### 2. Configurar los inversores
Edita el archivo `config.yaml` con las direcciones IP y parámetros de tu instalación:
```bash
cp config.example.yaml config.yaml
nano config.yaml
```

### 3. Iniciar el servicio
```bash
docker compose up -d
```

Accede al dashboard en tu navegador web en: `http://localhost:8080` (o la IP local del equipo).
