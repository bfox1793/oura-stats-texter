resource "aws_ssm_parameter" "oura_api_token" {
  name  = "/oura-stats-texter/oura_api_token"
  type  = "SecureString"
  value = "PLACEHOLDER"

  lifecycle {
    ignore_changes = [value]
  }
}

resource "aws_ssm_parameter" "telegram_bot_token" {
  name  = "/oura-stats-texter/telegram_bot_token"
  type  = "SecureString"
  value = "PLACEHOLDER"

  lifecycle {
    ignore_changes = [value]
  }
}

resource "aws_ssm_parameter" "telegram_chat_id" {
  name  = "/oura-stats-texter/telegram_chat_id"
  type  = "String"
  value = "PLACEHOLDER"

  lifecycle {
    ignore_changes = [value]
  }
}
