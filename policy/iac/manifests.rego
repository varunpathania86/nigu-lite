package main

import rego.v1

deny contains finding if {
  input.environment == "production"
  input.dns.provider != "cloudflare"
  finding := "production manifests require Cloudflare DNS"
}

deny contains finding if {
  input.environment == "production"
  input.tls.mode != "letsencrypt"
  finding := "production manifests require Let's Encrypt TLS"
}

deny contains finding if {
  input.product == "edu"
  not input.apps == ["gibbon"]
  finding := "edu tenants must select only Gibbon"
}

deny contains finding if {
  input.product == "erp"
  not input.apps == ["erpnext"]
  finding := "ERP tenants must select only ERPNext"
}
