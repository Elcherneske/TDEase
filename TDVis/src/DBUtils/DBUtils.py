import json  # Add json module import
import pandas as pd
from .PostgreUtils import PostgreUtils
from .SqliteUtils import SqliteUtils
import hashlib

class DBUtils:
    def __init__(self, args):
        self.args = args
        db_mode = self.args.get_config("Database", "mode")
        if db_mode == "sqlite":
            self.db = SqliteUtils(self.args)
        elif db_mode == "postgresql":
            self.db = PostgreUtils(self.args)
        else:
            raise ValueError(f"不支持的数据库模式: {db_mode}")
        
        # 新增：统一获取当前数据库的占位符（? 或 %s）
        self.placeholder = self.db.param_placeholder()
        
        # 初始化表结构（自动创建缺失表）
        self._initialize_tables()

    @staticmethod
    def encode_password(password: str) -> str:
        """_summary_
        对密码进行的哈希加密方式(后续可以该换其他的加密方式)
        """
        return hashlib.sha256(password.encode()).hexdigest()
        
    def user_login(self, username: str, password: str) -> pd.DataFrame:
        """
        用户登录
        :param username: 用户名
        :param password: 存储的加密密码
        :return: 用户信息
        """
        # 查询用户信息
        encoded_password = self.encode_password(password)
        return self.db.select_data_to_df(
            "users",
            columns=["*"],
            condition=f"username = {self.placeholder} AND password = {self.placeholder}",  # 使用统一占位符属性
            params=(username, encoded_password)
        )

    def user_register(self, username: str, password: str, role: str) -> bool:
        """
        用户注册
        """
        try:
            # 参数化查询防止SQL注入
            user_info = self.db.select_data_to_df(
                "users", 
                columns=["*"], 
                condition="username = %s",  # 占位符方式
                params=(username,)
            )
            
            if not user_info.empty:
                return False

            encoded_password = self.encode_password(password)
            # 使用参数化插入
            return self.db.insert_data(
                "users",
                columns=["username", "password", "role","file_addresses"],
                values=(username, encoded_password, role,'[]' )
            )
        except Exception as e:
            print(f"注册失败: {str(e)}")
            return False
        
    def query_users(self, conditions: str, limit: int, offset: int) -> pd.DataFrame:
        """
        查询用户
        :param conditions: 条件
        :param limit: 限制
        :param offset: 偏移
        :return: 查询结果DataFrame,包含数据库类型信息
        """
        try:
            # 查询用户数据
            user_info = self.db.select_data_to_df("users", columns=["*"], condition=conditions, limit=limit, offset=offset)
            # 添加数据库类型信息
            user_info.index = user_info.index+1
            return user_info
        except Exception as e:
            print(f"查询用户失败: {str(e)}")
            return pd.DataFrame()  

    def delete_users(self, usernames: list) -> bool:
        """删除多个用户"""
        try:
            self.db.begin_transaction()
            # 使用统一占位符属性生成IN子句占位符
            placeholders = ','.join([self.placeholder] * len(usernames))
            query = f"DELETE FROM users WHERE username IN ({placeholders})"
            affected_rows = self.db.execute_non_query(query, tuple(usernames))
            
            if affected_rows != len(usernames):
                self.db.rollback_transaction()
                return False
                
            self.db.commit_transaction()
            return True
        except Exception as e:
            self.db.rollback_transaction()
            print(f"[ERROR] 删除用户失败: {str(e)}")
            return False

    def update_password(self, username: str, old_password: str, new_password: str) -> bool:
        """
        更新用户密码
        :param username: 用户名
        :param old_password: 原密码（未加密）
        :param new_password: 新密码（未加密）
        """
        try:
            # 验证旧密码
            if self.user_login(username, old_password).empty:
                return False
            
            # 加密新密码
            encoded_new_password = self.encode_password(new_password)
            
            # 执行参数化更新
            query = "UPDATE users SET password = %s WHERE username = %s"
            return self.db.execute_non_query(query, (encoded_new_password, username)) > 0
        except Exception as e:
            print(f"密码更新失败: {str(e)}")
            return False

    def update_user(self, old_username: str, new_username: str, old_role: str, new_role: str) -> bool:
        """Update user information with improved transaction handling"""
        try:
            if old_username != new_username or old_role != new_role:
                # Build the update query
                set_clause = []
                params = []
                
                if old_username != new_username:
                    set_clause.append("username = %s")
                    params.append(new_username)
                
                if old_role != new_role:
                    set_clause.append("role = %s")
                    params.append(new_role)
                
                # Add the condition parameter
                params.append(old_username)
                
                # Execute the update
                query = f"UPDATE users SET {', '.join(set_clause)} WHERE username = %s"
                affected_rows = self.db.execute_non_query(query, tuple(params))
                
                return affected_rows > 0
            return True
        except Exception as e:
            print(f"[ERROR] 更新用户失败: {str(e)}")
            return False

    def add_file_address(self, username: str, file_path: str) -> bool:
        #自动将双引号过滤掉,确保能够被识别为windows中的地址
        sanitized_path = file_path.replace('"', '')  # Remove all double quotes
        
        try:
            if isinstance(self.db, PostgreUtils):
                placeholder = "%s"
            elif isinstance(self.db, SqliteUtils):
                placeholder = "?"
            else:
                raise ValueError("Unsupported database type")
            
            array_append_expr = self.json_array_append("file_addresses", "$", placeholder)
            query = (
                f"UPDATE users SET file_addresses = {array_append_expr} "
                f"WHERE username = {placeholder}"
            )
            
            params = (sanitized_path, username) 
            
            self.db.execute_non_query(query, params=params)
            return True
                
        except Exception as e:
            print(f"Failed to add file address: {str(e)}")
            return False

    def get_file_addresses(self, username: str) -> list:
        try:
            result = self.db.select_data_to_df(
                "users",
                columns=["file_addresses"],
                condition="username = %s",  # PostgreSQL 使用 %s 占位符
                params=(username,),
                limit=0,
                offset=0
            )
            return result.iloc[0]['file_addresses'] if not result.empty else []
        except Exception as e:
            print(f"Error retrieving file addresses: {str(e)}")
            return []

    def update_file_addresses(self, username: str, file_addresses: list) -> bool:
        """
        Update file addresses for a user
        :param username: The username to update
        :param file_addresses: List of file addresses
        :return: True if successful, False otherwise
        """
        try:
            # Convert list to JSON string
            file_addresses_json = json.dumps(file_addresses)
            # Build update query
            query = "UPDATE users SET file_addresses = %s WHERE username = %s"
            # Execute query
            self.db.execute_non_query(query, (file_addresses_json, username))
            return True
        except Exception as e:
            print(f"Failed to update file addresses: {str(e)}")
            return False

    def delete_data(self, table_name: str, condition: str) -> None:
        """
        删除数据
        :param table_name: 表名
        :param condition: WHERE条件语句
        """
        try:
            self.db.delete_data(table_name, condition)
        except Exception as e:
            print(f"删除数据失败: {str(e)}")
            raise Exception(f"删除数据失败: {str(e)}")

    def json_array_append(self, column: str, path: str, placeholder: str) -> str:
        if isinstance(self.db, PostgreUtils):
            return f"{column}::jsonb || jsonb_build_array({placeholder})"
        elif isinstance(self.db, SqliteUtils):
            return f"json_insert({column}, '$[#]', {placeholder})"
        else:
            raise ValueError("Unsupported database type")

    def _initialize_tables(self):
        """自动初始化缺失的业务表（如users表）"""
        required_tables = {
            "users": [
                "id INTEGER PRIMARY KEY AUTOINCREMENT",
                "username VARCHAR(100) UNIQUE NOT NULL",
                "password VARCHAR(100) NOT NULL",
                "role VARCHAR(50) NOT NULL",
                "file_addresses TEXT DEFAULT '[]'"
            ]
        }

        for table_name, columns in required_tables.items():
            if not self._table_exists(table_name):
                self.db.create_table(table_name, columns)
                print(f"自动创建表 {table_name} 成功")

                if table_name == "users":
                    admin_username = "admin"
                    admin_password = "123456"
                    admin_role = "admin"

                    # 使用统一占位符属性构造查询条件
                    admin_exists = self.db.select_data_to_df(
                        "users",
                        columns=["username"],
                        condition=f"username = {self.placeholder}",  # 使用统一占位符属性
                        params=(admin_username,)
                    ).empty

                    if admin_exists:
                        encoded_password = self.encode_password(admin_password)
                        self.db.insert_data(
                            "users",
                            columns=["username", "password", "role", "file_addresses"],
                            values=(admin_username, encoded_password, admin_role, '[]')
                        )
                        print(f"插入默认管理员 {admin_username} 成功")

    def _table_exists(self, table_name: str) -> bool:
        """检测指定表是否存在"""
        if isinstance(self.db, PostgreUtils):
            # PostgreSQL检测表存在SQL（查询信息模式）
            check_sql = """
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = %s
                )
            """
            # 修正：使用iloc[row, column]格式避免位置索引警告
            result_df = self.db.execute_query(check_sql, (table_name,))
            return result_df.iloc[0, 0]  # 改为行列联合索引
        elif isinstance(self.db, SqliteUtils):
            # SQLite检测表存在SQL（查询sqlite_master）
            check_sql = """
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name = ?
            """
            # 改为使用通用查询方法
            return not self.db.execute_query(check_sql, (table_name,)).empty
        else:
            raise ValueError("Unsupported database type")