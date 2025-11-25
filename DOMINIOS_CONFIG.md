# Configuración de Dominios - Morphology Atlas

## 📋 Dominios Configurados

### Desarrollo
- **Dominio**: `dev.neuropedialab.org`
- **Puerto**: 8888
- **Descripción**: Entorno de desarrollo y pruebas

### Producción
- **Dominio**: `morpho.neuropedialab.org`
- **Puerto**: 80
- **Descripción**: Entorno de producción público

---

## 🌐 Configuración DNS

Para que los dominios funcionen, debes configurar los registros DNS:

### En tu proveedor de DNS (ej: Cloudflare, Route53, etc.)

#### Para Desarrollo (dev.neuropedialab.org)
```
Tipo: A
Nombre: dev
Valor: [IP_DEL_SERVIDOR]
TTL: 3600 (o automático)
```

#### Para Producción (morpho.neuropedialab.org)
```
Tipo: A
Nombre: morpho
Valor: [IP_DEL_SERVIDOR]
TTL: 3600 (o automático)
```

---

## 🚀 Deployment

### Desarrollo
```bash
chmod +x deploy.sh
./deploy.sh dev
```

### Producción
```bash
chmod +x deploy.sh
./deploy.sh prod
```

---

## 🔧 Configuración Manual

### Opción 1: Usar docker-compose directamente

**Desarrollo:**
```bash
docker-compose -f docker-compose.dev.yml up -d
```

**Producción:**
```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Opción 2: Usar docker-compose.yml (actual)
El archivo `docker-compose.yml` actual está configurado para desarrollo local (puerto 8888).
Para cambiar a producción, renombra los archivos:

```bash
mv docker-compose.yml docker-compose.local.yml
mv docker-compose.prod.yml docker-compose.yml
docker-compose up -d
```

---

## 🔒 Configuración SSL/HTTPS (Opcional pero Recomendado)

### Usando Certbot (Let's Encrypt)

1. **Instalar Certbot:**
```bash
sudo apt-get update
sudo apt-get install certbot python3-certbot-nginx
```

2. **Obtener certificado para desarrollo:**
```bash
sudo certbot --nginx -d dev.neuropedialab.org
```

3. **Obtener certificado para producción:**
```bash
sudo certbot --nginx -d morpho.neuropedialab.org
```

4. **Renovación automática:**
```bash
sudo certbot renew --dry-run
```

### Configuración Nginx con SSL

Modifica los archivos `nginx-dev.conf` y `nginx-prod.conf` para agregar:

```nginx
server {
    listen 443 ssl http2;
    server_name morpho.neuropedialab.org;
    
    ssl_certificate /etc/letsencrypt/live/morpho.neuropedialab.org/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/morpho.neuropedialab.org/privkey.pem;
    
    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    
    # ... resto de configuración ...
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name morpho.neuropedialab.org;
    return 301 https://$server_name$request_uri;
}
```

---

## 🧪 Pruebas

### Verificar que el contenedor está corriendo
```bash
docker ps | grep morphology-atlas
```

### Verificar salud del contenedor
```bash
docker inspect --format='{{.State.Health.Status}}' morphology-atlas-dev
```

### Ver logs
```bash
# Desarrollo
docker-compose -f docker-compose.dev.yml logs -f

# Producción
docker-compose -f docker-compose.prod.yml logs -f
```

### Probar localmente
```bash
# Desarrollo
curl http://localhost:8888

# Producción
curl http://localhost:80
```

### Probar con dominio (una vez configurado DNS)
```bash
curl http://dev.neuropedialab.org
curl http://morpho.neuropedialab.org
```

---

## 📊 Monitoreo

### Ver uso de recursos
```bash
docker stats morphology-atlas-dev
docker stats morphology-atlas-prod
```

### Ver información del contenedor
```bash
docker inspect morphology-atlas-dev
docker inspect morphology-atlas-prod
```

---

## 🔄 Actualización

Para actualizar la aplicación:

```bash
# 1. Pull los cambios más recientes
git pull

# 2. Re-deploy
./deploy.sh dev   # para desarrollo
./deploy.sh prod  # para producción
```

---

## 🛠️ Troubleshooting

### El contenedor no inicia
```bash
# Ver logs de error
docker-compose -f docker-compose.dev.yml logs

# Reiniciar contenedor
docker-compose -f docker-compose.dev.yml restart
```

### Puerto ya en uso
```bash
# Ver qué está usando el puerto
sudo lsof -i :8888
sudo lsof -i :80

# Detener proceso o cambiar puerto en docker-compose
```

### DNS no resuelve
```bash
# Verificar propagación DNS
nslookup dev.neuropedialab.org
dig dev.neuropedialab.org

# Forzar actualización DNS local
sudo systemd-resolve --flush-caches
```

### Problemas de permisos
```bash
# Dar permisos de ejecución al script
chmod +x deploy.sh

# Ejecutar con sudo si es necesario
sudo ./deploy.sh prod
```

---

## 📝 Notas Importantes

1. **Firewall**: Asegúrate de que los puertos 80 y 8888 estén abiertos en el firewall del servidor
   ```bash
   sudo ufw allow 80/tcp
   sudo ufw allow 8888/tcp
   ```

2. **SELinux**: Si usas SELinux, puede que necesites configurar contextos
   ```bash
   sudo semanage port -a -t http_port_t -p tcp 8888
   ```

3. **Backups**: Considera hacer backups regulares de:
   - Imágenes Docker: `docker save`
   - Datos y configuración: `/home/arkantu/docker/morphology-atlas/`

4. **Logs**: Los logs se rotan automáticamente (configurado en docker-compose.prod.yml)

---

## 🎯 Checklist de Deployment

### Pre-deployment
- [ ] Configurar registros DNS (A records)
- [ ] Abrir puertos en firewall
- [ ] Verificar espacio en disco
- [ ] Hacer backup de la versión actual

### Deployment
- [ ] Ejecutar `./deploy.sh [dev|prod]`
- [ ] Verificar que el contenedor está healthy
- [ ] Probar acceso local (http://localhost)
- [ ] Esperar propagación DNS (puede tardar hasta 48h)
- [ ] Probar acceso por dominio

### Post-deployment
- [ ] Configurar SSL/HTTPS (opcional pero recomendado)
- [ ] Configurar monitoreo
- [ ] Configurar backups automáticos
- [ ] Documentar cualquier cambio

---

## 📞 Soporte

Para problemas o preguntas:
- Revisar logs: `docker-compose logs -f`
- Verificar health: `docker inspect`
- Consultar documentación de Nginx
- Revisar configuración de DNS

---

## 🔗 URLs Finales

Una vez configurado todo:

- **Desarrollo**: http://dev.neuropedialab.org
- **Producción**: http://morpho.neuropedialab.org
- **Local (dev)**: http://localhost:8888
- **Local (prod)**: http://localhost:80
