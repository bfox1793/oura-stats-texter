resource "aws_ssm_parameter" "oura_api_token" {
  name  = "/oura-stats-texter/oura_api_token"
  type  = "SecureString"
  value = "PLACEHOLDER"

  lifecycle {
    ignore_changes = [value]
  }
}
