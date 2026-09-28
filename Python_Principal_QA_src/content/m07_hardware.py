MODULE = dict(id=7, title="Hardware, Binary Data & System Interfaces",
              desc="Python at the boundary with devices: parsing binary log pages, decoding registers, building ioctl structures with ctypes, driving CLI tools safely, verifying data integrity at speed and capturing serial consoles.")

QUESTIONS = [

P("Concept", "Parse an NVMe SMART / Health Information log page (log ID 02h, 512 bytes) in Python. What must you get right?",
short="""Use `struct` with an explicit little-endian format (`<`) at the documented byte offsets: critical warning (byte 0, a bit field), composite temperature (bytes 1-2, Kelvin), available spare, threshold and percentage used (bytes 3-5), then 16-byte (128-bit) counters from byte 32 onward, which need `int.from_bytes(..., "little")` because `struct` has no 128-bit type. Convert units (data units are thousands of 512-byte units) and decode warning bits by name.""",
deep="""Key details:

- **Endianness**: NVMe structures are little-endian. Always use `<` in struct formats; native `@` alignment and byte order can differ by platform.
- **Offsets from the spec** (NVMe base spec, SMART / Health log): byte 0 critical warning; bytes 1-2 composite temperature in Kelvin; 3 available spare (%); 4 spare threshold (%); 5 percentage used; bytes 32-47 data units read; 48-63 data units written; 64-79 host read commands; 80-95 host write commands; 96-111 controller busy time; 112-127 power cycles; 128-143 power-on hours; 144-159 unsafe shutdowns; 160-175 media and data integrity errors; 176-191 error log entries.
- **128-bit counters**: `int.from_bytes(buf[32:48], "little")`; Python ints are unbounded, so no overflow.
- **Units**: one data unit = 1000 x 512 bytes, so bytes = units x 512,000.
- **Critical warning bits**: 0 spare below threshold, 1 temperature threshold, 2 reliability degraded, 3 media read-only, 4 volatile memory backup failed, 5 persistent memory region read-only.
- **Validation**: check the buffer length before parsing, and keep the raw bytes in the result bundle so parsing bugs can be fixed retroactively.

Design point: put this in a typed, tested parser (a dataclass with `from_bytes`) inside the HAL, with golden-file tests from real devices.""",
code=r'''
import struct
from dataclasses import dataclass

WARN_BITS = ["spare_below_threshold", "temperature", "reliability_degraded", "read_only", "volatile_backup_failed", "pmr_read_only"]

def u128(buf, off): return int.from_bytes(buf[off:off + 16], "little")

@dataclass(frozen=True)
class SmartLog:
    critical_warning: list; temperature_c: int; available_spare: int; spare_threshold: int
    percent_used: int; data_written_tb: float; power_on_hours: int; unsafe_shutdowns: int; media_errors: int

    @classmethod
    def from_bytes(cls, buf: bytes) -> "SmartLog":
        if len(buf) != 512: raise ValueError(f"SMART log must be 512 bytes, got {len(buf)}")
        warn, temp_k, spare, thresh, used = struct.unpack_from("<BHBBB", buf, 0)
        return cls([n for i, n in enumerate(WARN_BITS) if warn >> i & 1], temp_k - 273, spare, thresh, used,
                   round(u128(buf, 48) * 512_000 / 1e12, 2), u128(buf, 128), u128(buf, 144), u128(buf, 160))

# build a fake page the way a device would return it
page = bytearray(512)
struct.pack_into("<BHBBB", page, 0, 0b00000101, 318, 7, 10, 91)     # warnings: spare + reliability; 45 C
page[48:64] = (123_456_789).to_bytes(16, "little")                    # data units written
page[128:144] = (41_230).to_bytes(16, "little")                       # power-on hours
page[144:160] = (17).to_bytes(16, "little")                           # unsafe shutdowns
page[160:176] = (2).to_bytes(16, "little")                            # media errors
log = SmartLog.from_bytes(bytes(page))
print(log)
print("health gate:", "FAIL" if log.critical_warning or log.available_spare < log.spare_threshold else "PASS")
''',
follow=(
"Why not read the counters as two 64-bit values with `<QQ`? => You can (low, high = ...; value = low | high << 64), but `int.from_bytes` over 16 bytes is clearer and handles the full 128-bit range directly.",
"How do you test the parser without hardware? => Golden files: capture raw 512-byte pages from real devices (including a failing one), store them in the repo, and assert parsed fields; add hand-built edge cases like maximum counters and all warning bits set.",
),
pitfall="Using native format characters (`struct.unpack('HBB', ...)`) without `<`: native mode inserts alignment padding and uses host byte order, so offsets silently shift.",
signals="You insist on explicit endianness and spec offsets, handle 128-bit counters and units correctly, decode bit fields by name, validate length, and keep raw data for re-parsing.",
),

P("Concept", "How do you decode hardware register values in Python, and when would you use `ctypes` bit-fields instead of shifts and masks?",
short="""Shifts and masks (`(value >> shift) & ((1 << width) - 1)`) driven by a field table are portable, explicit and easy to test; they're my default. `ctypes.Structure` with bit-field declarations is convenient for mirroring a C header, but bit-field layout is compiler/ABI-defined, so verify it against known values. Python ints are arbitrary precision, so mask results explicitly and convert two's-complement fields yourself.""",
deep="""Example: the NVMe Controller Capabilities (CAP) register is 64 bits: MQES bits 15:0 (maximum queue entries, zero-based), CQR bit 16, AMS bits 18:17, TO bits 31:24 (timeout in 500 ms units), DSTRD bits 35:32, NSSRS bit 36, CSS bits 44:37, BPS bit 45, MPSMIN bits 51:48, MPSMAX bits 55:52.

A **field table** approach (`{"MQES": (0, 16), "TO": (24, 8), ...}`) gives one generic decoder, pretty printing and round-trip encoding, and the table can be generated from the spec or a register description file.

**Signed fields**: if the top bit of a `width`-bit field is set, subtract `1 << width`.

**ctypes**: `class CAP(ctypes.LittleEndianStructure): _fields_ = [("MQES", c_uint64, 16), ...]` mirrors C bit-fields. Use `LittleEndianStructure` to fix byte order, `_pack_` to control padding, and `from_buffer_copy(raw)` to parse. Always cross-check against the shift/mask decoder in a unit test.

Also useful: `int.bit_count()` (3.10+) for population counts, `format(v, "#018x")` for fixed-width hex display.""",
code=r'''
import ctypes

CAP_FIELDS = {"MQES": (0, 16), "CQR": (16, 1), "AMS": (17, 2), "TO": (24, 8), "DSTRD": (32, 4),
              "NSSRS": (36, 1), "CSS": (37, 8), "BPS": (45, 1), "MPSMIN": (48, 4), "MPSMAX": (52, 4)}

def decode(value, fields):
    return {name: (value >> shift) & ((1 << width) - 1) for name, (shift, width) in fields.items()}

def encode(values, fields):
    out = 0
    for name, v in values.items():
        shift, width = fields[name]
        if v >> width: raise ValueError(f"{name}={v} does not fit in {width} bits")
        out |= v << shift
    return out

cap = encode({"MQES": 1023, "CQR": 1, "TO": 40, "DSTRD": 0, "CSS": 0b1, "MPSMIN": 0, "MPSMAX": 4}, CAP_FIELDS)
f = decode(cap, CAP_FIELDS)
print(f"CAP = {cap:#018x}")
print(f"max queue entries {f['MQES'] + 1}, ready timeout {f['TO'] * 0.5:.0f} s, page size {4096 << f['MPSMIN']}..{4096 << f['MPSMAX']} bytes")

class CAPBits(ctypes.LittleEndianStructure):
    _fields_ = [("MQES", ctypes.c_uint64, 16), ("CQR", ctypes.c_uint64, 1), ("AMS", ctypes.c_uint64, 2),
                ("rsvd", ctypes.c_uint64, 5), ("TO", ctypes.c_uint64, 8), ("DSTRD", ctypes.c_uint64, 4)]
bits = CAPBits.from_buffer_copy(cap.to_bytes(8, "little"))
print("ctypes agrees:", (bits.MQES, bits.TO) == (f["MQES"], f["TO"]))

def to_signed(v, width): return v - (1 << width) if v >> (width - 1) & 1 else v
print("12-bit 0xFF6 as signed:", to_signed(0xFF6, 12), "| popcount of 0xF0F0:", (0xF0F0).bit_count())
''',
follow=(
"Why is Python's `~x` surprising for register math? => Python ints are infinite two's complement, so `~0x0F` is `-16`, not `0xF0`; mask it: `~x & 0xFF` for 8-bit registers.",
"How would you keep register definitions in sync with firmware? => Generate the field tables (and C headers) from one source of truth, such as a register description file (SystemRDL/IP-XACT or a YAML spec), in the build.",
),
pitfall="Assuming `ctypes` bit-field layout matches the hardware without testing it, or forgetting to mask after `~` and left shifts.",
signals="You use a table-driven decoder with encode/decode round-trip, handle signedness and masking, know ctypes bit-field caveats, and propose a single source of truth for register maps.",
),

P("Concept", "How would you issue an NVMe admin command from Python on Linux without a CLI tool?",
short="""Open the controller character device (`/dev/nvme0`), build a `struct nvme_admin_cmd` (the 72-byte `nvme_passthru_cmd`) with `ctypes`, point its `addr` at a buffer you own (a `ctypes` array), and call `fcntl.ioctl(fd, NVME_IOCTL_ADMIN_CMD, cmd)`, where the request code is `_IOWR('N', 0x41, struct)` = `0xC0484E41`. Check the ioctl return value and the command's result/status, and run with the needed privileges.""",
deep="""Structure (from `linux/nvme_ioctl.h`): `opcode u8, flags u8, rsvd1 u16, nsid u32, cdw2 u32, cdw3 u32, metadata u64, addr u64, metadata_len u32, data_len u32, cdw10..cdw15 u32, timeout_ms u32, result u32`: 72 bytes.

Example: Identify Controller is opcode `0x06` with `cdw10 = 1` (CNS 01h) and a 4096-byte data buffer.

Why do this instead of calling `nvme-cli`? Lower overhead per command (no process spawn), direct access to status and result fields, and precise control of timeouts, which matters in stress tests issuing thousands of commands. Why not? It's Linux-specific, needs root or capabilities, and a mistake can harm the device; many teams keep `nvme-cli` for readability and use ioctl only in performance-critical paths or through a vetted library.

Safety: keep a reference to the buffer while the ioctl runs, validate buffer sizes, restrict destructive opcodes (format, sanitize, firmware commit) behind explicit flags, and log every command for reproducibility.""",
code=r'''
import ctypes, sys

class NvmePassthruCmd(ctypes.Structure):
    _fields_ = [("opcode", ctypes.c_uint8), ("flags", ctypes.c_uint8), ("rsvd1", ctypes.c_uint16),
                ("nsid", ctypes.c_uint32), ("cdw2", ctypes.c_uint32), ("cdw3", ctypes.c_uint32),
                ("metadata", ctypes.c_uint64), ("addr", ctypes.c_uint64),
                ("metadata_len", ctypes.c_uint32), ("data_len", ctypes.c_uint32),
                ("cdw10", ctypes.c_uint32), ("cdw11", ctypes.c_uint32), ("cdw12", ctypes.c_uint32),
                ("cdw13", ctypes.c_uint32), ("cdw14", ctypes.c_uint32), ("cdw15", ctypes.c_uint32),
                ("timeout_ms", ctypes.c_uint32), ("result", ctypes.c_uint32)]

def _IOWR(type_char, nr, size):                      # Linux ioctl request encoding
    return (3 << 30) | (size << 16) | (ord(type_char) << 8) | nr

NVME_IOCTL_ADMIN_CMD = _IOWR("N", 0x41, ctypes.sizeof(NvmePassthruCmd))
print("sizeof(nvme_passthru_cmd) =", ctypes.sizeof(NvmePassthruCmd), "| ioctl =", hex(NVME_IOCTL_ADMIN_CMD))

buf = (ctypes.c_uint8 * 4096)()                      # keep a reference while the ioctl runs
cmd = NvmePassthruCmd(opcode=0x06, cdw10=1, addr=ctypes.addressof(buf), data_len=4096, timeout_ms=5000)

if sys.platform.startswith("linux"):
    import fcntl, os
    try:
        fd = os.open("/dev/nvme0", os.O_RDONLY)
        fcntl.ioctl(fd, NVME_IOCTL_ADMIN_CMD, cmd)
        print("model:", bytes(buf[24:64]).decode().strip())      # Identify Controller MN field
    except OSError as e:
        print("ioctl not possible here:", e.strerror)
else:
    print("not Linux: command built but not sent (opcode 0x06, CNS=1, 4096-byte buffer)")
''',
follow=(
"How do you tell a transport error from an NVMe command error? => A negative ioctl return / `OSError` means the kernel couldn't submit it; a positive return value is the NVMe status field (status code type and code) meaning the controller rejected it; `result` holds DW0 of the completion.",
"How do you prevent a test from accidentally issuing a Format NVM on the wrong drive? => A HAL that requires an explicit destructive-operation flag, verifies the target serial number matches the reservation, and refuses devices marked as system/boot disks.",
),
pitfall="Passing a Python `bytes` object's address or letting the buffer be garbage-collected during the call. Use a `ctypes` array (or `bytearray` via `from_buffer`) and keep a reference.",
signals="You know the passthrough structure and ioctl encoding, compute the request code correctly, handle buffers safely, distinguish error layers, and discuss when ioctl is worth it versus CLI tools.",
),

P("Scenario", "Your framework shells out to `nvme-cli` and `smartctl` thousands of times. How do you make these calls robust?",
short="""Use `subprocess.run` with an argument **list** (never `shell=True`), a timeout on every call, captured stdout/stderr, `check` semantics mapped to your own exception with the command, exit code and stderr, and machine-readable output (`-o json`, `--json`) parsed and validated instead of scraping text. On timeout kill the whole process group, log every command with duration, and retry only commands known to be safe to repeat.""",
deep="""Checklist:

- **No shell**: `["nvme", "smart-log", dev, "-o", "json"]`; device paths or names from inventories can't inject commands.
- **Timeouts**: hung tools are common with misbehaving devices. On timeout, `subprocess.run` kills the child, but grandchildren (tools that spawn helpers) survive; start with `start_new_session=True` (POSIX) and kill the process group, or `CREATE_NEW_PROCESS_GROUP` on Windows.
- **Structured output**: JSON output is stable across versions compared to text; validate required fields and types.
- **Errors**: raise a domain exception (`DeviceCommandError(cmd, rc, stderr)`), never return `None`; classify errors (device vs tool vs environment).
- **Encoding**: `text=True, encoding="utf-8", errors="replace"` so odd bytes in model strings don't crash parsing.
- **Environment**: pin tool versions in lab images; record `nvme version` in results.
- **Performance**: for high-frequency polling, reduce process spawns (batch queries, longer intervals) or switch that path to ioctl.""",
code=r'''
import json, subprocess, sys, time

class DeviceCommandError(RuntimeError):
    def __init__(self, tool, rc, stderr): super().__init__(f"{tool} exited {rc}: {stderr.strip()[:80]}"); self.rc = rc

def run_tool(tool, args, timeout=5.0):
    t = time.perf_counter()
    try:
        r = subprocess.run(args, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=timeout)
    except subprocess.TimeoutExpired:
        raise TimeoutError(f"{tool} timed out after {timeout}s") from None
    if r.returncode != 0:
        raise DeviceCommandError(tool, r.returncode, r.stderr)
    data = json.loads(r.stdout)
    for field in ("critical_warning", "temperature"):
        if field not in data: raise ValueError(f"missing field {field!r} in tool output")
    print(f"  ok in {(time.perf_counter() - t) * 1000:.0f} ms")
    return data

PY = sys.executable
fake_ok   = [PY, "-c", "import json; print(json.dumps({'critical_warning': 0, 'temperature': 318}))", "/dev/nvme0"]
fake_err  = [PY, "-c", "import sys; sys.stderr.write('NVMe status: INVALID_FIELD(0x2)'); sys.exit(22)"]
fake_hang = [PY, "-c", "import time; time.sleep(30)"]
for label, args in (("healthy", fake_ok), ("rejected", fake_err), ("hung", fake_hang)):
    try:
        print(label, "->", run_tool("nvme smart-log", args, timeout=1.0))
    except (DeviceCommandError, TimeoutError, ValueError) as e:
        print(label, "->", type(e).__name__, e)
''',
follow=(
"Why might a timeout still leave processes running? => `subprocess.run` kills only the direct child; tools that fork helpers leave orphans. Start the child in a new session/process group and kill the group on timeout.",
"How do you make these calls testable without hardware? => Put them behind the HAL interface and inject a fake runner that returns recorded JSON outputs and error cases.",
),
pitfall="`subprocess.run(f\"nvme smart-log {dev}\", shell=True)` with text scraping via regex: injection risk, locale- and version-dependent parsing, and no timeout.",
signals="You cover argument lists, timeouts with process-group cleanup, structured output validation, typed errors, encoding, version pinning, and testability via injection.",
),

P("Design", "How do you verify data integrity for terabytes written to a drive during a stress test, efficiently?",
short="""Write **self-describing blocks**: each block embeds its LBA, a write sequence number or generation, and a seed-derived payload plus a checksum, so the verifier can regenerate the expected content without storing it and can tell a corrupted block from a misdirected or stale write. Verify with CRC32 (`zlib`, runs in C and releases the GIL on large buffers) or BLAKE2 for stronger detection, stream in large aligned chunks, and parallelize across regions.""",
deep="""Failure modes to detect:

- **Bit flips / corruption**: checksum mismatch.
- **Misdirected write** (data landed at the wrong LBA): the embedded LBA doesn't match the location read.
- **Lost or stale write** (old data returned): the embedded generation is older than the last one written.
- **Torn write** (partial sector update after power loss): checksum mismatch within a block, or mixed generations inside one transfer.

Design:

- Block header: magic, LBA (u64), generation (u32), seed ID, CRC of payload; payload from `hash(seed, lba, generation)` or a fast PRNG.
- The verifier recomputes expected data, so no expected-data database is needed, only the per-region generation map (small).
- Throughput: large sequential I/O (1 MiB+), `readinto` into preallocated buffers, `memoryview` slices, checksum calls on big buffers. Multiple threads work because `zlib.crc32` and `hashlib` release the GIL for large inputs.
- Report the first bad LBA with the expected vs actual header, and save the raw sector for firmware engineers.""",
code=r'''
import struct, zlib, hashlib

SECTOR, MAGIC = 512, 0x5AFE
HDR = struct.Struct("<HQIH")                     # magic, lba, generation, reserved
def make_block(lba, gen, seed=7):
    payload = hashlib.blake2b(f"{seed}:{lba}:{gen}".encode(), digest_size=64).digest() * 7   # 448 bytes
    body = HDR.pack(MAGIC, lba, gen, 0) + payload
    body = body.ljust(SECTOR - 4, b"\0")
    return body + struct.pack("<I", zlib.crc32(body))

def check(lba, data, expected_gen):
    if struct.unpack_from("<I", data, SECTOR - 4)[0] != zlib.crc32(data[:SECTOR - 4]):
        return "CORRUPT (checksum)"
    magic, found_lba, gen, _ = HDR.unpack_from(data)
    if found_lba != lba: return f"MISDIRECTED (block for LBA {found_lba})"
    if gen < expected_gen: return f"STALE (gen {gen}, expected {expected_gen})"
    return "OK"

disk = {lba: make_block(lba, 1) for lba in range(8)}      # generation 1 everywhere
for lba in range(8): disk[lba] = make_block(lba, 2)       # overwrite with generation 2
disk[2] = make_block(2, 1)                                 # device returned old data
disk[5] = make_block(6, 2)                                 # data landed at the wrong LBA
flip = bytearray(disk[7]); flip[100] ^= 0x10; disk[7] = bytes(flip)
for lba in range(8):
    print(lba, check(lba, disk[lba], expected_gen=2))
''',
follow=(
"Why not just compare against a copy of what you wrote? => At terabyte scale you can't store it; a deterministic generator makes expected data recomputable from (seed, LBA, generation) with a tiny state map.",
"CRC32 or SHA-256? => CRC32 is very fast and catches random corruption well but is not collision-resistant; for adversarial or very large-scale guarantees use BLAKE2/SHA-256, accepting more CPU. Many tools use CRC32C (hardware accelerated) in practice.",
),
pitfall="Using a constant pattern (all 0xA5) for every block. It can't detect misdirected or stale writes because every block looks the same.",
signals="You enumerate failure modes (corruption, misdirected, stale, torn), design self-describing blocks that make them distinguishable, and address throughput and useful failure reporting.",
),

P("Scenario", "Capture a device's serial (UART) console during long tests without losing data or blocking the test. How?",
short="""Read the port in a dedicated background thread (pyserial with a short read timeout, or `asyncio` streams), timestamp each line on arrival, push lines into a bounded ring buffer (`collections.deque(maxlen=N)`) and a log file, and match trigger patterns (panics, asserts, "watchdog reset") that set an event the test can wait on. Keep the reader independent of test logic, stop it cleanly with an event, and attach the last N lines to failures.""",
deep="""Requirements: consoles produce bursts (boot logs, crash dumps) and silence for hours; losing the lines just before a crash is the worst outcome.

Design:

- **Reader thread**: blocking reads with a small timeout so it can notice the stop event; never do heavy processing in it, just decode, timestamp, store and match cheap patterns.
- **Storage**: a ring buffer for "tail on failure", plus an append-only file for full history (rotate by size). The deque with `maxlen` is thread-safe for appends and pops.
- **Triggers**: precompiled regex table (`re.compile("panic|ASSERT|WDT reset")`); on match, record the line and set a `threading.Event` or put into a queue for the orchestrator.
- **Encoding**: consoles emit garbage bytes during resets; decode with `errors="replace"`.
- **Timestamps**: host monotonic time plus wall-clock, so console lines can be correlated with test commands and power events.
- **Robustness**: reconnect if the USB-serial adapter disappears (device reset), and surface "console silent for N minutes" as a warning.""",
code=r'''
import collections, io, re, threading, time

class ConsoleCapture:
    TRIGGERS = re.compile(r"(PANIC|ASSERT|WDT reset)")
    def __init__(self, stream, tail=5):
        self.stream, self.tail = stream, collections.deque(maxlen=tail)
        self.stop, self.fatal, self.hits = threading.Event(), threading.Event(), []
        self.thread = threading.Thread(target=self._run, name="uart-reader", daemon=True)
    def _run(self):
        t0 = time.monotonic()
        while not self.stop.is_set():
            raw = self.stream.readline()                    # pyserial: port.readline() with timeout
            if not raw:
                time.sleep(0.005); continue
            line = f"[{time.monotonic() - t0:7.3f}] {raw.decode('utf-8', 'replace').rstrip()}"
            self.tail.append(line)
            if self.TRIGGERS.search(line):
                self.hits.append(line); self.fatal.set()
    def __enter__(self): self.thread.start(); return self
    def __exit__(self, *exc): self.stop.set(); self.thread.join(timeout=2)

fake_port = io.BytesIO(b"boot: FW 2.1.7\nFTL: rebuild 100%\nio: qd32 ok\nio: qd32 ok\n"
                       b"\xff\xfeASSERT ftl_gc.c:812 free_blocks > 0\nWDT reset\nboot: FW 2.1.7\n")
with ConsoleCapture(fake_port, tail=4) as cap:
    crashed = cap.fatal.wait(timeout=1.0)           # the test waits on the event, not on the port
    time.sleep(0.05)
print("fatal event seen:", crashed)
print("first trigger   :", cap.hits[0])
print("tail for report :"); print("\n".join(cap.tail))
''',
follow=(
"Why not read the serial port inside the test's main thread between commands? => Data arrives while the test is blocked on I/O; the OS buffer can overflow and you lose exactly the lines before a hang or crash.",
"How would you do this with asyncio instead of threads? => `pyserial-asyncio` or `asyncio.open_connection` to a serial-over-network bridge, reading lines in a task that feeds an `asyncio.Queue`, with the same ring buffer and trigger logic.",
),
pitfall="Unbounded in-memory log lists during a 72-hour run, or decoding with strict UTF-8 so one garbage byte during a reset kills the reader thread and silently stops capture.",
signals="You separate capture from processing, bound memory, timestamp for correlation, handle bad bytes and reconnects, and expose triggers and tails to the test and reports.",
),

P("Concept", "How do you parse a multi-gigabyte binary trace file of fixed-size records efficiently?",
short="""Memory-map the file (`mmap`), wrap it in a `memoryview`, and decode records with a precompiled `struct.Struct`: `iter_unpack` for full scans, `unpack_from(mm, offset)` for random access by index (offset = header + index x record size). Filter early and aggregate as you go instead of building a list of all records. For heavy analytics, convert once to a columnar format.""",
deep="""Why `mmap`: the OS pages data in on demand and caches it; you avoid reading the whole file into a Python `bytes` object, and random access to record N is O(1).

Techniques:

- `rec = struct.Struct("<QIIHH...")`; `rec.size` gives the record length; validate `(file_size - header) % rec.size == 0` to detect truncation.
- `rec.iter_unpack(view[start:end])` decodes a region in C; process in chunks to keep memory flat.
- Binary search on a sorted field (timestamps) with `unpack_from` at computed offsets finds a time window without scanning.
- Read the header first (magic, version, record size) and dispatch to the right format version.
- On Windows, close the mmap before deleting or rewriting the file.""",
code=r'''
import mmap, os, struct, tempfile, collections

HEADER = struct.Struct("<4sHHI")                 # magic, version, record_size, count
REC = struct.Struct("<QIBBH")                    # timestamp_us, lba_lo, opcode, status, latency_us

path = os.path.join(tempfile.mkdtemp(), "trace.bin")
N = 500_000
with open(path, "wb") as f:
    f.write(HEADER.pack(b"TRCE", 1, REC.size, N))
    f.write(b"".join(REC.pack(1_000 * i, i * 8, (1, 2, 9)[i % 3], 0 if i % 997 else 4, 50 + i % 400) for i in range(N)))

with open(path, "rb") as f, mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
    magic, ver, rsize, count = HEADER.unpack_from(mm, 0)
    assert magic == b"TRCE" and rsize == REC.size and len(mm) == HEADER.size + count * rsize, "truncated or wrong format"
    view = memoryview(mm)[HEADER.size:]
    errors, slow = collections.Counter(), 0
    for ts, lba, op, status, lat in REC.iter_unpack(view):          # C-level decode, no list of all records
        if status: errors[op] += 1
        slow += lat > 440
    lo, hi = 0, count                                                  # binary search: first record at t >= 250 ms
    while lo < hi:
        mid = (lo + hi) // 2
        if REC.unpack_from(mm, HEADER.size + mid * REC.size)[0] < 250_000_000: lo = mid + 1
        else: hi = mid
    view.release()
print(f"{count:,} records, {os.path.getsize(path) / 1e6:.1f} MB | errors by opcode {dict(errors)} | slow ops {slow}")
print("first record at t>=250 s is index", lo)
''',
follow=(
"How do you handle multiple format versions in the same parser? => Read the header version and select a `Struct` and field mapping per version; keep golden sample files of each version in tests.",
"The analysis team wants to run ad-hoc queries on these traces. What do you do? => Convert once to Parquet/Arrow (or DuckDB) with typed columns; queries then run vectorized and far faster than re-parsing binary each time.",
),
pitfall="`data = open(path, 'rb').read()` followed by slicing each record into new `bytes` objects: double memory and millions of copies.",
signals="You use mmap plus Struct for zero-copy decoding, validate headers and sizes, aggregate while streaming, and use offset arithmetic for random access and binary search.",
),

]
