import json
from hashlib import sha256

CHUNK_SIZE = 1024


def main(filename: str):
    with open(filename, mode='rb') as fp:
        file_bytes = fp.read()

    padded = file_bytes + b'\0' * (CHUNK_SIZE - (len(file_bytes) % CHUNK_SIZE))

    chunks = [padded[i:i + CHUNK_SIZE] for i in range(0, len(padded), CHUNK_SIZE)]
    chunk_hashes = [sha256(chunk).hexdigest()[:32] for chunk in chunks]
    file_hash = sha256(file_bytes).hexdigest()[:32]

    fileinfo = {
        'filename': f'{filename}',
        'file_size': len(file_bytes),
        'file_hash': file_hash,
        'num_chunks': len(chunks),
        'chunk_hashes': chunk_hashes
    }

    with open(f"{filename}.fileinfo", mode='w') as fp:
        json.dump(fileinfo, fp, indent=4)

    print(f"Wrote to {fileinfo}.fileinfo")

if __name__ == '__main__':
    main('source.jpg')