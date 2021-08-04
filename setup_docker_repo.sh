aws ecr get-login-password --region eu-west-2
docker login --username AWS --password-stdin 216370203482.dkr.ecr.us-east-1.amazonaws.com
aws ecr create-repository --repository-name hello-world

#public.ecr.aws/y5j3i3w6/raveler

docker tag hello-world public.ecr.aws/y5j3i3w6/paperclip_client
docker push public.ecr.aws/y5j3i3w6/paperclip_client