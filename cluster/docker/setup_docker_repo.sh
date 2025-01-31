aws ecr get-login-password --region eu-west-2 | docker login --username AWS --password-stdin ""
aws ecr create-repository --repository-name factorio
