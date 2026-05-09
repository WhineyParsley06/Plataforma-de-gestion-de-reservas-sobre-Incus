variable "containers" {
  type = map(object({
    ip = string
  }))

  default = {
    "node-control" = {
      ip = "10.10.0.5"
    }

    "app-api" = {
      ip = "10.10.0.10"
    }

    "app-core" = {
      ip = "10.10.0.11"
    }

    "db-postgres" = {
      ip = "10.10.0.12"
    }

    "monitoring" = {
      ip = "10.10.0.20"
    }

    "ceph-node" = {
      ip = "10.10.0.30"
    }
  }
}
