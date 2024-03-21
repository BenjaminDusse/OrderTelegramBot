sudo docker build -t inverbot .
sudo docker run --name inverbot_container --restart unless-stopped -v /home/avaz/inverbot/app:/app inverbot