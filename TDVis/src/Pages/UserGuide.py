import streamlit as st
from pathlib import Path

class UserGuide():
    """用户指南类，用于显示用户指南内容"""
    def __init__(self):
        # 使用 Path 来处理路径
        pages_dir = Path(__file__).parent
        static_dir = pages_dir.parent.parent / 'static'

        self.md_file = None
        self.doc_path = static_dir / "doc"
        self.image_folder = static_dir / "image"

    def run(self):
        self.display_guide()

    def display_guide(self):
        # 从全局session_state获取语言状态（与MainPage保持一致）
        lang = st.session_state.get("language", "en")  # 新增：使用全局语言状态
        
        # 调整语言判断逻辑匹配全局标识
        if lang == "zh":  
            self.md_file = self.doc_path / "user_guide_zh.md"
        else: 
            self.md_file = self.doc_path / "user_guide_en.md"
        
        if self.md_file.exists():
            with open(self.md_file, "r", encoding="utf-8") as f:
                content = f.readlines()
        else:
            st.error(f"🚨 Error: Could not find {self.md_file}")
            content = []

        for line in content:

            # Markdown-style image (e.g., ![alt text](path/to/image.png))
            if line.strip().startswith("!["):
                start = line.find("(") + 1
                end = line.find(")")
                image_name = line[start:end].split("/")[-1]
                image_path = self.image_folder / image_name

                if image_path.exists():
                    st.image(str(image_path), caption=image_name, width=800)
                else:
                    st.warning(f"⚠️图片缺失: {image_name}")

            # Normal markdown text
            else:
                st.markdown(line)