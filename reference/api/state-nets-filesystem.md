# API: State, Nets, and Filesystem

Use this file for snapshot/restore, batch edits, and on-device file operations.

## Full State API

- `get_state()`
- `set_state(json_str, clear_first=True, from_wokwi=False)`

Recommended pattern:

```python
baseline = get_state()
# ... make changes ...
set_state(baseline)
```

## Net and Path Data (State-Adjacent)

- `get_num_nets()`, `get_net_info(i)`, `get_net_nodes(i)`
- `get_num_paths(...)`, `get_path_info(i)`, `get_path_between(a, b)`

For JSON schema and editing rules, use `reference/state-format.md`.

## JFS (Device Filesystem)

File handle APIs:

- `jfs.open(path, mode)`, `jfs.read(file, size=1024)`, `jfs.write(file, data)`
- `jfs.close(file)`, `jfs.seek(file, pos, whence=0)`, `jfs.tell(file)`
- `jfs.size(file)`, `jfs.available(file)`

Filesystem helpers:

- `jfs.exists(path)`, `jfs.listdir(path)`, `jfs.mkdir(path)`, `jfs.rmdir(path)`
- `jfs.remove(path)`, `jfs.rename(from_path, to_path)`, `jfs.stat(path)`
- `jfs.info()`

## Slot and Context Helpers

- `nodes_save(slot=None)`, `nodes_discard()`, `nodes_has_changes()`
- `switch_slot(slot)`
- `context_toggle()`, `context_get()`

## Escalate To

- `reference/state-format.md` for robust JSON editing.
- `reference/repl-runtime-playbook.md` for transport-safe execution patterns.
