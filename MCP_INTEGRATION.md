# MCP 集成说明 (MCP_INTEGRATION.md)

本文说明「麦门一人食补给站」如何集成 **M-China 麦当劳 MCP（mcd-mcp）**，将真实 MCP 工具能力用于「一个人生活」人群的就餐决策与陪伴场景。

---

## 实际调用的 MCP 工具

| MCP 工具 | 用途 | 业务价值 |
|---|---|---|
| `now-time-info` | 获取当前时间 | 决定「正餐 / 加餐 / 夜宵」语义，并供节日模块判定 |
| `query-nearby-stores` | 查询附近可自取门店（beType=1） | 极速单默认就近自取，3 分钟搞定 |
| `delivery-query-stores` | 查询可外送门店（拿 beCode） | 犒劳单/坐下来吃时使用外送 |
| `query-meals` | 查询在售餐品（orderType 1=到店 / 2=外送） | 推荐候选池 + 周菜单来源 |
| `list-nutrition-foods` | 餐品营养信息列表（能量/蛋白/脂肪/碳水/钠/钙） | **核心**：按控热量/高蛋白/低钠目标筛均衡候选；官方用途即"搭配指定热量套餐" |
| `query-meal-detail` | 查套餐组成与可替换项 | "减负担定制"：换无糖饮品、去酱、加菜，把一顿饭调轻 |
| `available-coupons` / `query-my-coupons` | 可领券 / 我的券 | 自动套最大可用券，均衡不牺牲到手价 |
| `calculate-price` | 计算实付（storeCode+orderType+beType+items+couponId） | 营养组合同样走算价，确认"均衡"不比随便点更贵 |
| `create-order` | 创建订单 | **仅在用户明确「下单/确认」后**调用，绝不自动下单 |

---

## 调用流程

```
1. now-time-info            → 当前时间，决定正餐/加餐/夜宵 + 节日判定
2. query-nearby-stores      → 门店（外送先 delivery-query-stores 拿 beCode）
3. query-meals              → 在售餐品
   3a. list-nutrition-foods → 拉营养数据，按用户目标筛均衡候选
   3b. query-meal-detail    → 看可替换项，给减负担定制建议
4. available-coupons
   + query-my-coupons       → 可用券
5. calculate-price          → 实付金额（券后）
6. [用户确认后] create-order → 真正下单
```

### 三大创意模块如何复用上述流程
- **① 状态双模式**：步骤 1 后用 `detect_mode(state)` 判定 quick/treat，影响步骤 3 选品权重与步骤 6 文案语气（极速单压快+省+经典，犒劳单压满足感+小确幸）。
- **② 周中不重样周菜单**：步骤 3 拿到在售餐品后调 `generate_weekly_plan(...)`，批量产出 7 天方案（不逐单下单，只给菜单）。
- **③ 一个人的节日不空桌**：步骤 1 拿到时间后 `detect_festival(now)` 命中则走 `festival_plan(...)` 覆盖当餐推荐。

---

---

## 测试与验证

`src/` 下为纯逻辑实现，配套 `tests/` 单元测试（共 19 项，覆盖记忆层读写、双模式判定、周菜单去重、节日判定），使用 mock 餐品数据，本地即可运行校验，无需联网或登录。
