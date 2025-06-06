
- [English](README.MD)
- 中文

# Tp Manager

*如果本插件有用, 请给个star吧 :)*

## 修改
- 更改普通玩家最大路径量为10
- 更改总路径量为1024
- 添加了指令 `!!tp warps addhere`
- 修改了指令 `!!tp pos` 为 `!!tp posc`
- 为传送至其他维度添加了指令 `!!tp posd`

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
| `!!tp warps list`      | 列出所有坐标点 |
| `!!tp warps add <point> <x> <y> <z> <dimension>` | 添加或设置坐标点 |
| `!!tp warps addhere <point>` | 在当前位置添加或设置坐标点（需要开启服务端和MCDR的rcon功能） |
| `!!tp warps remove <point>` | 删除坐标点 |

## 配置文件

#### tpm/config.json

注意, 有些服务器执行 `teleport_xyz_command` 时会把在其他维度的玩家传送到主世界.  
将指令更改为 `execute at {name} run tp {name} {x} {y} {z}` 即可解决该问题

```javascript
{
    "minimum_permission_level": { // 指令权限
        "pos": 2,
        "ask": 1,
        "askhere": 1,
        "accept": 1,
        "reject": 0,
        "cancel": 0
    },
    "teleport_cooldown": 60, // 秒, 传送冷却
    "teleport_expiration": 10, // 秒, 传送请求过期时间
    "teleport_commands": [ // 用于传送到玩家的指令集
        "say Teleporting {src} to {dst} ...",
        "tp {src} {dst}",
    ],
    "teleport_xyz_command": "tp {name} {x} {y} {z}" // 用于传送到坐标的指令
}
```
