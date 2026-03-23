resource "aws_ssm_parameter" "oura_api_token" {
  name  = "/oura-stats-texter/oura_api_token"
  type  = "SecureString"
  value = "PLACEHOLDER"

  lifecycle {
    ignore_changes = [value]
  }
}

resource "aws_ssm_parameter" "sms_gateway_email" {
  name  = "/oura-stats-texter/sms_gateway_email"
  type  = "String"
  value = "7277428426@txt.att.net"
}

resource "aws_ssm_parameter" "sender_email" {
  name  = "/oura-stats-texter/sender_email"
  type  = "String"
  value = "PLACEHOLDER"

  lifecycle {
    ignore_changes = [value]
  }
}
