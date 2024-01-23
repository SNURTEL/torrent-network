docker compose up --build --detach
sleep 10
docker stop psi_peer_server
docker stop psi_peer_downloader