docker compose up --build --detach
sleep 10
docker exec psi_peer_downloader rm resources/source.jpg
docker exec psi_peer_downloader rm source.jpg.fileinfo