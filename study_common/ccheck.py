#!/usr/bin/env python3
"""Compile-check every ```c block of a study page's content with gcc (via WSL on Windows).

Usage:  python study_common/ccheck.py C_QA_src [C_Advanced_QA_src ...]

Each snippet is tried as-is, then with common headers prepended, then with its body
wrapped in a function (for statement fragments), under gnu17 and then c2x. A snippet
passes if any attempt compiles with -fsyntax-only. Failures are printed with gcc's
first error lines. A snippet whose only errors (with headers, or inside the function wrapper)
are undeclared names or unknown types is reported as a FRAG(ment) rather than a failure.
"""
import glob, os, re, shutil, subprocess, sys, tempfile

HEADERS = """#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stddef.h>
#include <stdint.h>
#include <stdbool.h>
#include <stdarg.h>
#include <string.h>
#include <limits.h>
#include <errno.h>
#include <assert.h>
#include <signal.h>
#include <setjmp.h>
#include <ctype.h>
#include <math.h>
#include <time.h>
#include <stdatomic.h>
#include <stdalign.h>
#include <pthread.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <sys/mman.h>
#include <sys/wait.h>
#include <semaphore.h>
#include <mqueue.h>
#include <inttypes.h>
#include <float.h>
#include <wchar.h>
#include <sched.h>
#include <poll.h>
#include <dlfcn.h>
#include <threads.h>
#include <stdnoreturn.h>
#include <sys/socket.h>
#include <sys/ipc.h>
#include <sys/shm.h>
#include <sys/epoll.h>
#include <sys/syscall.h>
#include <sys/time.h>
#include <sys/resource.h>
#include <sys/uio.h>
#include <sys/select.h>
"""


def snippets(topic):
    for path in sorted(glob.glob(os.path.join(topic, 'content', 'm*.txt'))):
        qid, buf, infence = None, None, False
        for line in open(path, encoding='utf-8').read().split('\n'):
            if line.startswith('@@ ') and not infence:
                qid = line[3:].split('|')[0].strip()
            elif line.startswith('```'):
                if not infence:
                    infence, buf = True, ([] if line.strip() == '```c' else None)
                else:
                    if buf is not None:
                        yield qid, '\n'.join(buf)
                    infence, buf = False, None
            elif infence and buf is not None:
                buf.append(line)


def main():
    work = tempfile.mkdtemp(prefix='ccheck_', dir='.')
    names = []
    for topic in sys.argv[1:]:
        counts = {}
        for qid, code in snippets(topic):
            counts[qid] = counts.get(qid, 0) + 1
            base = f"{os.path.basename(topic)}__{qid}_{counts[qid]}"
            variants = [code, HEADERS + code, HEADERS + 'void __snippet(void) {\n' + code + '\n}\n']
            for i, v in enumerate(variants):
                with open(os.path.join(work, f'{base}.v{i}.c'), 'w', encoding='utf-8', newline='\n') as f:
                    f.write(v + '\n')
            names.append(base)
    script = r'''cd "$1"; for b in $(cat names.txt); do ok=; for std in gnu17 c2x; do for v in 0 1 2; do
  if gcc -std=$std -fsyntax-only -w -pthread "$b.v$v.c" 2>/dev/null; then ok=1; break 2; fi; done; done
  if [ -z "$ok" ]; then frag=; real=
    for v in 1 2; do r=$(gcc -std=gnu17 -fsyntax-only -w -pthread "$b.v$v.c" 2>&1 | grep error | grep -v -e undeclared -e "unknown type name" -e "implicit declaration" -e "storage size of" -e "incomplete type" -e "not a structure or union" | head -3)
      if [ -z "$r" ]; then frag=1; else real="$r"; fi; done
    if [ -n "$frag" ]; then echo "FRAG $b"; else echo "FAIL $b"; echo "$real"; fi; fi; done'''
    with open(os.path.join(work, 'names.txt'), 'w', newline='\n') as f:
        f.write('\n'.join(names) + '\n')
    with open(os.path.join(work, 'run.sh'), 'w', newline='\n') as f:
        f.write(script + '\n')
    if os.name == 'nt':
        wpath = subprocess.run(['wsl', 'wslpath', '-a', os.path.abspath(work).replace('\\', '/')],
                               capture_output=True, text=True).stdout.strip()
        cmd = ['wsl', 'bash', wpath + '/run.sh', wpath]
    else:
        cmd = ['bash', os.path.join(work, 'run.sh'), work]
    out = subprocess.run(cmd, capture_output=True, text=True).stdout
    shutil.rmtree(work)
    fails, frags = out.count('FAIL '), out.count('FRAG ')
    print(out.rstrip())
    print(f'{len(names) - fails - frags} of {len(names)} snippets compile; '
          f'{frags} are fragments using names from the surrounding text; {fails} have other errors')


if __name__ == '__main__':
    main()
