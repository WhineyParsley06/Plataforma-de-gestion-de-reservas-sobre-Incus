# OpenTofu - Infraestructura Incus

Este directorio contiene la infraestructura como código del proyecto
"Plataforma de gestión de reservas sobre Incus".

## Qué automatiza

- Creación de la red `reservas-net`.
- Creación del perfil `reservas-profile`.
- Creación/verificación de contenedores:
  - node-control
  - app-api
  - app-core
  - db-postgres
  - monitoring
  - ceph-node
- Asignación de IPs fijas en la red 10.10.0.0/24.

## Comandos

```bash
tofu init
tofu plan
tofu apply

