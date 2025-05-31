import configparser

from pathlib import Path

class Args:
    def __init__(self):
        # 修正路径解析：从Utils目录到DBUtils的正确相对路径
        script_dir = Path(__file__).resolve().parent  # src/Utils 目录
        self.config_path = script_dir.parent / "DBUtils" / "dbconfig.toml"  # src/DBUtils/dbconfig.toml
        self.config = configparser.ConfigParser()
        self.config.optionxform = str  # 保持键的大小写
        self.load_config()  # 初始化时自动加载配置

    def load_config(self):
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config.read_file(f)  # 直接读取原始TOML文件
            print(f"成功加载配置文件：{self.config_path}")  # 调试输出
        except Exception as e:
            print(f"加载配置文件失败：{str(e)}")

    def get_config(self, section, option):
        # 关键修正：TOML的section名称是小写的，统一转换为小写匹配
        target_section = section.lower()
        if self.config.has_section(target_section):
            value = self.config.get(target_section, option, fallback='')
            # 保持原有类型转换逻辑
            try:
                return int(value)
            except ValueError:
                try:
                    return float(value)
                except ValueError:
                    lower_val = value.lower()
                    if lower_val == 'true':
                        return True
                    elif lower_val == 'false':
                        return False
                    return value.strip('"').strip("'")
        print(f"未找到section: {section}（实际存在的section: {self.config.sections()}）")  # 调试提示
        return None

    def save_config(self):
        with open(self.config_path, 'w') as configfile:
            self.config.write(configfile)

    def set_config(self, section, option, value, is_save=True):
        if section not in self.config:
            self.config.add_section(section)
        self.config[section][option] = str(value)
        if is_save:
            self.save_config()

