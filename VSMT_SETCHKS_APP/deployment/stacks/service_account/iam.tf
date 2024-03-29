##################
#  IAM - Service account role
##################

resource "aws_iam_role" "iam_host_role" {
  path               = "/"
  name               = "${var.service_name}-host-role-${var.env}"
  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::${local.aws_account_id}:oidc-provider/${trimprefix(data.aws_eks_cluster.eks.identity[0].oidc[0].issuer, "https://")}"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringLike": {
          "${trimprefix(data.aws_eks_cluster.eks.identity[0].oidc[0].issuer, "https://")}:aud": "sts.amazonaws.com",
          "${trimprefix(data.aws_eks_cluster.eks.identity[0].oidc[0].issuer, "https://")}:sub": "system:serviceaccount:vsmt-setchks-app*:ddc-vsmt-setchks-app"
        }
      }
    }
  ]
}
EOF
}

data "aws_iam_policy_document" "iam_host_role_policy_document" {
  statement {
    actions = [
      "secretsmanager:Describe*",
      "secretsmanager:List*",
      "secretsmanager:Get*"
    ]

    resources = [
      "arn:aws:secretsmanager:${var.aws_region}:${local.aws_account_id}:secret:${var.service_prefix}*"
    ]
  }
  statement {
    actions = [
        "rds:*"
        ]
    resources =  flatten([
      [
        "arn:aws:rds:${var.aws_region}:${local.aws_account_id}:*:${var.service_prefix}*",
        "arn:aws:rds:${var.aws_region}:${local.aws_account_id}:db-proxy-endpoint:*",
        "arn:aws:rds:${var.aws_region}:${local.aws_account_id}:db-proxy:*",
        "arn:aws:rds:${var.aws_region}:${local.aws_account_id}:target-group:*"
      ]
    ])
  }
  statement {
    actions = ["elasticache:*"]
    resources = flatten([
      [
        "arn:aws:elasticache:${var.aws_region}:${local.aws_account_id}:${var.service_prefix}*",
        "arn:aws:elasticache:${var.aws_region}:${local.aws_account_id}:replicationgroup:${var.service_prefix}*",
        "arn:aws:elasticache:${var.aws_region}:${local.aws_account_id}:parametergroup:${var.service_prefix}*",
        "arn:aws:elasticache:${var.aws_region}:${local.aws_account_id}:subnetgroup:${var.service_prefix}*",
        "arn:aws:elasticache:${var.aws_region}:${local.aws_account_id}:snapshot:${var.service_prefix}*"
      ]
    ])
  }
}


resource "aws_iam_role_policy" "iam_host_role_policy" {
  role   = aws_iam_role.iam_host_role.id
  name   = "${var.service_name}-host-policy-${var.env}"
  policy = data.aws_iam_policy_document.iam_host_role_policy_document.json
}

resource "aws_iam_instance_profile" "host_profile" {
  name = "${var.service_name}-instance-profile-${var.env}"
  role = aws_iam_role.iam_host_role.name
  path = "/"
}