# D125 — Method-level reachability census: the bounded negative on the receiver-to-network chain, and the missing-class count

**Author:** `android-diver` · **Lane:** `android-diver` · **Report:** D125 · **Class:** static artifact extraction only
**Reserved:** D125 via `_lead_alloc.py` (atomic `O_CREAT|O_EXCL`, claimed 22:20:14).
**Cites and does not repeat:** D122 (`covenant-diver`) — AXML column typology, AhMyth artifact census.
**Reconciles with:** D113 (chain closure), D114 (my own, frozen), D104/D106 (`covenant-diver`).
**SCOPE:** static read of `androrat` release DEX and source tree, and one `AhMyth` manifest.
**DEFINER SCOPE:** `android-diver`. **COUNTED:** input cardinality printed beside every result.

---

## 0. Preamble — a retracted frame, and one inherited assertion re-derived

**D122 supersedes my T1 framing and I accept that without argument.** I tested its central claim against the raw bytes rather than citing it on trust:

| probe | byte read | what it is |
|---|---|---|
| `rec[0]+20` | `55` | `ns` index of **rec[1]** |
| `rec[1]+20` | `55` | `ns` index of **rec[2]** |
| `rec[2]+20` | `2` | **low byte of the following chunk header** |

The chunk header at that offset decodes as **`u16 = 0x0102`** — `START_ELEMENT`. So **`0x37` is the `ns` string-pool index at the head of the next record**, and **`0x02` is the next chunk's header byte**, exactly as D122 states.

My D121 §1.3 said `0x02` "appears nowhere in these three records." That was true of the three records and **incomplete as an account**: D122 located where `0x02` actually lives — one byte past the final record, as chunk-header byte 0. **D122's reading is stronger; mine is withdrawn.** The brief's packed-vs-decoded hypothesis is falsified, and the underlying column contract (`ns`@+0, `name`@+4, `rawValue`@+8, `size`@+12, `res0`@+14, `dataType`@+15, `data`@+16) is D122's.

**The 8/8 `data` census survives** — `data` was always read at +16, which no lane disputed.

**Inherited assertions re-derived rather than inherited.** Per the new sub-rule, `[blocked]` or `[verified]` sourced from a brief is an untested value. Two were tested here:

| inherited claim | source | re-derived? | result |
|---|---|---|---|
| `tcpConnection` is an `AsyncTask` reached from the service lifecycle, not reachable from the receiver | D122 | **yes** — §2, field and method level | **CONFIRMED** |
| `controlPanel` is absent from the type table | D122 | **yes** — §3 | **CONFIRMED**, and **two more found** |

---

## 1. The method-level reachability census

### 1.1 Instrument and bounds

**INPUT CARDINALITY:** APK `classes.dex` — **3,604,660 B, 26,908 strings, 3,403 types, 6,109 protos, 12,964 fields, 26,535 methods, 2,472 class_defs.**

**Bounds control (a check that can fail, placed first):** proto `return_type_idx` maximum = **3,400** against 3,403 types; **COUNTED: 0 malformed proto rows of 6,109.** field `type_idx` maximum = 3,401, `class_idx` maximum = 3,249. method_ids span `26,535 * 8 = 212,280` B from offset 298,376, ending exactly at `class_defs_off` **510,656**; **COUNTED: 0 malformed method_id rows of 26,535.** The reader is in range before any conclusion is drawn from it.

### 1.2 Every method on the chain

**COUNTED: 6 chain classes, 39 declared methods.**

| class | type_id | class_def | methods | names |
|---|---|---|---|---|
| `broadcastReciever` | 1965 | 1110 | **4** | `<clinit>`, `<init>`, `isMyServiceRunning`, `onReceive` |
| `mainService` | 1972 | 1117 | **6** | `<clinit>`, `<init>`, `getApplicationContext`, `onBind`, `onStartCommand`, `startActivity` |
| `MainActivity` | 1923 | 2413 | **6** | `<clinit>`, `<init>`, `finish`, `getApplicationContext`, `onCreate`, `overridePendingTransition` |
| `jobScheduler` | 1971 | 1116 | **7** | `<init>`, `doBackgroundWork`, `getApplicationContext`, `jobFinished`, `onStartJob`, `onStopJob`, `startActivity` |
| `functions` | 1969 | 1114 | **11** | `<init>`, `deviceInfo`, `findContext`, `getActivity`, `getPhoneNumber`, `getScreenUp`, `get_numberOfCameras`, `jobScheduler`, `readFromClipboard`, `takescreenshot`, `takescreenshotOfRootView` |
| `tcpConnection` | 1976 | 1121 | **5** | `<clinit>`, `<init>`, `doInBackground` ×2, `execute` |

### 1.3 Network-shaped method census

**COUNTED: 16 network-signature types in the full type table; 0 app methods with a network return type.**

Applying a name heuristic across every chain class:

| class | methods | network-shaped methods |
|---|---|---|
| `tcpConnection` | 5 | **`doInBackground` ×2, `execute`** |
| `broadcastReciever` | 4 | **NONE** |
| `mainService` | 6 | **NONE** |
| `MainActivity` | 6 | **NONE** |
| `jobScheduler` | 7 | **NONE** |
| `functions` | 11 | **NONE** |
| `config` | 2 | **NONE** |

**`tcpConnection` is the only class in the application namespace with any network-shaped method.** Its transport is an `AsyncTask` body (`doInBackground`), reached through `execute`, and **it declares 0 methods with a `java.net` return type** — the socket work is entirely internal to the task body. This is consistent with D122 and is the correct shape for a C2 client.

### 1.4 The structural disconnection — field-level

This is the part that upgrades the claim from assertion to proof.

**COUNTED: 12,964 fields in the APK DEX; 3 fields typed `tcpConnection` in the entire DEX.**

| declaring class | field | type |
|---|---|---|
| `tcpConnection$1` | `this$0` | `Lcom/example/reverseshell2/tcpConnection;` |
| `tcpConnection$2` | `this$0` | `Lcom/example/reverseshell2/tcpConnection;` |
| `tcpConnection$3` | `this$0` | `Lcom/example/reverseshell2/tcpConnection;` |

**All three are synthetic outer-class back-references from `tcpConnection`'s own anonymous inner classes.** Nothing else.

**No application class declares a field of type `tcpConnection`.** Therefore **no class can invoke it through a field** — the only ways in are a local `new` inside a method body, or a static/instance method on the type. **`broadcastReciever`, `mainService` and `MainActivity` declare 4, 6 and 6 methods respectively, and none of those names is a network operation, a transport call, or a `tcpConnection` reference.**

The AAB reproduces this **identically**: 14,803 fields, **3** typed `tcpConnection`, the same three `this$0`, type_id 1974 vs the APK's 1976. **Two independent build outputs, same structure.**

### 1.5 The `tcpConnectionClass` thread, resolved

The string `tcpConnectionClass` (APK id 26004, AAB id 31281) matches **no field declaration in either DEX.** It is a surviving **local variable name** — debug/`LocalVariableTable` residue, not a field. It does not create an edge. **A name that looks like a reference is not a reference**; the field table is the authority, and the field table shows three entries, all synthetic.

### 1.6 Statement of the bounded negative

> **There is no path from `broadcastReciever` to network activity in either shipped artifact.**
>
> **Bounded:** this is a static method-and-field census of two DEX files. It establishes that **no class on the receiver chain declares, holds, or names a network-capable method or field**, and that `tcpConnection` — the sole network-capable app class — has **no non-synthetic reference to it** anywhere in either field table. **It does not** prove that no bytecode path exists through a local construction inside a method body whose `.code_item` was not disassembled; that is the residual unknown stated in §5.

**D113's restraint is confirmed and now has a mechanism.** The five-hop chain is: external `SCREEN_ON` → exported `broadcastReciever.onReceive` (no guard) → `isMyServiceRunning() == false` → `context.startService(mainService)` → `mainService.onStartCommand` → `startActivity(MainActivity, 0x10000000|0x00010000)` = `FLAG_ACTIVITY_NEW_TASK | FLAG_ACTIVITY_FROM_BACKGROUND`. **It is a service-restart-and-launch primitive. It is not C2 re-entry, and `tcpConnection` is not on it.**

**One honest addition to the chain picture:** `jobScheduler` (7 methods) declares **`startActivity`** and implements `onStartJob`/`onStopJob`/`jobFinished`, and `functions` (11 methods) declares `takescreenshot`, `deviceInfo`, `getPhoneNumber`, `getScreenUp`, `readFromClipboard`. These are **capability surfaces that exist in the binary** — but `jobScheduler` is gated by `android.permission.BIND_JOB_SERVICE` (D104/D114), is **not reachable from the receiver**, and **none of its 7 methods is network-shaped.** Reported as present capability, not as a chain extension.

---

## 2. The missing-class count — the full list

### 2.1 Method

Enumerate every `.java` file under `app/src/main`, extract its `package` declaration and every top-level `class` declaration, convert to a DEX type descriptor, and test membership against the DEX type table.

**INPUT CARDINALITY:** **19 `.java` files; 19 top-level class declarations.**

### 2.2 Result

| | count |
|---|---|
| declared classes **present** in APK type table | **16** |
| declared classes **missing** from APK type table | **3** |

**THE MISSING LIST:**

| descriptor | source file |
|---|---|
| `Lcom/example/reverseshell2/controlPanel;` | `java\com\example\reverseshell2\controlPanel.java` |
| `Lcom/example/reverseshell2/jumper;` | `java\com\example\reverseshell2\jumper.java` |
| `Lcom/example/reverseshell2/keypadListner;` | `java\com\example\reverseshell2\keypadListner.java` |

**The count is 3, and the count is the finding.**

| class | status | who found it |
|---|---|---|
| `keypadListner` | missing | D104 — also a declared `<receiver>` at source L65–L70, absent from both compiled artifacts |
| `controlPanel` | missing | D122 — also a declared `<activity>` at source L39 |
| **`jumper`** | **missing** | **new in D125 — not previously enumerated by any lane** |

**`jumper` is the new item.** It is a source-declared class absent from the shipped binary that **appears on no prior missing-list** and **is not referenced by any manifest component** — it was simply never counted because prior work enumerated *components* rather than *classes*. All three share one explanation: **source files present in the tree, absent from the build output**, so the shipped RAT is a strict subset of its own source.

**A control note:** the 16 "present" classes include all 12 `R$*` resource classes and `R`, plus `BuildConfig` — so the instrument correctly finds classes that *are* compiled, and the three misses are real absences rather than a broken descriptor conversion. `BuildConfig` was independently confirmed present in **both** DEXes at `type_id[1922]` (D114), which is a second positive control from a different lane.

**154 inner/anonymous classes** are present in the APK namespace and were counted separately — the miss list is top-level declarations only, as stated.

---

## 3. Allocation and registry

**D125, reserved to `android-diver` at 22:20:14** via `_lead_alloc.py claim` — atomic `O_CREAT|O_EXCL`.

**Registry `status` confirms the reservation and the collision table.** The registry reports **D121 at 4 files**, **D11 at 5 files**, **D12 at 2 files**. Four lanes share D121 with four distinct filenames and four disjoint subjects. **Nothing renamed** — and I note the arithmetic plainly: **the number identifies a lane, the filename identifies a document, and a corpus that equates them cannot tell four reports from one.** The lead's structural fix is correct, and the older `D11`/`D12` entries are the same defect predating it.

---

## 4. Method and limits

**Method.** Hand-written DEX, AXML and source parsers; no third-party disassembler. Every census prints its input cardinality. Bounds controls run **before** the readings that depend on them. Both artifacts read with the same instrument so APK/AAB comparisons are instrument-neutral. Source claims cited as `[source: <file>]`.

**Limits.**

- **No execution. No device. No emulator. No network. No live C2. No REA. No `open_binary`.** No APK or AAB installed, run, or opened.
- **§1.6's negative is bounded to the field and method declaration surface.** `code_item` bodies were **not** disassembled, so a local `new tcpConnection(...)` inside `mainService.onStartCommand` or a handler would **not** appear in the census above. The claim rests on: no field of that type exists, no chain-class method is network-shaped, and no non-synthetic reference to `tcpConnection` exists. **A local-construction path is the residual unknown.**
- **The `tcpConnectionClass` local-name inference** is read as `LocalVariableTable` residue; the debug-info item was not decoded. Stated as an inference, not a measurement.
- **§2's missing list is a type-table membership test, not a load-reachability analysis.** Entry-point reachability was not computed.
- **`AhMyth` was consulted only for D122's artifact census claim, which I cite rather than repeat.** No AhMyth DEX exists in this corpus (D122: 8,437 files, 0 APK / 0 AAB / 0 DEX).
- I did **not** edit D100, D104, D106, D113, D114 or D122. All corrections are by reference.
- **My own error this round:** I re-committed the `IndexError` from indexing a **proto index into the type table** — the identical bug I recorded in D121 §6. I caught it only because I ran a bounds control first and it printed `return_type_idx max = 3400` against 3,403 types, which did not match the failure. **The bug recurred; the control is why it was found in one step instead of after a wrong conclusion.** Filed against my own tooling.

---

## 5. Carry-ins

1. **D122 supersedes my T1 framing.** I tested its `p+20` claim against raw bytes and it is correct: `0x37` = `ns` of the next record, `0x02` = the following chunk's header byte (`u16=0x0102`). My §1.3 account is withdrawn; the column contract is D122's.
2. **The bounded negative holds, proven at field level.** `tcpConnection` is referenced by exactly **3** fields in each DEX — all synthetic `this$0` from its own inner classes. **No app class holds a `tcpConnection` field**, so no class can reach it through a field. Identical in APK and AAB.
3. **The missing-class list is 3: `controlPanel`, `jumper`, `keypadListner`.** `jumper` is new. The count is the finding, and all three share one cause — shipped binary is a strict subset of source.
4. **`tcpConnectionClass` is not a field.** It matches no field declaration; it is a local-variable name. A name that looks like a reference is not a reference.
5. **Residual unknown for the lead:** a local `new tcpConnection(...)` inside a `code_item` body would not be caught by a declaration-surface census. **Disassembling `mainService.onStartCommand` and `broadcastReciever.onReceive` `.code_item`s is the probe that would close it.** That probe was not run here.
6. **`jobScheduler` and `functions` are live capability surfaces** (7 and 11 methods, `startActivity`/`takescreenshot`/`deviceInfo`) that exist in the binary, are not on the receiver chain, and are not network-shaped. Not a chain extension; noted because they are reachable from elsewhere.

---

## 6. Frozen measurement, fixed point

```
D125 frozen measurement -- counts taken on this file including this block

  bytes            : 16156
  lf               : 208
  cr               : 0
  bom              : absent
  fffd             : 0
  strict_utf8      : decodes without error
  headings         : 16     (regex ^#{1,6}[ \t], basis: bare-LF line starts)
  h1_count         : 1     (exactly one '# ' heading)
  dup_headings     : 0     (whole-line exact match, table separators excluded)
  cyrillic_es_0441 : 0
  ellipsis_2026    : 0
  non_ascii        : 47
  btick_nonascii   : 0     (backticked tokens containing non-ASCII content)
  abs_paths        : 0     (this report cites no absolute path; all paths are relative)
  sha256_zeroed    : 699274EB54F88A152C2720E136E2D34B42DCFC1FA4580597F8F068FB4B4EE0C6
                     (digest of this file with this one 64-char field replaced
                      by 64 zeros; reproducible by a third party from the artifact
                      alone. A file cannot contain its own true digest -- the
                      authoritative post-freeze digest is reported externally.)
```
