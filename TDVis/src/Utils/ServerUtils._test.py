from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import os
import threading
import time
import socket

class ServerControlTest:
    _active_server = None
    _active_monitor = None
    _TEST_REPORT_PATH = r'D:\desktop\20250421-CYC\20250421-CE-BUP-CYC-10000-2000-100nl-3S-50cm-4_html'  # 内置测试用报告路径
        # D:\desktop\20250421-CYC\20250421-CE-BUP-CYC-10000-2000-100nl-3S-50cm-2_html
        #D:\desktop\20250421-CYC\20250421-CE-BUP-CYC-10000-2000-100nl-3S-50cm-4_html

    class Handler(SimpleHTTPRequestHandler):
        def end_headers(self):
            # 禁用缓存
            self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Expires', '0')
            super().end_headers()

        def translate_path(self, path):
            base_dir = os.path.abspath(ServerControlTest._TEST_REPORT_PATH)
            path = path.split('?', 1)[0]
            path = os.path.normpath(os.path.join(base_dir, *path.split('/')))
            
            if not os.path.abspath(path).startswith(base_dir):
                self.send_error(403, "Forbidden path traversal attempt")
                return '/dev/null'
                
            print(f"[安全路径] 请求: {self.path} -> 服务路径: {path}")
            return path

    @staticmethod
    def stop_active_server():
        if ServerControlTest._active_server:
            try:
                # 保持原有套接字配置
                ServerControlTest._active_server.socket.setsockopt(
                    socket.SOL_SOCKET, socket.SO_REUSEADDR, 1
                )
                # 终止监控线程
                if ServerControlTest._active_monitor:
                    try:
                        print("正在终止监控线程...")
                        ServerControlTest._active_monitor.join(timeout=0.5)
                        if ServerControlTest._active_monitor.is_alive():
                            print("[警告] 监控线程未正常退出，强制终止")
                        else:
                            print("[成功] 监控线程已终止")
                    except Exception as e:
                        print(f"[异常] 终止监控线程时出错: {str(e)}")
                
                # 停止服务器主循环
                try:
                    print("正在关闭服务器主循环...")
                    ServerControlTest._active_server.shutdown()
                    print("[成功] 服务器主循环已停止")
                except Exception as e:
                    print(f"[异常] 关闭服务器主循环失败: {str(e)}")
                
                # 释放套接字资源
                try:
                    print("正在释放端口资源...")
                    ServerControlTest._active_server.server_close()
                    print("[成功] 端口资源已释放")
                except Exception as e:
                    print(f"[异常] 释放端口资源失败: {str(e)}")
                    
            except KeyboardInterrupt:
                print("[强制中断] 接收到系统中断信号")
            finally:
                try:
                    ServerControlTest._active_server = None
                    ServerControlTest._active_monitor = None
                    print("[状态] 所有资源引用已清除")
                except Exception as e:
                    print(f"[异常] 清理资源时出错: {str(e)}")

    @staticmethod
    def start_report_server():
        try:
            ServerControlTest.stop_active_server()
            
            # 验证目录和文件
            if not os.path.exists(ServerControlTest._TEST_REPORT_PATH):
                raise Exception(f"报告目录不存在: {ServerControlTest._TEST_REPORT_PATH}")
            
            required_files = [
                "topmsv/index.html",
                "topmsv/visual/prsm.html"
            ]
            for f in required_files:
                if not os.path.exists(os.path.join(ServerControlTest._TEST_REPORT_PATH, f)):
                    raise Exception(f"必需文件缺失: {f}")

            # 端口检查
            try:
                test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                test_socket.bind(('0.0.0.0', 8000))
                test_socket.close()
            except OSError:
                raise Exception("端口8000被占用")

            # 启动服务器
            ServerControlTest._active_server = ThreadingHTTPServer(
                ('0.0.0.0', 8000),
                ServerControlTest.Handler
            )
            
            # 启动监控线程
            ServerControlTest._active_monitor = threading.Thread(
                target=ServerControlTest.server_monitor,
                args=(ServerControlTest._active_server,),
                daemon=True
            )
            ServerControlTest._active_monitor.start()
            
            # 主服务线程
            threading.Thread(
                target=ServerControlTest._active_server.serve_forever,
                daemon=True
            ).start()
            
            return ServerControlTest.get_url()
        except Exception as e:
            raise Exception(f"测试服务器启动失败: {str(e)}")

    @staticmethod
    def get_url():
        local_ip = ServerControlTest.get_local_ip()
        # 移除时间戳参数，改为在Handler中控制缓存
        return f"http://{local_ip}:8000/topmsv/index.html"

    @staticmethod
    def get_local_ip():
        """获取本机IP"""
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(('8.8.8.8', 80))
            return s.getsockname()[0]
        finally:
            s.close()

    @staticmethod
    def server_monitor(server):
        """60分钟自动关闭"""
        start_time = time.time()
        while time.time() - start_time < 3600:
            time.sleep(10)
        server.shutdown()

if __name__ == '__main__':
    try:
        url = ServerControlTest.start_report_server()
        print(f"测试服务器已启动，访问地址：{url}")
        # 添加持续运行循环防止二次中断
        while True:
            time.sleep(3600)  # 改为长睡眠减少中断概率
    except KeyboardInterrupt:
        print("\n正在优雅关闭服务器...")
        ServerControlTest.stop_active_server()
        print("服务已停止")