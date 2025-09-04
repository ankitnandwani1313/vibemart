provider "aws" {
  region  = "eu-west-1"
  profile = "default"
}

resource "aws_instance" "new_server" {
  ami               = "ami-09b024e886d7bbe74"
  key_name          = "ankit-key-pair"
  instance_type     = "t2.large"
  user_data         = file("${path.module}/../docker/install_docker.sh")

  # Name of the security group
  security_groups   = ["default"]

  tags = {
    Name = "vibemart-airflow"
  }
}
