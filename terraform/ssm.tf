resource "aws_ssm_parameter" "oura_api_token" {
  name  = "/oura-stats-texter/oura_api_token"
  type  = "SecureString"
  value = "PLACEHOLDER"

  lifecycle {
    ignore_changes = [value]
  }
}

resource "aws_ssm_parameter" "twilio_account_sid" {
  name  = "/oura-stats-texter/twilio_account_sid"
  type  = "SecureString"
  value = "PLACEHOLDER"

  lifecycle {
    ignore_changes = [value]
  }
}

resource "aws_ssm_parameter" "twilio_api_key_sid" {
  name  = "/oura-stats-texter/twilio_api_key_sid"
  type  = "SecureString"
  value = "PLACEHOLDER"

  lifecycle {
    ignore_changes = [value]
  }
}

resource "aws_ssm_parameter" "twilio_api_key_secret" {
  name  = "/oura-stats-texter/twilio_api_key_secret"
  type  = "SecureString"
  value = "PLACEHOLDER"

  lifecycle {
    ignore_changes = [value]
  }
}

resource "aws_ssm_parameter" "twilio_phone_number" {
  name  = "/oura-stats-texter/twilio_phone_number"
  type  = "String"
  value = "PLACEHOLDER"

  lifecycle {
    ignore_changes = [value]
  }
}

resource "aws_ssm_parameter" "recipient_phone_number" {
  name  = "/oura-stats-texter/recipient_phone_number"
  type  = "String"
  value = "PLACEHOLDER"

  lifecycle {
    ignore_changes = [value]
  }
}
