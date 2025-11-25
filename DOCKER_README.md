# 🐳 Morphology Atlas - Docker Guide

## Inicio Rápido con Docker

### Opción 1: Script Automático (Recomendado)

```bash
./start-docker.sh
```

Este script:
- ✅ Verifica que Docker esté instalado
- ✅ Construye la imagen Docker
- ✅ Arranca el contenedor
- ✅ Muestra la URL de acceso

### Opción 2: Comandos Manuales

```bash
# Construir y arrancar
docker-compose up -d --build

# Ver logs
docker-compose logs -f

# Detener
docker-compose stop

# Apagar y eliminar
docker-compose down
```

## 🌐 Acceso

Una vez arrancado, la aplicación estará disponible en:

**http://localhost:8080**

## 📋 Requisitos

- Docker >= 20.10
- docker-compose >= 1.29

### Instalar Docker

#### Linux (Ubuntu/Debian)
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

#### macOS
```bash
brew install --cask docker
```

#### Windows
Descarga Docker Desktop desde: https://www.docker.com/products/docker-desktop

## 🛠️ Comandos Útiles

### Ver estado del contenedor
```bash
docker-compose ps
```

### Ver logs en tiempo real
```bash
docker-compose logs -f
```

### Reiniciar el servicio
```bash
docker-compose restart
```

### Detener el contenedor
```bash
docker-compose stop
```

### Arrancar el contenedor (si está detenido)
```bash
docker-compose start
```

### Eliminar todo (contenedor e imagen)
```bash
docker-compose down
docker rmi morphology-atlas_morphology-atlas
```

### Acceder al contenedor
```bash
docker exec -it morphology-atlas sh
```

## 📦 Detalles Técnicos

### Imagen Base
- **nginx:alpine** - Servidor web ligero y eficiente
- Tamaño de imagen: ~180 MB

### Puerto
- **Host**: 8080
- **Container**: 80

### Volúmenes
No se utilizan volúmenes externos. Todo el contenido está embebido en la imagen.

### Healthcheck
El contenedor incluye un healthcheck que verifica cada 30 segundos que el servicio esté respondiendo.

## 🔧 Configuración Personalizada

### Cambiar el Puerto

Edita `docker-compose.yml`:

```yaml
ports:
  - "3000:80"  # Cambia 8080 por el puerto que prefieras
```

### Usar un Dominio Personalizado

Si tienes un dominio, configura un proxy inverso (nginx, traefik, etc.):

```nginx
server {
    listen 80;
    server_name tu-dominio.com;
    
    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 📊 Monitoreo

### Ver uso de recursos
```bash
docker stats morphology-atlas
```

### Ver logs con timestamps
```bash
docker-compose logs -f --timestamps
```

## 🚀 Producción

### Construir imagen optimizada
```bash
docker build -t morphology-atlas:latest .
```

### Ejecutar en producción
```bash
docker run -d \
  --name morphology-atlas \
  -p 80:80 \
  --restart always \
  morphology-atlas:latest
```

### Docker Swarm / Kubernetes

El proyecto es compatible con orquestadores. Ejemplos:

#### Docker Swarm
```bash
docker stack deploy -c docker-compose.yml morphology
```

#### Kubernetes (ejemplo básico)
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: morphology-atlas
spec:
  replicas: 3
  selector:
    matchLabels:
      app: morphology-atlas
  template:
    metadata:
      labels:
        app: morphology-atlas
    spec:
      containers:
      - name: morphology-atlas
        image: morphology-atlas:latest
        ports:
        - containerPort: 80
---
apiVersion: v1
kind: Service
metadata:
  name: morphology-atlas
spec:
  type: LoadBalancer
  ports:
  - port: 80
    targetPort: 80
  selector:
    app: morphology-atlas
```

## 🔒 Seguridad

### Mejores Prácticas Implementadas

1. ✅ Imagen base oficial de Alpine (mínima superficie de ataque)
2. ✅ Sin privilegios de root innecesarios
3. ✅ Healthcheck incluido
4. ✅ Sin secretos en la imagen

### Recomendaciones Adicionales

- Usa HTTPS en producción (con certificados Let's Encrypt)
- Implementa rate limiting
- Configura logs centralizados
- Mantén Docker actualizado

## 🐛 Troubleshooting

### El contenedor no arranca

```bash
# Ver logs detallados
docker-compose logs

# Verificar que el puerto 8080 esté libre
netstat -tulpn | grep 8080

# Limpiar y reconstruir
docker-compose down
docker-compose up --build
```

### Error de permisos

```bash
# En Linux, asegúrate de estar en el grupo docker
sudo usermod -aG docker $USER
newgrp docker
```

### La aplicación no carga los JSON

```bash
# Verificar que los archivos se copiaron correctamente
docker exec morphology-atlas ls -la /usr/share/nginx/html/data/organized/

# Verificar permisos
docker exec morphology-atlas ls -la /usr/share/nginx/html/
```

### Puerto ya en uso

```bash
# Cambiar el puerto en docker-compose.yml
# O detener el servicio que usa el puerto 8080
sudo lsof -ti:8080 | xargs kill -9
```

## 📝 Logs

Los logs de nginx se pueden ver con:

```bash
# Logs de acceso
docker exec morphology-atlas tail -f /var/log/nginx/access.log

# Logs de error
docker exec morphology-atlas tail -f /var/log/nginx/error.log
```

## 🔄 Actualización

Para actualizar la aplicación:

```bash
# 1. Detener y eliminar el contenedor actual
docker-compose down

# 2. Actualizar archivos del proyecto (git pull, etc.)

# 3. Reconstruir y arrancar
docker-compose up -d --build
```

## 💡 Tips

### Desarrollo con Live Reload

Para desarrollo, puedes montar el directorio local:

```yaml
services:
  morphology-atlas:
    volumes:
      - ./index.html:/usr/share/nginx/html/index.html
      - ./data:/usr/share/nginx/html/data
```

### Reducir tamaño de imagen

La imagen ya está optimizada con Alpine. Tamaño típico: ~180 MB

### Backup de datos

```bash
# Exportar datos
docker cp morphology-atlas:/usr/share/nginx/html/data ./backup-data

# Restaurar datos
docker cp ./backup-data morphology-atlas:/usr/share/nginx/html/data
```

## ✅ Verificación

Después de arrancar, verifica que todo funcione:

```bash
# Verificar que el contenedor está corriendo
docker-compose ps

# Verificar healthcheck
docker inspect morphology-atlas | grep Health -A 10

# Probar el endpoint
curl http://localhost:8080

# Probar que los JSON se cargan
curl http://localhost:8080/data/organized/summary.json
```

---

**🎉 ¡Listo! Tu Morphology Atlas está dockerizado y corriendo.**

Para más información, consulta [README.md](README.md)
