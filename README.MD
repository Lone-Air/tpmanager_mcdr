
- English
- [中文](README_zh.MD)

# Tp Manager - Renewed

*If it's useful, please give a star :)*

## Modification
- Change the maxium of points of normal players to 10 
- Change the maxium of points limit to 1024
- add command `!!tp warps addhere`
- modified the command `!!tp pos` to `!!tp posc`
- add command `!!tp posd` for teleporting to a point in another dimension
- add more commands to `!!tp warps` sub-node
- paginated `!!tp list`
- add `!!tp search`
- add commands for categories
- add category management, including creation, removal, listing, searching, renaming, prefix redefinition, and moving warp points between categories
- add manual category tags; a warp point can be manually tagged to multiple categories, with tags persisted in `categories.json`
- add `!!tp categories rmtag <warp_point>` to remove all manual category tags from a warp point
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
| `!!tp warps list [page]`      | List warp points within the page |
| `!!tp warps search <keyword> [page]` | List warp points that matches the keyword within the page |
| `!!tp warps add <point> <x> <y> <z> <dimension>` | Add or set a warp point |
| `!!tp warps addhere <point>` | Add or set a warp point at your current position (required to enable the rcon feather of the server and mcdreforged) |
| `!!tp warps remove <point>` | Remove a warp point |
| `!!tp warps rename <point> <new_point>` | Rename a warp point |
| `!!tp warps disown <point>` | Disown a warp point |
| `!!tp warps alias <alias> <original>` | Create an alias of a warp point |
| `!!tp warps rmalias <alias>` | Remove an alias of a warp point not directly remove the warp point |
| `!!tp categories add <name> <prefix>` | Create a category |
| `!!tp categories remove <name>` | Remove a category, aka `!!tp categories rm` |
| `!!tp categories list <category> [page]` | List warp points in a category, aka `!!tp categories l` |
| `!!tp categories listc [page]` | List all categories, aka `!!tp categories lc` |
| `!!tp categories searchc <keyword> [page]` | Search categories, aka `!!tp categories sc` |
| `!!tp categories search <category> <name> [page]` | Search warp points in a category, aka `!!tp categories se` |
| `!!tp categories padd <category> <name> <x> <y> <z> <dimension>` | Add / set a warp point in a category |
| `!!tp categories paddhere <category> <name>` | Add a warp point here in a category |
| `!!tp categories rename <old> <new>` | Rename a category, aka `!!tp categories re` |
| `!!tp categories redef <category> <new_prefix>` | Change a category prefix |
| `!!tp categories premove <category> <point>` | Remove a warp point from a category, aka `!!tp categories prm` |
| `!!tp categories pmove <category> <point> <target_category>` | Move a warp point to another category, aka `!!tp categories pmv` |
| `!!tp categories tag <warp_point> <category>` | Manually tag a warp point into a category (multiple allowed) |
| `!!tp categories rmtag <warp_point>` | Remove all manual category tags from a warp point |

## Config files

#### tpm/categories.json

Category configuration and manual category tags are stored in this file. The `tags` object maps each warp point to a list of manually assigned categories, so one warp point can belong to multiple manually tagged categories.

```json
{
    "categories": [
        {
            "name": "main",
            "prefix": "main"
        }
    ],
    "tags": {
        "spawn": ["main", "public"],
        "home": ["survival"]
    }
}
```

Manual tags take precedence over automatic prefix-based category detection. Removing a category also removes its manual tags.

#### tpm/config.json

```javascript
{
    "minimum_permission_level": { // Command permissions
        "posc": 2,
        "posd": 2,
        "ask": 1,
        "askhere": 1,
        "accept": 1,
        "confirm": 1,
        "reject": 0,
        "cancel": 0,
        "warp": 1,
        "warp_set": 2,
        "warp_addhere": 2,
        "warp_remove": 1,
        "warp_config": 3,
        "warp_list": 1,
        "warp_search": 1,
        "warp_rename": 1,
        "warp_disown": 1,
        "warp_alias": 1,
        "warp_rmalias": 1,
        "category_add": 1,
        "category_remove": 1,
        "category_list": 1,
        "category_listc": 1,
        "category_search": 1,
        "category_searchc": 1,
        "category_padd": 2,
        "category_paddhere": 2,
        "category_rename": 1,
        "category_redef": 1,
        "category_premove": 1,
        "category_pmove": 1,
        "category_tag": 1,
        "category_rmtag": 1,
        "category_config": 3
    },
    "teleport_cooldown": 60, // in sec, the minimum teleport operation interval
    "teleport_expiration": 10, // in sec, the teleport request expiration
    "teleport_commands": [ // Command list for teleport players
        "say Teleporting {src} to {dst} ...",
        "tp {src} {dst}",
    ],
    "teleport_xyz_command": "tp {name} {x} {y} {z}" // Command for teleport position,
    "enable_wrap": true
}
```
