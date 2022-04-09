docker run -d \
  -p 34197:34197/udp \
  -p 27015:27015/tcp \
  --name factorio2 \
  --restart=always \
  216370203482.dkr.ecr.eu-west-2.amazonaws.com/factorio