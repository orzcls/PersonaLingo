# Runtime Protocol (PersonaLingo Skill)

本文档描述 Agent 如何加载与调用本 Skill 包。

## 1. 入口
本 Skill 适配 huashu-nuwa 的两种入口:
- **明确目标**: 用户已完成 MBTI 问卷 + 目标分数 → 直接调用 `/api/distill/run`
- **模糊需求**: 用户仅提供自由文本 → 先调 `/api/distill/diagnose` 获得诊断问卷,再提交问卷之后进入 run

## 2. 数据加载
```python
import json
with open('corpus.json', 'r', encoding='utf-8') as f:
    skill = json.load(f)
profile  = skill.get('learner_profile') or {}
framework = skill.get('capability_framework') or {}
anchors  = skill.get('anchors') or []
```

## 3. 调用菜单 (HTTP)
| 操作 | 端点 | 备注 |
|---|---|---|
| 检索上下文 | `POST /api/conversation/ask?corpus_id=smoke_c_0fe070a1` | 基于本语料库 RAG |
| 查看笔记 | `GET /api/notes?corpus_id=smoke_c_0fe070a1` | 学习笔记 |
| 重新蒸馏 | `POST /api/distill/run?questionnaire_id=<qid>` | 触发 7 步链路 |

## 4. 安全约束
- 回答必须以 `corpus.anchors` / `corpus.bridges` / `corpus.vocabulary` 为首要上下文
- 不得虚构用户未出现的个人经历
- 若 `capability_framework.lift_paths` 给出步骤,教练回复应对齐步骤
