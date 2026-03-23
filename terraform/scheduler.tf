resource "aws_iam_role" "scheduler_role" {
  name = "oura-stats-texter-scheduler"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Action    = "sts:AssumeRole"
      Principal = { Service = "scheduler.amazonaws.com" }
    }]
  })
}

resource "aws_iam_role_policy" "scheduler_policy" {
  name = "oura-stats-texter-scheduler"
  role = aws_iam_role.scheduler_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = "lambda:InvokeFunction"
      Resource = aws_lambda_function.oura_stats_texter.arn
    }]
  })
}

resource "aws_scheduler_schedule" "daily_8am_et" {
  name       = "oura-stats-texter-daily"
  group_name = "default"

  flexible_time_window {
    mode = "OFF"
  }

  schedule_expression          = "cron(0 8 * * ? *)"
  schedule_expression_timezone = "America/New_York"

  target {
    arn      = aws_lambda_function.oura_stats_texter.arn
    role_arn = aws_iam_role.scheduler_role.arn
  }
}
