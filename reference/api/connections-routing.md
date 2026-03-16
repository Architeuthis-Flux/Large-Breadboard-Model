# API: Connections and Routing

Use this file for wiring, net inspection, and routing checks.

## Node Addressing

You can target nodes by:

- Constant: `D13`, `TOP_RAIL`, `GPIO_1`, `ADC0`
- String name: `"d13"`, `"top_rail"`
- Numeric row: `1` to `60`

For IDs and aliases, see `reference/node-map.md`.

## Core Connection Functions

- `connect(node1, node2, duplicates=-1)`
- `disconnect(node1, node2)` (`node2=-1` clears all from `node1`)
- `fast_connect(...)`, `fast_disconnect(...)`
- `is_connected(node1, node2)`
- `nodes_clear()`

## Net and Path Introspection

- `get_num_nets()`
- `get_net_info(net_idx)`
- `get_net_nodes(net_idx)`
- `get_num_bridges()`
- `get_bridge(bridge_idx)`
- `get_num_paths(include_duplicates=False)`
- `get_path_info(path_idx)`
- `get_all_paths()`
- `get_path_between(node1, node2)`

## Debug Print Helpers

- `print_nets()`
- `print_bridges()`
- `print_paths()`
- `print_crossbars()`
- `print_chip_status()`

## Minimal Patterns

```python
# Connect and verify
connect(1, D4)
print(bool(is_connected(1, D4)))
```

```python
# Temporary ADC probe route
connect(ADC0, 5)
v = adc_get(0)
disconnect(ADC0, -1)
print(v)
```

## Escalate To

- `reference/hardware-guide.md` for non-ideal behavior and resistance limits.
- `reference/state-format.md` for large/batch modifications via state JSON.
