# /bin/bash
aws ecr get-login-password --region eu-west-2 | docker login --username AWS --password-stdin 216370203482.dkr.ecr.eu-west-2.amazonaws.com
docker build . -t paperclip-client
docker tag paperclip-client 216370203482.dkr.ecr.eu-west-2.amazonaws.com/paperclip-client
docker push 216370203482.dkr.ecr.eu-west-2.amazonaws.com/paperclip-client
docker run paperclip-client