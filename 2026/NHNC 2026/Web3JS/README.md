# web3js

A tiny EVM lives inside this build of `d8`. You can create one with:

```js
const vm = evm("600160020100");  // hex of creation+runtime code
vm.run();
vm.stack(1);                     // inspect the top of the stack
vm.step();                       // single step, etc. (see https://www.evm.codes/)
```

## Running locally

The remote runs exactly this image. It reads a single line of **base64**
from your connection, decodes it into `run.js`, and runs it with `d8`.

```sh
sudo docker compose up -d --build
# then:
( base64 -w0 your_exploit.js; echo ) | nc localhost 5000
```

The real flag is at `/flag.txt` and is only readable by root. A setuid-root
helper `/readflag` prints it for you — but you have to be able to execute it.

Files:
- `d8`, `snapshot_blob.bin`, `icudtl.dat` — the challenge engine
- `serve.sh` — the per-connection handler used on the remote
- `readflag.c`, `Dockerfile`, `docker-compose.yml` — the deployment
- `flag.txt` — a placeholder flag for local testing
