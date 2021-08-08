export IMAGE_URL=factoriotools/factorio:latest
docker pull $IMAGE_URL
docker create --name temp_container $IMAGE_URL
#docker exec -it temp_container mkdir factorio/config
docker cp ./config temp_container:/factorio/config
docker cp ./config/server-settings.json temp_container:/opt/factorio/data/server-settings.example.json

docker commit temp_container 216370203482.dkr.ecr.eu-west-2.amazonaws.com/factorio
#docker tag temp_container 216370203482.dkr.ecr.eu-west-2.amazonaws.com/factorio
docker push 216370203482.dkr.ecr.eu-west-2.amazonaws.com/factorio
docker rm temp_container
docker run 216370203482.dkr.ecr.eu-west-2.amazonaws.com/factorio