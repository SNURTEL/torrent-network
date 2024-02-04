# torrent-network

A torrent-like system for local network implemented in Python with asyncio and BSD sockets. Supports parallel download from multiple peers, seeding incomplete files and automatic availability reporting. A Docker configuration for testing is also included.

### How it works

The system runs in a local network. Two types of nodes are present:
- Coordinator - a single node responsible for monitoring availability of specific files and guiding peers where the files can be found. The coordinator does not query peers for any information - they must submit all reports voluntarily.
- Peer - multiple nodes capable of downloading and seeding files. 

Files can be shared between peers in the network in chunks of constant size. Files are distinguished by their metadata stored in `.fileinfo` files - this includes file hash, size, number of chunks and a control sum for each chunk. To download the file, a peer must first know it's `.fileinfo` representation.

When a file is to be downloaded, peer reserves space on disk (creates an empty `.partial` file) and queries the coordinator for information on different peers which hold a copy of the file (full or partial) using the file hash. If some peers only some chunks and not the entire file, the downloader queries them directly to find out which chunks they own. Then, it is decided from which peer to download which chunk, multiple connections are opened and chunks are downloaded from peers in parallel (rarest-first). For each chunk, a control sum is also checked to ensure file integrity. If chunk download fails for any reason, the chunk is put in a retry queue, from which the chunks are re-downloaded. After the peer finished downloading all chunks and file integrity is looking good, the `.partial` suffix is removed and the peer starts seeding the file.

Availability reporting happens periodically each $N$ seconds. Each peer reports availability of each file it seeds to coordinator - it can either report it has a full copy (2), only some chunks (1 - reported when the peer is downloading the file), or it does not have the file (0 - in case the user deleted it while the system was running). To save bandwidth & coordinator memory, peers do not report _which_ chunks they own - it is up to the downloader to query individual peers and find the chunks. If the coordinator does not receive any information on a particular file from a given peer for some time (multiple of reporting interval), the peer is considered down, and it is removed from coordinator's availability table.

For more details, check out the original project documentation (in polish, since this was a university project): [doc](doc/Sieć%20torrent%20-%20dokumentacja%20końcowa.md).


### Try it out 

```shell
$ docker compose up --build
```

Four containers should be started - one coordinator and three peers, two of which have the file `source.jpg`. The third peer should query the coordinator for file availability and then start downloading it from two different peers. 5ms delay is added to network operations so the entire thing does not happen instantaneously.

Check if the file download was successful:

```shell
$ docker cp psi_peer1:/code/src/peer/resources/out.jpg .
```

Other commands:
```shell
$ docker exec -it psi_peer1 sh
$ python3 peer.py --help

    Download files from "torrent" network.
    
    Usage:
        python3 peer.py get <.fileinfo file> <out file>
        python3 peer.py start-server
        python3 peer.py kill-server
        python3 peer.py help
```