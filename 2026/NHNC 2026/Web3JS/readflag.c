/* readflag: setuid-root helper.
 * Raises privileges and prints /flag.txt so that an unprivileged player who
 * has achieved RCE (but cannot read the root-only flag directly) can obtain
 * the flag by executing this binary. */
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

int main(void) {
    if (setuid(0) != 0 || setgid(0) != 0) {
        /* keep going; we may still have a readable euid */
    }

    FILE *f = fopen("/flag.txt", "r");
    if (!f) {
        perror("fopen(/flag.txt)");
        return 1;
    }

    char buf[512];
    size_t n;
    while ((n = fread(buf, 1, sizeof(buf), f)) > 0) {
        fwrite(buf, 1, n, stdout);
    }
    fclose(f);
    fflush(stdout);
    return 0;
}
