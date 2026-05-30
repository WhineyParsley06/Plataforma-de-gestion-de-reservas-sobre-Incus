terraform {
  required_version = ">= 1.6.0"
}

locals {
  network_name = "reservas-net"
  profile_name = "reservas-profile"

  containers = {
    node-control = {
      ip = "10.10.0.5"
    }
    app-api = {
      ip = "10.10.0.10"
    }
    app-core = {
      ip = "10.10.0.11"
    }
    db-postgres = {
      ip = "10.10.0.12"
    }
    monitoring = {
      ip = "10.10.0.13"
    }
    ceph-node = {
      ip = "10.10.0.14"
    }
  }
}

resource "terraform_data" "incus_network" {
  input = {
    name = local.network_name
  }

  provisioner "local-exec" {
    command = <<EOC
set -e

if incus network list --format csv | grep -q "^${self.input.name},"; then
  echo "La red ${self.input.name} ya existe."
else
  echo "Creando red ${self.input.name}"
  incus network create ${self.input.name} ipv4.address=10.10.0.1/24 ipv4.nat=true ipv6.address=none
fi
EOC
  }
}

resource "terraform_data" "incus_profile" {
  depends_on = [terraform_data.incus_network]

  input = {
    profile = local.profile_name
    network = local.network_name
  }

  provisioner "local-exec" {
    command = <<EOC
set -e

if incus profile list --format csv | grep -q "^${self.input.profile},"; then
  echo "El perfil ${self.input.profile} ya existe."
else
  echo "Creando perfil ${self.input.profile}"
  incus profile create ${self.input.profile}
fi

if ! incus profile device list ${self.input.profile} | grep -q "^root"; then
  incus profile device add ${self.input.profile} root disk path=/ pool=default
fi

if ! incus profile device list ${self.input.profile} | grep -q "^eth0"; then
  incus profile device add ${self.input.profile} eth0 nic name=eth0 network=${self.input.network}
fi
EOC
  }
}

resource "terraform_data" "incus_containers" {
  depends_on = [terraform_data.incus_profile]

  for_each = local.containers

  input = {
    name    = each.key
    ip      = each.value.ip
    profile = local.profile_name
  }

  provisioner "local-exec" {
    command = <<EOC
set -e

NAME="${self.input.name}"
IP="${self.input.ip}"
PROFILE="${self.input.profile}"

if incus list "$NAME" --format csv | grep -q "^$NAME,"; then
  echo "El contenedor $NAME ya existe."
else
  echo "Creando contenedor $NAME"
  incus launch images:ubuntu/24.04 "$NAME" -p "$PROFILE"
fi

echo "Asignando IP fija $IP a $NAME"
incus config device override "$NAME" eth0 ipv4.address="$IP" || true

echo "Iniciando $NAME si está detenido"
incus start "$NAME" 2>/dev/null || true
EOC
  }
}

output "contenedores" {
  value = local.containers
}
