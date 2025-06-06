import sqlite3
import pandas as pd
from typing import List, Tuple, Any

class SqliteUtils:
    def __init__(self, args):
        self.args = args
        self.dbname = args.get_config("database", "dbname")
        self.conn = None  # 新增事务连接属性
        self.cursor = None  # 新增事务游标属性

    # 修改：移除 cursor.closed 和 conn.closed 检查，直接关闭连接
    def _connect(self):
        """建立数据库连接"""
        try:
            conn = sqlite3.connect(self.dbname)
            cursor = conn.cursor()
            return conn, cursor
        except Exception as e:
            raise Exception(f"数据库连接失败: {str(e)}")

    # 修改：execute_non_query 方法的 finally 块
    def execute_non_query(self, query: str, params=None) -> int:
        try:
            conn, cursor = self._connect()
            cursor.execute(query, params or ())
            conn.commit()
            return cursor.rowcount
        except sqlite3.Error as e:
            print(f"Query failed: {str(e)}")
            return 0
        finally:
            if cursor:  # 直接关闭，无需检查 closed
                cursor.close()
            if conn:  # 直接关闭，无需检查 closed
                conn.close()

    # 修改：delete_data 方法的 finally 块
    def delete_data(self, table_name: str, condition: str, params: tuple = None) -> None:
        """
        删除数据（兼容PostgreUtils接口）
        :param table_name: 表名
        :param condition: WHERE条件语句
        :param params: 参数元组(可选)
        """
        try:
            conn, cursor = self._connect()
            if params:
                delete_query = "DELETE FROM {} WHERE {}".format(table_name, condition)
                cursor.execute(delete_query, params)
            else:
                delete_query = f"DELETE FROM {table_name} WHERE {condition}"
                cursor.execute(delete_query)
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise Exception(f"删除数据失败: {str(e)}")
        finally:
            if cursor:  # 直接关闭
                cursor.close()
            if conn:  # 直接关闭
                conn.close()

    # 修改：select_data_to_df 方法（显式管理连接生命周期）
    def select_data_to_df(
        self,
        table_name: str,
        columns: List[str] = ["*"],
        condition: str = None,
        params: tuple = None,
        limit: int = None,
        offset: int = None
    ) -> pd.DataFrame:
        """
        查询数据并转换为DataFrame（兼容PostgreUtils接口）
        """
        conn, cursor = None, None  # 初始化连接变量
        try:
            conn, cursor = self._connect()
            columns_str = ", ".join(columns)
            select_query = f"SELECT {columns_str} FROM {table_name}"
            if condition:
                select_query += f" WHERE {condition}"
            if limit:
                select_query += f" LIMIT {limit}"
            if offset:
                select_query += f" OFFSET {offset}"
            # 显式传递连接并确保查询后关闭
            return pd.read_sql_query(select_query, conn, params=params)
        except Exception as e:
            raise Exception(f"查询数据失败: {str(e)}")
        finally:
            if cursor:  # 直接关闭
                cursor.close()
            if conn:  # 直接关闭
                conn.close()

    # 修改：update_data 方法的 finally 块
    def update_data(self, table_name: str, set_clause: str, condition: str, params: tuple) -> None:
        """
        更新数据（兼容PostgreUtils接口）
        :param table_name: 表名
        :param set_clause: SET子句
        :param condition: WHERE条件语句
        :param params: 参数列表
        """
        try:
            self.begin_transaction()
            update_query = f"UPDATE {table_name} SET {set_clause} WHERE {condition}"
            self.cursor.execute(update_query, params)
            self.commit_transaction()
        except Exception as e:
            self.rollback_transaction()
            raise Exception(f"更新数据失败: {str(e)}")
        finally:
            if self.cursor:  # 直接关闭
                self.cursor.close()
            if self.conn:  # 直接关闭
                self.conn.close()

    # 修改：execute_query 方法的 finally 块
    def execute_query(self, query: str, params: tuple = None) -> pd.DataFrame:
        """
        执行查询并返回DataFrame结果
        :param query: SQL查询语句
        :param params: 参数元组（可选）
        :return: 包含查询结果的DataFrame
        """
        conn, cursor = None, None  # 初始化连接变量
        try:
            conn, cursor = self._connect()
            # 使用pandas读取查询结果，支持参数化查询
            return pd.read_sql_query(query, conn, params=params)
        except Exception as e:
            raise Exception(f"执行查询失败: {str(e)}")
        finally:
            if cursor:  # 直接关闭
                cursor.close()
            if conn:  # 直接关闭
                conn.close()

    # 新增创建表方法（兼容PostgreUtils接口）
    def create_table(self, table_name: str, columns: List[str]) -> None:
        """
        创建数据库表（自动跳过已存在的表）
        :param table_name: 表名
        :param columns: 列定义列表（格式示例：["id INTEGER PRIMARY KEY", "name TEXT NOT NULL"]）
        """
        columns_str = ", ".join(columns)
        create_query = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_str})"
        self.execute_non_query(create_query)  # 复用非查询执行方法
    
    # 新增插入数据方法（兼容PostgreUtils接口）
    def insert_data(self, table_name: str, columns: List[str], values: List[Any]) -> int:
        """
        插入数据（参数化查询防止SQL注入）
        :param table_name: 表名
        :param columns: 列名列表（如 ["name", "age"]）
        :param values: 对应列的值列表（长度需与columns一致）
        :return: 成功插入的行数（通常为1）
        """
        columns_str = ", ".join(columns)
        placeholders = ", ".join([self.param_placeholder()] * len(columns))  # 使用?占位符
        insert_query = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"
        return self.execute_non_query(insert_query, tuple(values))  # 传递参数元组

    # Add parameter placeholder method (PostgreSQL uses %s, SQLite uses ?)
    def param_placeholder(self) -> str:
        return "?"