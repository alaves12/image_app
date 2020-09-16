# image_app
画像処理アプリケーション　　
自分が処理したい画像を入力し、ボタンを押すことで画像を処理することができる。

## help for docker
docker build -t image_app .

docker run -itd -p 127.0.0.1:8000:8000 -v $PWD/dehazepro:/code --name image_app image_app

docker exec image_app python3 manage.py runserver 0.0.0.0:8000

http://localhost:8000/
をクリックして接続
