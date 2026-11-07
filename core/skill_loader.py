import os
import yaml

class SkillLoader:
    def __init__(self, skill_dir="skills"):
        self.skill_dir = skill_dir

    def load_skill(self, skill_name: str) -> dict:
        # 兼容大模型偶尔返回带有前后空格的情况
        skill_name = skill_name.strip()
        filepath = os.path.join(self.skill_dir, f"{skill_name}.md")
        
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"❌ 找不到技能文件: {filepath}")

        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        # 解析 Markdown 中的 YAML Front-matter
        parts = content.split("---")
        if len(parts) >= 3:
            yaml_meta = yaml.safe_load(parts[1])
            prompt_body = parts[2].strip()
            return {
                "meta": yaml_meta,
                "prompt": prompt_body
            }
        else:
            raise ValueError(f"❌ Skill 文件 {skill_name}.md 格式错误，缺少 YAML 边界")