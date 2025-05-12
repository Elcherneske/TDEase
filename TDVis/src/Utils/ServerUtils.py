from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import os
import threading
import time


class ServerControl():
    _active_server = None  # 新增类变量跟踪活动服务器
    _active_monitor = None  # 新增监控线程跟踪

    @staticmethod
    def stop_active_server():
        """关闭当前活动的服务器"""
        if ServerControl._active_server:
            try:
                # 添加线程状态判断，防止重复关闭
                if ServerControl._active_monitor and ServerControl._active_monitor.is_alive():
                    ServerControl._active_monitor.join(timeout=5)
                ServerControl._active_server.shutdown()
                ServerControl._active_server.server_close()
            except Exception as e:
                pass
            finally:
                ServerControl._active_server = None
                ServerControl._active_monitor = None  # 清除监控线程引用

    @staticmethod
    def start_report_server(report_path):
        """启动报告服务器并返回访问URL"""
        try:
            ServerControl.stop_active_server()
            
            os.chdir(report_path)
            # 使用 SimpleHTTPRequestHandler 替代自定义处理器
            ServerControl._active_server = ThreadingHTTPServer(
                ('127.0.0.1', 8000),
                SimpleHTTPRequestHandler  # 直接使用基础处理器
            )
            
            # 启动超时监控
            ServerControl._active_monitor = threading.Thread(
                target=ServerControl.server_monitor,
                args=(ServerControl._active_server,),
                daemon=True
            )
            ServerControl._active_monitor.start()
            
            threading.Thread(
                target=ServerControl._active_server.serve_forever,
                daemon=True
            ).start()
            
            return ServerControl.get_url()
        except Exception as e:
            raise Exception(f"服务器启动失败: {str(e)}")

    @staticmethod
    def get_url():
        """获取报告URL"""
        return "http://localhost:8000/topmsv/index.html"  # 固定使用 localhost
    @staticmethod
    def server_monitor(server):
        """60分钟无操作自动关闭"""
        start_time = time.time()
        while time.time() - start_time < 3600:
            time.sleep(10)
        server.shutdown()

