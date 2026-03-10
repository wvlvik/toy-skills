# Excel 单元格结构定义

## 成员工作表

每个团队成员有独立的工作表，表名即成员姓名。

### 标题与周期

| 单元格 | 内容 | 示例 |
|--------|------|------|
| A1 | 标题 | "2月绩效考核表" |
| J2 | 考核周期 | "2026.2.1-2026.2.28" |

### 评分区域

生产质量和测试质量评分位于第9-10行：

| 行 | 内容 | 自评列(J) | 上级评分列(J) | URL列(K) |
|----|------|-----------|---------------|----------|
| 9 | 生产质量 | 自评分 | 上级评分 | TAPD URL |
| 10 | 测试质量 | 自评分 | 上级评分 | TAPD URL |

### 上级评分总计位置

上级评分总计位于工作表底部，位置因成员而异：

**标准情况**（大多数成员）：
- 上级评分合计在 J 列（第10列）
- 从底部向上查找第一个 > 50 的数值

**特殊情况**：
- **陈方杰**：上级评分在 K 列（第11列）
- **刘奕君**：上级评分在 K 列（第11列）

```python
special_col_members = {'陈方杰', '刘奕君'}
score_col = 11 if name in special_col_members else 10
```

## 汇总工作表

汇总表名为"汇总"，包含所有成员的绩效汇总。

### 列定义

| 列 | 字段 | 说明 |
|----|------|------|
| A | 序号 | 1, 2, 3... |
| B | 部门 | 合并单元格，如"前端开发部" |
| C | 岗位 | 如"前端开发" |
| D | 姓名 | 成员姓名 |
| E | 绩效分数 | 上级评分合计 |
| F | 绩效系数 | 根据分数计算 |

### 行位置

- 数据从第3行开始
- 第1-2行为标题行
- 成员数据行：3-18行

### 合并单元格

- B列（部门）是合并单元格，新增记录时不需要填写
- 仅填写非合并单元格：A, C, D, E, F

## 常见成员列表

```python
MEMBER_SHEETS = [
    '吴铝', '文武', '陈方杰', '李金涛', '刘子昱',
    '戴婕妤', '熊思', '曹振辉', '方乐', '汤显文',
    '刘奕君', '周树梧', '唐尧', '陈铁梁'
]
```

## 单元格查找策略

### 查找上级评分合计

```python
def find_superior_score(ws, name):
    """从工作表底部向上查找上级评分"""
    special_col_members = {'陈方杰', '刘奕君'}
    score_col = 11 if name in special_col_members else 10

    for row_idx in range(ws.max_row, 0, -1):
        cell_value = ws.cell(row=row_idx, column=score_col).value
        if cell_value is not None:
            try:
                score = float(cell_value)
                if score > 50:  # 上级评分通常 > 50
                    return score
            except (ValueError, TypeError):
                continue
    return None
```

### 查找汇总表中的成员行

```python
def find_member_row(ws, name):
    """在汇总表中查找成员所在行"""
    for row_idx in range(3, 20):
        cell_name = ws.cell(row=row_idx, column=4).value
        if cell_name == name:
            return row_idx
    return None
```