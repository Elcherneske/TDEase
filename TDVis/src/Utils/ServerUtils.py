from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import os
import threading
import time
import socket


class ServerControl():
    _active_server = None  # 新增类变量跟踪活动服务器
    _active_monitor = None  # 新增监控线程跟踪

    class Handler(SimpleHTTPRequestHandler):  # 新增自定义Handler
        def end_headers(self):
            self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Expires', '0')
            super().end_headers()

        def translate_path(self, path):
            base_dir = os.getcwd()
            path = path.split('?', 1)[0]
            path = os.path.normpath(os.path.join(base_dir, *path.split('/')))
            
            if not os.path.abspath(path).startswith(base_dir):
                self.send_error(403, "Forbidden path traversal attempt")
                return '/dev/null'
            return path

    @staticmethod
    def stop_active_server():
        """关闭当前活动的服务器"""
        if ServerControl._active_server:
            try:
                # 新增端口释放和线程终止处理
                ServerControl._active_server.socket.setsockopt(
                    socket.SOL_SOCKET, socket.SO_REUSEADDR, 1
                )
                if ServerControl._active_monitor and ServerControl._active_monitor.is_alive():
                    ServerControl._active_monitor.join(timeout=0.5)
                ServerControl._active_server.shutdown()
                ServerControl._active_server.server_close()
            except Exception as e:
                print(f"关闭服务时发生异常: {str(e)}")
            finally:
                ServerControl._active_server = None
                ServerControl._active_monitor = None  # 清除监控线程引用

    @staticmethod
    def start_report_server(report_path):
        """启动报告服务器并返回访问URL"""
        try:
            ServerControl.stop_active_server()
            
            os.chdir(report_path)
            # 修改此处绑定地址为0.0.0.0以允许外部访问
            ServerControl._active_server = ThreadingHTTPServer(
                ('0.0.0.0', 8000),  # 修改此行
                ServerControl.Handler  # 使用自定义Handler
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


    @staticmethod  # 添加装饰器
    def get_url():
        """获取报告URL"""
        local_ip=ServerControl.get_local_ip()
        return f"http://{local_ip}:8000/topmsv/index.html"  # 添加f-string格式化

    @staticmethod
    def server_monitor(server):
        """60分钟无操作自动关闭"""
        start_time = time.time()
        while time.time() - start_time < 3600:
            time.sleep(10)
        server.shutdown()
    
    @staticmethod
    def get_local_ip():  # 修复缺少的静态方法装饰器
        """获取本机IP地址"""
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(('8.8.8.8', 80))
            return s.getsockname()[0]
        finally:
            s.close()
