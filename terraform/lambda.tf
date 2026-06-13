# Build a deployment package that bundles runtime deps (PyNaCl for Discord
# signature verification) alongside the handler source.
resource "null_resource" "build" {
  triggers = {
    source = filebase64sha256("${path.module}/../fetch_scores.py")
    reqs   = filebase64sha256("${path.module}/../requirements.txt")
  }

  provisioner "local-exec" {
    command = <<-EOT
      set -euo pipefail
      rm -rf "${path.module}/build"
      mkdir -p "${path.module}/build"
      python3 -m pip install -r "${path.module}/../requirements.txt" \
        --platform manylinux2014_x86_64 --implementation cp \
        --python-version 3.12 --only-binary=:all: \
        --target "${path.module}/build"
      cp "${path.module}/../fetch_scores.py" "${path.module}/build/"
    EOT
  }
}

data "archive_file" "lambda_zip" {
  type        = "zip"
  source_dir  = "${path.module}/build"
  output_path = "${path.module}/fetch_scores.zip"
  depends_on  = [null_resource.build]
}

resource "aws_iam_role" "lambda_role" {
  name = "oura-stats-texter-lambda"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Action    = "sts:AssumeRole"
      Principal = { Service = "lambda.amazonaws.com" }
    }]
  })
}

resource "aws_iam_role_policy" "lambda_policy" {
  name = "oura-stats-texter-lambda"
  role = aws_iam_role.lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = ["ssm:GetParameter"]
        Resource = "arn:aws:ssm:us-east-1:*:parameter/oura-stats-texter/*"
      },
      {
        # Allow the function to invoke itself for the async slash-command worker.
        Effect   = "Allow"
        Action   = ["lambda:InvokeFunction"]
        Resource = "arn:aws:lambda:us-east-1:*:function:oura-stats-texter"
      },
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents",
        ]
        Resource = "arn:aws:logs:*:*:*"
      },
    ]
  })
}

resource "aws_lambda_function" "oura_stats_texter" {
  function_name    = "oura-stats-texter"
  role             = aws_iam_role.lambda_role.arn
  handler          = "fetch_scores.lambda_handler"
  runtime          = "python3.12"
  filename         = data.archive_file.lambda_zip.output_path
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256
  timeout          = 30
}

# Public HTTPS endpoint Discord POSTs interactions to. Auth is NONE at the AWS
# layer because Discord can't sign SigV4 requests — the handler verifies every
# request via the Ed25519 signature instead.
resource "aws_lambda_function_url" "discord" {
  function_name      = aws_lambda_function.oura_stats_texter.function_name
  authorization_type = "NONE"
}

resource "aws_lambda_permission" "function_url" {
  statement_id           = "AllowDiscordFunctionUrl"
  action                 = "lambda:InvokeFunctionUrl"
  function_name          = aws_lambda_function.oura_stats_texter.function_name
  principal              = "*"
  function_url_auth_type = "NONE"
}

# Public Function URL invocation also requires lambda:InvokeFunction on the
# resource policy, not just lambda:InvokeFunctionUrl.
resource "aws_lambda_permission" "function_url_invoke" {
  statement_id  = "AllowDiscordFunctionInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.oura_stats_texter.function_name
  principal     = "*"
}

output "discord_interactions_url" {
  description = "Set this as the Interactions Endpoint URL in the Discord app settings."
  value       = aws_lambda_function_url.discord.function_url
}
