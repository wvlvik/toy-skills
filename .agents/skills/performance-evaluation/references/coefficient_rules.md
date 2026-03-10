# 绩效系数计算规则

## 系数映射表

| 分数范围 | 绩效系数 | 等级 |
|----------|----------|------|
| > 116 | 1.2 | 优秀 |
| 106 - 115 | 1.1 | 良好 |
| 91 - 105 | 1.0 | 合格 |
| 81 - 90 | 0.9 | 需改进 |
| ≤ 80 | 0.8 | 不合格 |

## 计算公式

```python
def calculate_coefficient(score: float) -> float:
    """根据绩效分数计算绩效系数"""
    if score > 116:
        return 1.2
    elif score >= 106:
        return 1.1
    elif score >= 91:
        return 1.0
    elif score >= 81:
        return 0.9
    else:
        return 0.8
```

## 分数来源

绩效分数来自成员工作表的"上级评分"合计值：

1. 打开成员工作表
2. 定位到上级评分合计单元格（J列底部，或K列特殊情况）
3. 读取数值

## 特殊处理

### 分数为0的情况

如果某成员上级评分为0，保留汇总表中的原有分数，不进行更新：

```python
if name == '吴铝' and score == 0:
    print(f"  {name}: 上级评分为0，保留原有分数")
    continue
```

### 分数缺失的情况

如果未找到上级评分，跳过该成员：

```python
if score is None:
    print(f"  {name}: 未找到上级评分")
    continue
```

## 汇总表更新逻辑

### 已存在记录

如果成员已在汇总表中：

1. 获取当前行号
2. 更新 E 列（绩效分数）
3. 更新 F 列（绩效系数）

```python
ws.cell(row=row, column=5).value = score
ws.cell(row=row, column=6).value = coefficient
```

### 新增记录

如果成员不在汇总表中：

1. 找到下一个空行
2. 填写序号、岗位、姓名、分数、系数
3. 不填写部门列（B列是合并单元格）

```python
seq += 1
ws.cell(row=next_row, column=1).value = seq
ws.cell(row=next_row, column=3).value = '前端开发'
ws.cell(row=next_row, column=4).value = name
ws.cell(row=next_row, column=5).value = score
ws.cell(row=next_row, column=6).value = coefficient
```

## 示例计算

| 姓名 | 上级评分 | 绩效系数 |
|------|----------|----------|
| 张三 | 120 | 1.2 |
| 李四 | 110 | 1.1 |
| 王五 | 100 | 1.0 |
| 赵六 | 85 | 0.9 |
| 孙七 | 75 | 0.8 |

## 注意事项

1. 绩效系数保留1位小数（如 1.0, 1.1, 1.2）
2. 分数范围边界值：106属于1.1，105属于1.0
3. 更新汇总表时使用 `data_only=False` 模式，避免公式丢失