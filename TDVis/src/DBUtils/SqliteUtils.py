import sqlite3
import pandas as pd
from typing import List, Tuple, Any

class SqliteUtils:
    def __init__(self, args):
        self.args = args
        self.dbname = args.get_config("database", "dbname")
        self.conn = None  # 新增事务连接属性
        self.cursor = None  # 新增事务游标属性

    def _connect(self):
        """建立数据库连接"""
        try:
            conn = sqlite3.connect(self.dbname)
            cursor = conn.cursor()
            return conn, cursor
        except Exception as e:
            raise Exception(f"数据库连接失败: {str(e)}")

    # 新增事务管理方法
    def begin_transaction(self):
        self.conn, self.cursor = self._connect()
        
    def commit_transaction(self):
        self.conn.commit()
        self.cursor.close()
        self.conn.close()
        
    def rollback_transaction(self):
        self.conn.rollback()
        self.cursor.close()
        self.conn.close()

    # 新增非查询执行方法（兼容PostgreUtils接口）
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
            cursor.close()
            conn.close()

    # 新增参数占位符方法（PostgreSQL用%s，SQLite用?）
    def param_placeholder(self) -> str:
        return "?"

    # 修改delete_data方法，支持参数化查询
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
            if cursor and not cursor.closed:
                cursor.close()
            if conn and not conn.closed:
                conn.close()

    # 修改select_data_to_df方法，支持参数传递
    def select_data_to_df(
        self,
        table_name: str,
        columns: List[str] = ["*"],
        condition: str = None,
        params: tuple = None,  # 新增参数
        limit: int = None,
        offset: int = None
    ) -> pd.DataFrame:
        """
        查询数据并转换为DataFrame（兼容PostgreUtils接口）
        """
        try:
            columns_str = ", ".join(columns)
            select_query = f"SELECT {columns_str} FROM {table_name}"
            if condition:
                select_query += f" WHERE {condition}"
            if limit:
                select_query += f" LIMIT {limit}"
            if offset:
                select_query += f" OFFSET {offset}"
            # 使用pandas的params参数支持参数化查询
            return pd.read_sql_query(select_query, self._connect()[0], params=params)
        except Exception as e:
            raise Exception(f"查询数据失败: {str(e)}")

    # 新增update_data方法（兼容PostgreUtils接口）
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
            if self.cursor and not self.cursor.closed:
                self.cursor.close()
            if self.conn and not self.conn.closed:
                self.conn.close()

    # 其他原有方法（如create_table、insert_data等）保持不变...