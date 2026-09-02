
- [English](README.MD)
- 中文

# Tp Manager - Renewed

*如果本插件有用, 请给个star吧 :)*

## 修改
- 更改普通玩家最大路径量为10
- 更改总路径量为1024
- 添加了指令 `!!tp warps addhere`
- 修改了指令 `!!tp pos` 为 `!!tp posc`
- 为传送至其他维度添加了指令 `!!tp posd`
- 添加了更多 `!!tp warps` 子节点的指令
- 页面化 `!!tp list`
- 添加 `!!tp search`
- 添加分类管理功能，包括创建、删除、列表、搜索、重命名、修改前缀以及在分类之间移动坐标点
- 添加手动分类标签；一个坐标点可以同时手动标记到多个分类，标签持久化保存于 `categories.json`
- 添加 `!!tp categories rmtag <坐标点>` 用于移除坐标点的所有手动分类标记

## 依赖

| ID | 下载链接 |
|----|----|
| [kpi](https://github.com/kmcsr/kpi_mcdr) | <https://github.com/kmcsr/kpi_mcdr/releases> |

## 指令

> [!TIP]
> 一些插件也注册了 `!!tp` 指令. 故此可使用 `!!tpm` 替换 `!!tp` 节点.

|                指令格式 | 介绍 |
|------------------------|-----|
| `!!tp help`            | 显示帮助信息, `!!tp`同 |
| `!!tp posc <x> <y> <z>` | 传送到当前维度下的指定坐标 |
| `!!tp posd <d> <x> <y> <z>` | 传送到指定维度下的指定坐标 |
| `!!tp ask <name>`      | 请求传送到玩家, `!!tpa`同 |
| `!!tp askhere <name>`  | 请求玩家传送到你, `!!tph`同 |
| `!!tp accept`          | 同意传送请求 |
| `!!tp reject`          | 拒绝传送请求 |
| `!!tp cancel`          | 取消传送请求 |
| `!!tp warp <point>`    | 传送到坐标点, `!!warp`同 |
| `!!tp warps list [页]`      | 列出此页中的坐标点 |
| `!!tp warps search <关键词> [页]` | 列出此页中匹配关键词的坐标点 |
| `!!tp warps add <point> <x> <y> <z> <dimension>` | 添加或设置坐标点 |
| `!!tp warps addhere <point>` | 在当前位置添加或设置坐标点（需要开启服务端和MCDR的rcon功能） |
| `!!tp warps remove <point>` | 删除坐标点 |
| `!!tp warps rename <point> <new_point>` | 重命名一个坐标点 |
| `!!tp warps disown <point>` | 无所有权化一个坐标点 |
| `!!tp warps alias <alias> <original>` | 创建一个坐标点的别名 |
| `!!tp warps rmalias <alias>` | 删除一个坐标点的别名，而不是直接删除该坐标点 |
| `!!tp categories add <名称> <前缀>` | 创建分类 |
| `!!tp categories remove <名称>` | 删除分类, `!!tp categories rm`同 |
| `!!tp categories list <分类> [页]` | 列出分类中的坐标点, `!!tp categories l`同 |
| `!!tp categories listc [页]` | 列出所有分类, `!!tp categories lc`同 |
| `!!tp categories searchc <关键词> [页]` | 搜索分类, `!!tp categories sc`同 |
| `!!tp categories search <分类> <名称> [页]` | 搜索分类中的坐标点, `!!tp categories se`同 |
| `!!tp categories padd <分类> <名称> <x> <y> <z> <维度>` | 在分类中添加 / 设置坐标点 |
| `!!tp categories paddhere <分类> <名称>` | 在当前位置添加分类坐标点 |
| `!!tp categories rename <旧名称> <新名称>` | 重命名分类, `!!tp categories re`同 |
| `!!tp categories redef <分类> <新前缀>` | 修改分类前缀 |
| `!!tp categories premove <分类> <坐标点>` | 删除分类中的坐标点, `!!tp categories prm`同 |
| `!!tp categories pmove <分类> <坐标点> <目标分类>` | 移动坐标点到另一个分类, `!!tp categories pmv`同 |
| `!!tp categories tag <坐标点> <分类>` | 手动将坐标点标记到指定分类（可多个） |
| `!!tp categories rmtag <坐标点>` | 移除坐标点的所有手动分类标记 |

## 配置文件

#### tpm/categories.json

分类配置和手动分类标记保存在此文件中。`tags` 对象记录每个坐标点手动标记的分类列表，因此一个坐标点可以同时属于多个手动标记的分类。

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

手动分类标记在判断分类归属时优先于根据坐标点名称前缀进行的自动分类。删除分类时，该分类对应的手动标记也会一并删除。

#### tpm/config.json

注意, 有些服务器执行 `teleport_xyz_command` 时会把在其他维度的玩家传送到主世界.  
将指令更改为 `execute at {name} run tp {name} {x} {y} {z}` 即可解决该问题

```javascript
{
    "minimum_permission_level": { // 指令权限
        "posc": 2,
        "posd": 2,
        "ask": 1,
        "askhere": 1,
        "accept": 1,
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
    "teleport_cooldown": 60, // 秒, 传送冷却
    "teleport_expiration": 10, // 秒, 传送请求过期时间
    "teleport_commands": [ // 用于传送到玩家的指令集
        "say Teleporting {src} to {dst} ...",
        "tp {src} {dst}",
    ],
    "teleport_xyz_command": "tp {name} {x} {y} {z}" // 用于传送到坐标的指令,
    "enable_wrap": true
}
```
