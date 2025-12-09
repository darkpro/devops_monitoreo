# Plataforma local de CI/CD, Observabilidad y Seguridad

## 1. Descripción general

Este proyecto implementa una infraestructura local en Linux Mint que permite:

- Ejecutar una aplicación web en contenedores Docker.
- Integrarla a un pipeline CI/CD con GitHub Actions.
- Habilitar monitoreo y observabilidad con Prometheus, Grafana, Elasticsearch, Kibana y Filebeat.
- Aplicar prácticas de seguridad (DevSecOps) como gestión de secretos y escaneo de vulnerabilidades.
- Simular un entorno de operación en producción, incluyendo tolerancia a fallos y balanceador de carga local.

Toda la solución funciona en infraestructura local, sin depender de servicios en la nube pública.

## 2. Arquitectura general

Servicios principales:

- **App (Flask)**: API sencilla que expone `/` y `/metrics`.
- **NGINX**: Balanceador de carga local que expone la app en `http://localhost:8080`.
- **Prometheus**: Recolección de métricas de la app y del propio Prometheus.
- **Grafana**: Visualización de dashboards de métricas.
- **Elasticsearch + Kibana + Filebeat (ELK)**: Recolección, almacenamiento y visualización de logs de contenedores.
- **Vault**: Gestión local de secretos.
- **GitHub Actions + Trivy**: Pipeline CI/CD con escaneo de vulnerabilidades.

Diagrama simplificado:

```mermaid
flowchart LR
    U[Usuario] --> N[NGINX<br/>localhost:8080]
    N --> A[App Flask (Docker)]
    A -->|logs| FB[Filebeat]
    FB --> ES[Elasticsearch]
    ES --> K[Kibana]

    A -->|/metrics| P[Prometheus]
    P --> G[Grafana]

    V[Vault]:::sec

classDef sec fill=#ffdddd,stroke=#aa0000,stroke-width=1px;
```mermaid

3. Instrucciones de despliegue en Linux Mint
3.1. Requisitos previos

Linux Mint

Docker y Docker Compose

Git

Trivy

Vault (opcional, recomendado)

3.2. Clonar y levantar la infraestructura
git clone https://github.com/darkpro/devops_monitoreo.git
cd devops_monitoreo

# Levantar todos los servicios
docker compose up -d --build


Servicios expuestos:

App detrás de NGINX: http://localhost:8080/

Prometheus: http://localhost:9090/

Grafana: http://localhost:3000/ (usuario/clave por defecto: admin/admin)

Kibana: http://localhost:5601/

Elasticsearch: http://localhost:9200/

Vault (servidor local, fuera de Docker): http://localhost:8200/

3.3. Escalar la aplicación (simulación de producción)

docker compose up -d --scale app=2


Con esto se crean múltiples instancias de la app y NGINX actúa como balanceador de carga.

4. Observabilidad y monitoreo
4.1. Métricas con Prometheus y Grafana

La aplicación Flask expone métricas Prometheus en /metrics utilizando prometheus_flask_exporter.
Prometheus está configurado en observabilidad/prometheus.yml para scrapear:

prometheus:9090

app:5000/metrics

Además, se define un archivo de reglas observabilidad/alert_rules.yml con una alerta básica:

AppInstanceDown: se dispara cuando el job app no está disponible durante más de 1 minuto.

En Grafana se pueden crear dashboards usando Prometheus como data source para visualizar:

Número de peticiones.

Latencia.

Estado de las instancias de la app.

4.2. Logs con ELK (Elasticsearch, Logstash/Filebeat, Kibana)

Filebeat está configurado en elk/filebeat.yml para:

Leer los logs de todos los contenedores en /var/lib/docker/containers/*/*.log.

Enviar los logs a Elasticsearch en elasticsearch:9200.

Integrarse con Kibana en kibana:5601.

En Kibana se puede:

Configurar un índice filebeat-*.

Explorar los logs de la aplicación y del resto de servicios.

5. Seguridad en DevOps (DevSecOps)
5.1. Gestión de secretos con Vault

Vault se levanta con la configuración security/vault-config.hcl:

Escucha en 0.0.0.0:8200 sin TLS para entorno local de pruebas.

Usa almacenamiento en disco (/vault/data).

Los secretos sensibles (por ejemplo, claves de API o credenciales de base de datos) se gestionan en Vault y no se almacenan en el repositorio.
Para la demostración, se puede crear un secreto de ejemplo:

export VAULT_ADDR='http://127.0.0.1:8200'
vault login <TOKEN_INICIAL>
vault kv put secret/app DB_PASSWORD=supersecreto

5.2. Escaneo de vulnerabilidades con Trivy

Se utiliza Trivy tanto de forma local como dentro del pipeline CI/CD:

Escaneo local:

docker build -t proyecto-final_app:latest ./app
trivy image proyecto-final_app:latest


Pipeline GitHub Actions (.github/workflows/ci.yml):

Construye la imagen app-ci.

Ejecuta aquasecurity/trivy-action con severidades CRITICAL,HIGH.

Falla el pipeline si se detectan vulnerabilidades graves.

Esto asegura que no se desplieguen imágenes con vulnerabilidades críticas.

5.3. Hardening básico

Los servicios se ejecutan en una red Docker aislada (monitoreo).

No se exponen puertos innecesarios.

La gestión de secretos se externaliza a Vault.

Se aplica reinicio automático (restart: always) en la app para mejorar la resiliencia.

6. Operaciones en producción (simulación local)
6.1. Gestión de fallos y reinicios automáticos

El servicio app en docker-compose.yml incluye:

restart: always


Prueba realizada:

Levantar la infraestructura:

docker compose up -d


Verificar el contenedor:

docker ps


Simular una caída:

docker stop proyecto-final-app-1


Docker reinicia automáticamente el contenedor debido a la política restart: always.

6.2. Balanceador de carga local

NGINX se configura como balanceador de carga hacia el servicio app:

nginx.conf:

events {}

http {
    upstream backend {
        server app:5000;
    }

    server {
        listen 80;

        location / {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
    }
}


Al escalar la aplicación con:

docker compose up -d --scale app=2


NGINX reparte las peticiones entre las distintas instancias.
La ruta http://localhost:8080/ devuelve un JSON donde se muestra el hostname del contenedor, permitiendo verificar el balanceo.

7. CI/CD

El pipeline CI/CD se define en .github/workflows/ci.yml:

Se ejecuta en cada push a la rama main.

Pasos:

checkout del repositorio.

Construcción de la imagen Docker de la app.

Escaneo de vulnerabilidades con Trivy.

Bloqueo del pipeline si se detectan vulnerabilidades CRITICAL o HIGH.

En un escenario extendido, este pipeline podría incluir:

Ejecución de tests automatizados.

Publicación de la imagen en un registry local.

Despliegue automatizado en el entorno local.
