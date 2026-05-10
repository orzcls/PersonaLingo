# PersonaLingo Skill - INTJ

## 语料库生成流程 (三段式蒸馏 / 7 步)

### 输入
- MBTI类型 + 兴趣问卷 + 目标分数 (+ 上传材料/对话历史)

### 流程
1. **Research 深度调研** → 聚合问卷+材料+对话→ LearnerProfile
2. **Framework 框架提炼** → 能力×场景×目标三维矩阵 + 痛点 + 提升路径
3. **Persona 用户画像** → MBTI维度分析 + 沟通风格推断
4. **Anchors 锚点故事** → 3-4个个人核心故事
5. **Bridges 题库桥接** → 21题桥接法连接锚点和题库
6. **Vocabulary 词汇升级** → 分数段适配的词汇表
7. **Patterns 句型模板** → MBTI匹配的表达模式

### 输出
- 完整个性化语料库 (corpus.json) + 本 Skill.md

## 当前语料库摘要
- Stage 1 深度调研产物: ✓ 已生成
- Stage 2 能力框架产物: ✓ 已生成
- 锚点数: 1
- 桥接数: 0
- 词汇数: 1
- 句型数: 1
- 目标分数: N/A

## 如何加载本 Skill (给外部 Agent)
1. 读取同目录的 `corpus.json` 获得完整语料 + profile + framework
2. 按 `runtime_protocol.md` 描述的协议Call 法执行 RAG 检索 / 生成回复
3. 若需再生成: 调用 PersonaLingo `/api/distill/run?questionnaire_id=<id>`
