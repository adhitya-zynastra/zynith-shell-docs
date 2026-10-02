# Postmortem — Zynith UI prototype crashed on live reload (`NiriState` teardown)

| | |
|---|---|
| **Severity** | Medium. Only the Quickshell prototype crashed; the native shell kept every surface and role and was not affected. The side effects were visible on my desktop, though: report windows and orphaned copies |
| **Occurrences** | Six cores on 2026‑10‑02 between 12:47 and 13:25, plus one deliberate reproduction at 13:36 |
| **Fixed in** | `e381281` (`feature/zynith-ui`), with `6cb70d6` for the launcher |
| **Status** | Resolved. The reproduction that failed within 2–6 reloads now survives 30 |

## What happened

While Claude was building the Stage 1 spike ([benchmark](../../03_Performance/benchmarks/zynith-ui-spike-2026-10-02.md)),
it found **six `org.quickshell` crash-report windows** on workspace 7. Several `quickshell` processes were also running
that the `zynith-ui` launcher did not know about. VERIFIED from `coredumpctl`:

| Time | PID | Command line |
|---|---|---|
| 12:47:14 | 146198 | `/usr/bin/quickshell -p …/zynith-ui/ui/shell.qml` |
| 12:47:37 | 146355 | `/usr/bin/quickshell` |
| 13:06:22 | 153927 | `/usr/bin/quickshell -p …/shell.qml` |
| 13:20:23 | 165435 | `/usr/bin/quickshell -p …/shell.qml` |
| 13:24:33 | 168548 | `/usr/bin/quickshell -p …/shell.qml` |
| 13:25:13 | 168941 | `/usr/bin/quickshell` |

The bare `/usr/bin/quickshell` entries are copies started by **Quickshell's own crash handler**. That handler reruns the
crashed instance with a rewritten command line and opens a report window. Because the command line changes, the
launcher's `pgrep` never found these copies. They were left running, and some of them crashed again.

Every core had the same main-thread stack:

```
QCoreApplication::notifyInternal2
QTimerInfoList::activateTimers
timerSourceDispatch
g_main_context_dispatch …  QCoreApplication::exec  qs::launch::launch  main
```

That is a timer firing into an object whose memory had already been freed and zeroed.

The eight `quickshell` cores from 2026‑09‑18 are unrelated. They come from an earlier experiment
(`qs -p …/ZynAku_Shell/shell`), not from this prototype.

## What Claude suspected first, and what did not reproduce it

- **`BlurRegion` never clears `BackgroundEffect.blurRegion`** before its window is destroyed. Clavis clears it.
- **Creating bars at run time** that contain the media and visualizer widgets. Two test bars had just been
  added through `shell.json` when the first crashes occurred.
- **Quickshell internals.**

None of these reproduced the crash, all run against one fresh instance:

- the spectrum toggled 10 times;
- 4 stop/start cycles;
- 10 bar recreations;
- adding and removing the two test bars 3 times.

## What reproduced it

**Live reload.** When a QML file changes, Quickshell builds a new generation of the shell and destroys the old
one. Claude edited the prototype's QML all afternoon while it was running, so every save was a reload. Appending
and removing a comment in `shell.qml` crashed the instance after 2–6 reloads, every time.

Claude bisected with throwaway entry files that each instantiated one part of the shell. Each one was reloaded
10–12 times:

| Entry contents | Result |
|---|---|
| empty `ShellRoot` | survived |
| the IPC handler | survived |
| the panel host | survived |
| the bars | **crashed** |
| `Time`, `Audio`, `Media`, `Network`, `Power`, `Spectrum`, `Scheme`, `Theme` alone | survived |
| `Workspaces` alone | **crashed** |

`Workspaces` is a thin wrapper around the native `NiriState` singleton.

## Cause

`NiriState` declared its niri event-stream socket before its reconnect timer:

```cpp
QLocalSocket m_stream;
QTimer m_retry;
```

C++ destroys members in reverse order, so `m_retry` was destroyed first. When `m_stream` was destroyed next, its
destructor aborted the connection and emitted `disconnected`. The connection to `NiriState::onDisconnected` was
still live, because the `QObject` base had not been destroyed yet. That handler calls `m_retry.start(…)`, which
registered a **destroyed** timer with the event dispatcher. The object's memory was then freed. On a later pass of
the event loop, Qt delivered the timer event into that freed memory.

The singleton is destroyed only on a reload or at exit. At exit the event loop is already gone, so the dangling timer
never fires. Only a reload keeps the process alive long enough to hit it, which is why normal use would not have
shown the bug.

## Fix

- `e381281`: `NiriState` now has a destructor that disconnects the stream from the object and stops the timer
  before the members are torn down.
  - Verification: `Workspaces` alone survived 20 reloads, and the full shell survived 30. VERIFIED.
- `6cb70d6`: the launcher sets `QS_DISABLE_CRASH_HANDLER=1`.
  - A crash now ends the process and leaves a core for `coredumpctl`.
  - Quickshell no longer starts untracked copies or puts report windows on my desktop. Supervision is the
    launcher's job.
- Claude's `BlurRegion` suspicion was not borne out, so `BlurRegion` was left unchanged.

## Effect on measurements

The spike runs at 13:16 and 13:18 were taken while copies relaunched after the 12:47 and 13:06 crashes may still
have been running. The per-process numbers (CPU ticks, PSS, context switches) count only the measured PID. The
copies did add system load, though, and they could have drawn their own surfaces. The gate was therefore re-measured
on a clean desktop with a single instance; see the benchmark page.

## Lessons

- **This is the same class of defect as the [`Signal` use-after-free](2026-09-20-signal-uaf.md):** an object's
  teardown re-entered code that assumed the object was whole. In a `QObject` whose members emit signals from their
  own destructors, the destructor has to cut those connections first.
- **A reload is a teardown test.** The spike script now ends with a reload-survival check, so a regression of this
  kind fails the gate rather than appearing later as report windows.
