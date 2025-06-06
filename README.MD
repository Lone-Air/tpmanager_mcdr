
- English
- [中文](README_zh.MD)

# Tp Manager

*If it's useful, please give a star :)*

## Modification
- Change the maxium of points of normal players to 10 
- Change the maxium of points limit to 1024
- add command `!!tp warps addhere`
- modified the command `!!tp pos` to `!!tp posc`
- add command `!!tp posd` for teleporting to a point in another dimension

## Dependencies

| ID | Release Link |
|----|----|
| [kpi](https://github.com/kmcsr/kpi_mcdr) | <https://github.com/kmcsr/kpi_mcdr/releases> |

## Commands

> [!TIP]
> Some other plugins also registered `!!tp` as root command. To avoid conflict, you also can use `!!tpm` to replace `!!tp`

|         Command format | Introduction |
|------------------------|-----|
| `!!tp help`            | Show help message, aka `!!tp` |
| `!!tp posc <x> <y> <z>` | Teleport to target position in current dimension |
| `!!tp posd <d> <x> <y> <z>` | Teleport to target position in target dimension |
| `!!tp ask <name>`      | Send an teleport request, aka `!!tpa` |
| `!!tp askhere <name>`  | Send an teleport request to here, aka `!!tph` |
| `!!tp accept`          | Accept the teleport request |
| `!!tp reject`          | Reject the teleport request |
| `!!tp cancel`          | Cancel your teleport request |
| `!!tp warp <point>`    | Teleport to the warp point, aka `!!warp` |
| `!!tp warps list`      | List all warp points |
| `!!tp warps add <point> <x> <y> <z> <dimension>` | Add or set a warp point |
| `!!tp warps addhere <point>` | Add or set a warp point at your current position (required to enable the rcon feather of the server and mcdreforged) |
| `!!tp warps remove <point>` | Remove a warp point |

## Config files

#### tpm/config.json

```javascript
{
    "minimum_permission_level": { // Command permissions
        "posc": 2,
        "posd": 2,
        "ask": 1,
        "askhere": 1,
        "accept": 1,
        "reject": 0,
        "cancel": 0
    },
    "teleport_cooldown": 60, // in sec, the minimum teleport operation interval
    "teleport_expiration": 10, // in sec, the teleport request expiration
    "teleport_commands": [ // Command list for teleport players
        "say Teleporting {src} to {dst} ...",
        "tp {src} {dst}",
    ],
    "teleport_xyz_command": "tp {name} {x} {y} {z}" // Command for teleport position
}
```
