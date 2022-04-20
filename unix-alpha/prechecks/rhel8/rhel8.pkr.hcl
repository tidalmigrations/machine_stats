packer {
  required_plugins {
    amazon = {
      version = ">= 0.0.1"
      source  = "github.com/hashicorp/amazon"
    }
  }
}


variable aws_access_key {
  type        = string
  default     = ""
  description = "Add your AWS Access Key ID"
  sensitive   = true
}
variable aws_secret_key {
  type        = string
  default     = ""
  description = "Add your AWS Secret Access key"
  sensitive   = true
}
variable aws_region {
  type        = string
  default     = "ca-central-1"
}
variable packer_python_version {
  type        = string
  default     = env("PACKER_PYTHON_VERSION")
}
variable current_branch_name {
  type        = string
  default     = env("CURRENT_BRANCH_NAME")
}


source "amazon-ebs" "rhel8" {
  ami_name      = "machine-stats-prechecls-rhel8-python-${var.packer_python_version}"
  instance_type = "t2.micro"
  region        = "${var.aws_region}"
  access_key    = "${var.aws_access_key}"
  secret_key    = "${var.aws_secret_key}"

  source_ami_filter {
    filters = {
      name                = "RHEL-8*-x86_64-*"
      root-device-type    = "ebs"
      virtualization-type = "hvm"
    }
    most_recent = true
    owners      = ["309956199498"]
  }
  ssh_username = "ec2-user"
  force_deregister        =  true
  force_delete_snapshot   =  true
  skip_save_build_region  =  true
}


build {
  name    = "rhel8-build"
  sources = [
    "source.amazon-ebs.rhel8"
  ]

  provisioner "shell" {
    script = "./scripts/setup.sh"
    environment_vars = [
      "BRANCH_NAME=${var.current_branch_name}"
    ]
  }

  provisioner "shell" {
    script = "./scripts/rhel8-python-${var.packer_python_version}.sh"
  }
}
