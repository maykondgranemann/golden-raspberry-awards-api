provider "google" {
  credentials = file("/tmp/gcp-sa-key.json")
  project     = "golden-raspberry-awards-api"
  region      = "us-central1"
}

# 🔍 Verifica se o cluster já existe
data "google_container_cluster" "existing" {
  name     = "golden-cluster"
  location = "us-central1"
}

# Cria o cluster apenas se ele ainda não existir
resource "google_container_cluster" "primary" {
  count    = length(data.google_container_cluster.existing.name) > 0 ? 0 : 1
  name     = "golden-cluster"
  location = "us-central1"

  initial_node_count = 1  # Necessário para evitar erro

  lifecycle {
    prevent_destroy = true  # Evita que o cluster seja deletado sem querer
    ignore_changes = [
      node_pool,           
      initial_node_count,  
    ]
  }
}
