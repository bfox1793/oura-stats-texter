resource "aws_ssm_parameter" "oura_api_token" {
  name  = "/oura-stats-texter/oura_api_token"
  type  = "SecureString"
  value = "PLACEHOLDER"

  lifecycle {
    ignore_changes = [value]
  }
}

resource "aws_ssm_parameter" "discord_webhook_url" {
  name  = "/oura-stats-texter/discord_webhook_url"
  type  = "SecureString"
  value = "PLACEHOLDER"

  lifecycle {
    ignore_changes = [value]
  }
}

resource "aws_ssm_parameter" "discord_public_key" {
  name  = "/oura-stats-texter/discord_public_key"
  type  = "String"
  value = "PLACEHOLDER"

  lifecycle {
    ignore_changes = [value]
  }
}
