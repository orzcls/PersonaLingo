class MBTIAnalyzer:
    """MBTI 性格分析服务"""

    # 内置 12 道题目数据
    QUESTIONS = [
        # E/I 维度 (3题)
        {"id": 1, "dimension": "EI", "question": "At a party, you tend to:", "option_a": "Talk to many people, including strangers", "option_b": "Talk to a few close friends"},
        {"id": 2, "dimension": "EI", "question": "You recharge by:", "option_a": "Going out and socializing", "option_b": "Spending time alone"},
        {"id": 3, "dimension": "EI", "question": "In group discussions, you:", "option_a": "Speak up early and often", "option_b": "Listen first, then contribute"},
        # S/N 维度 (3题)
        {"id": 4, "dimension": "SN", "question": "You prefer to focus on:", "option_a": "Present realities and facts", "option_b": "Future possibilities and ideas"},
        {"id": 5, "dimension": "SN", "question": "You are more attracted to:", "option_a": "Practical applications", "option_b": "Innovative theories"},
        {"id": 6, "dimension": "SN", "question": "You trust more:", "option_a": "Direct experience and observation", "option_b": "Gut feelings and intuition"},
        # T/F 维度 (3题)
        {"id": 7, "dimension": "TF", "question": "When making decisions, you prioritize:", "option_a": "Logic and objective analysis", "option_b": "Personal values and harmony"},
        {"id": 8, "dimension": "TF", "question": "You would rather be seen as:", "option_a": "Competent and fair", "option_b": "Warm and empathetic"},
        {"id": 9, "dimension": "TF", "question": "In conflicts, you tend to:", "option_a": "Focus on finding the logical solution", "option_b": "Focus on maintaining relationships"},
        # J/P 维度 (3题)
        {"id": 10, "dimension": "JP", "question": "You prefer your schedule to be:", "option_a": "Planned and organized", "option_b": "Flexible and spontaneous"},
        {"id": 11, "dimension": "JP", "question": "You feel more comfortable when:", "option_a": "Decisions are made and settled", "option_b": "Options are kept open"},
        {"id": 12, "dimension": "JP", "question": "Your workspace is usually:", "option_a": "Neat and systematic", "option_b": "Creative and varied"},
    ]

    # MBTI 16类型简要描述
    TYPE_DESCRIPTIONS = {
        "INTJ": "The Architect - Strategic, independent, and determined",
        "INTP": "The Logician - Analytical, objective, and reserved",
        "ENTJ": "The Commander - Bold, imaginative, and strong-willed",
        "ENTP": "The Debater - Smart, curious, and intellectually daring",
        "INFJ": "The Advocate - Quiet, mystical, and inspiring",
        "INFP": "The Mediator - Poetic, kind, and altruistic",
        "ENFJ": "The Protagonist - Charismatic, inspiring, and natural leader",
        "ENFP": "The Campaigner - Enthusiastic, creative, and sociable",
        "ISTJ": "The Logistician - Practical, fact-minded, and reliable",
        "ISFJ": "The Defender - Dedicated, warm, and protective",
        "ESTJ": "The Executive - Organized, honest, and strong-willed",
        "ESFJ": "The Consul - Caring, sociable, and popular",
        "ISTP": "The Virtuoso - Bold, practical, and masterful with tools",
        "ISFP": "The Adventurer - Flexible, charming, and artistic",
        "ESTP": "The Entrepreneur - Smart, energetic, and perceptive",
        "ESFP": "The Entertainer - Spontaneous, energetic, and enthusiastic",
    }

    # MBTI 沟通风格（用于语料生成时的句型推荐）
    COMMUNICATION_STYLES = {
        "E": "expressive, detailed storytelling, longer responses",
        "I": "concise, reflective, thoughtful pauses",
        "S": "concrete examples, specific details, step-by-step",
        "N": "abstract connections, metaphors, big picture",
        "T": "logical structure, cause-effect, analytical",
        "F": "emotional context, values-driven, personal meaning",
        "J": "organized, clear conclusions, structured",
        "P": "flexible, exploratory, open-ended",
    }

    def get_questions(self):
        """返回所有MBTI测评题目"""
        return self.QUESTIONS

    def analyze(self, answers: dict) -> dict:
        """
        分析MBTI答案
        answers: {question_id: "a" or "b"} 字典
        返回: {"type_code": "INTP", "dimensions": {...}, "description": "...", "communication_style": "..."}
        """
        # 统计各维度
        dimensions = {"E": 0, "I": 0, "S": 0, "N": 0, "T": 0, "F": 0, "J": 0, "P": 0}

        for q in self.QUESTIONS:
            answer = answers.get(str(q["id"]), answers.get(q["id"]))
            if answer is None:
                continue
            dim = q["dimension"]
            if answer == "a":
                dimensions[dim[0]] += 1
            else:
                dimensions[dim[1]] += 1

        # 确定类型
        type_code = ""
        type_code += "E" if dimensions["E"] >= dimensions["I"] else "I"
        type_code += "S" if dimensions["S"] >= dimensions["N"] else "N"
        type_code += "T" if dimensions["T"] >= dimensions["F"] else "F"
        type_code += "J" if dimensions["J"] >= dimensions["P"] else "P"

        # 构建沟通风格
        comm_style = ", ".join([
            self.COMMUNICATION_STYLES[type_code[0]],
            self.COMMUNICATION_STYLES[type_code[1]],
            self.COMMUNICATION_STYLES[type_code[2]],
            self.COMMUNICATION_STYLES[type_code[3]],
        ])

        return {
            "type_code": type_code,
            "dimensions": {
                "EI": {"E": dimensions["E"], "I": dimensions["I"]},
                "SN": {"S": dimensions["S"], "N": dimensions["N"]},
                "TF": {"T": dimensions["T"], "F": dimensions["F"]},
                "JP": {"J": dimensions["J"], "P": dimensions["P"]},
            },
            "description": self.TYPE_DESCRIPTIONS.get(type_code, ""),
            "communication_style": comm_style,
        }

    def get_type_info(self, type_code: str) -> dict:
        """直接根据类型码获取信息（用户已知自己的MBTI时）"""
        comm_style = ", ".join([
            self.COMMUNICATION_STYLES[type_code[0]],
            self.COMMUNICATION_STYLES[type_code[1]],
            self.COMMUNICATION_STYLES[type_code[2]],
            self.COMMUNICATION_STYLES[type_code[3]],
        ])
        return {
            "type_code": type_code,
            "description": self.TYPE_DESCRIPTIONS.get(type_code, ""),
            "communication_style": comm_style,
        }
