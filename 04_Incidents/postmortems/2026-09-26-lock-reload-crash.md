# Postmortem — Shell crash on a config reload while locked (and a dangling Control Center pointer)

| | |
|---|---|
| **Severity** | Critical — the lock client died while the session was locked; the screen stayed locked with nothing drawn, and I hard-powered the machine off |
| **Occurred** | 2026‑09‑26 14:09:07 (`noctalia[3726]: segfault at b8 … in noctalia`) |
| **Trigger** | Claude wrote a new `~/.config/noctalia/lockscreen.toml` (the Batch 7 preset) while I had the session locked |
| **Root cause** | an upstream Noctalia 5.1.0 erase-while-iterating bug in `LockscreenWidgetsHost::syncSurfaces` |
| **Related** | two earlier crashes (02:18 and 12:16 the same day) with a different signature — a dangling `ScrollView` pointer in the Control Center's top navigation (Zynith code, fourth batch) is the most likely cause; see below |
| **Fixed in** | Batch 7, uncommitted on `e521a86` (no-git batch) |
| **Status** | Fixed in code; the crash path itself **was not re-run** (it needs a real lock) |

## What I observed

I was testing the lock screen — locking and unlocking a few times between 14:06 and 14:08, and changing the
wallpaper in between. At 14:08:54 I locked again. A few seconds later the screen stopped responding: no clock, no
password field, nothing. It looked like the machine had frozen, and I held the power button down. When I came back
I told Claude that I thought the machine had frozen.

## What the evidence showed

I had Claude work from the previous boot's journal and the core dumps, not from reproduction (reproducing it means
locking the session on purpose).

```
14:08:54.075 niri: locking session
14:09:07.459 [config] config changed, reloading
14:09:07.461 [WRN] [config] lockscreen.toml:117:16: …settings.face: unknown setting
kernel: noctalia[3726]: segfault at b8 ip 0000000000dc2703 … error 4
  #0 LockscreenWidgetsHost::syncSurfaceFrameTick(LockSurface*)
  #1 LockscreenWidgetsHost::syncSurfaces(LockScreen&)
  #2 LockscreenWidgetsController::handleConfigReload()
  #3 ConfigService::fireReloadCallbacks()
  #4 ConfigService::checkReload()
```

- **The trigger was the assistant's write, not anything I did.** 14:09:07 is when Claude, working in the
  background on the Batch 7 lock preset, replaced `lockscreen.toml`. The file watcher reloaded it 13 seconds after I
  had locked. The unknown-setting warnings are the new `face`/`tabular` keys, which the installed binary did not know
  yet. They are harmless; the crash came after them.
- **No GPU, memory or thermal event** in the same boot. niri logged `locking session` and nothing after it. The
  journal ends at 14:09:11, when I powered off.
- **Why it looked frozen.** Under `ext-session-lock-v1` the compositor must keep a session locked when its lock
  client dies without unlocking; that is the protocol's security guarantee. So when the shell crashed, niri kept
  the session locked with no lock surface to draw. That is correct behaviour for a locker crash, and from my side
  it is indistinguishable from a frozen machine.

## Root cause

`LockscreenWidgetsHost::syncSurfaces` (unchanged from pristine Noctalia 5.1.0) handles "a lock widget's
definition changed" like this:

```cpp
detachFromSurface(*existing);
std::erase_if(m_instances, [this, &state](std::unique_ptr<WidgetInstance>& instance) {
  detachFromSurface(*instance);              // runs for EVERY instance, not just the changed one
  return instance->state.id == state.id;
});
```

Two defects in three lines:

1. The predicate detaches **every** instance before testing the id, so one changed widget detaches all the others
   (they vanish until the next sync).
2. `detachFromSurface` calls `syncSurfaceFrameTick`, which walks `m_instances`. `std::erase_if` is
   `remove_if` + `erase`: once it has found the element to remove, it **moves** each later element down, leaving
   moved-from (null) `unique_ptr`s behind. The walk inside the predicate then reads `instance->surface` through a
   null pointer — `segfault at b8` is that member's offset.

It only runs while the lock screen is visible (`m_visible`), so it needs a lock-widget change **while locked**: a
config reload is enough. The new preset changed the clock widgets' settings, which is what took this branch.
`reloadPluginWidgets` and the other removal sites had the same shape (detach inside the predicate), with milder
exposure.

**Why nobody hit it before.** It needs a config change while locked. I rarely edit config while locked; Claude had
never written a lock config while I was locked before this.

## The fix

`LockscreenWidgetsHost::removeInstances(predicate)` collects the instances to remove, detaches them, and only then
erases them with a pure predicate. Every removal site uses it, and the "definition changed" site now removes only
the changed widget. As defence in depth, the frame-tick walk and its callback skip null entries.

**Verification.** Compiled and covered by the full suite. The crashing sequence — a config reload that changes a
lock widget while the session is locked — was **not re-run**. It needs a real lock, which is excluded by standing
rule. The lock editor does not reach this path (`m_visible` is false while editing).

## Crash A — `Select::~Select` during a Control Center teardown (02:18 and 12:16)

The same day had two earlier shell crashes with a different signature:

```
#0 Signal<>::ScopedConnection::disconnect()
#1 Select::~Select()
…  Node/Flex destructors (≈ 20 frames)
#22 PanelManager::destroyPanel()          (12:16:41, closing the Control Center)
#22 PanelManager::~PanelManager()         (02:18, shell exit)
```

`ScopedConnection` holds a `weak_ptr` to the signal's state, so it cannot crash on a destroyed signal. It crashes
when the `Select` object's own memory is already corrupt. The Control Center holds `Select`s (Audio and Network).

**Most likely cause (not proven):** in top-navigation mode — mine since the fourth batch (`top_nav = true`) —
`ControlCenterPanel::create()` built the sidebar `ScrollView`, then destroyed it straight away (`sidebarScroll.reset()`,
because a top row needs no scroll rail), but **left `m_sidebarScrollView` pointing at it**. Keyboard focus in the nav
row (`RovingListNavController::setKeyboardIndex(…, true)`) then calls `scrollSidebarNodeIntoView`, which runs
`scrollNodeIntoScrollView(*m_sidebarScrollView, …)` and **writes a scroll offset into freed memory**. Anything
allocated into that slot later in the same `create()` — tab bodies, including their `Select`s — can be corrupted,
and it only shows when the tree is destroyed. `scrollFocusedInputIntoView` read the same pointer.

The release cores have no debug information, so I cannot show the write landing in a `Select`. The dangling pointer
is certain and the mechanism fits both crashes. That is as far as the evidence goes.

**Fix (Batch 7):** the pointer is cleared when the scroll view is dropped, and the split-pane focus handling uses the
navigation strip itself as the "sidebar" pane in top-navigation mode. The one remaining check is time: no
`Select::~Select` crash after the fix.

## What went wrong in how the work was done

- **The assistant wrote a watched configuration file without checking whether I was locked.** It was working in the
  background while I was testing the lock screen. The shell has a `locked` field in `noctalia msg status`. From now
  on, a config write that the running shell watches is preceded by that check, and lock-affecting writes wait until
  the fixed binary is installed. This is recorded in Claude's working memory as a standing rule.
- **The same power-off interrupted a clean build** that Claude had just started. It left 0-byte generated Wayland
  protocol headers in `build/`, which the next incremental compile tripped over (`zwp_idle_inhibitor_v1_destroy was
  not declared`). The clean build regenerates them. The source tree, this documentation repository and my
  configuration files were checked for truncation and NUL bytes: none.

## Status and follow-up

| Item | State |
|---|---|
| Lock host erase-while-iterating | fixed in code; not exercised at runtime (needs a real lock) |
| Dangling `m_sidebarScrollView` | fixed; causation for the `Select` crashes inferred, not proven |
| Config writes while locked | procedural rule; the shell itself should also stop acting on lock-widget reloads while locked, or defer them to unlock — **future work** |
