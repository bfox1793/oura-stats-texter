data "archive_file" "lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/../fetch_scores.py"
  output_path = "${path.module}/fetch_scores.zip"
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
        Effect   = "Allow"
        Action   = ["ses:SendEmail"]
        Resource = "*"
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
