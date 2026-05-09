terraform {
  required_version = ">= 1.6.0"
}

resource "terraform_data" "incus_containers" {
  for_each = var.containers

  input = {
    name = each.key
    ip   = each.value.ip
  }

  provisioner "local-exec" {
    command = <<EOC
set -e

NAME="${self.input.name}"
IP="${self.input.ip}"

echo "==> Verificando contenedor $NAME"

if incus list "$NAME" --format csv | grep -q "$NAME"; then
  echo "El contenedor $NAME ya existe. No se modifica."
else
  echo "Creando contenedor $NAME"
  incus launch images:ubuntu/24.04 "$NAME"
  incus config device override "$NAME" eth0 ipv4.address="$IP"
  incus restart "$NAME"
  echo "Contenedor $NAME creado con IP $IP"
fi
EOC
  }
}
