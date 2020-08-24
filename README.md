# image_app
application

## help for docker
docker build -t image_app .

docker run -itd -p 127.0.0.1:8000:8000 -v $PWD/dehazepro:/code --name image_app image_app

docker exec image_app python3 manage.py runserver 0.0.0.0:8000
