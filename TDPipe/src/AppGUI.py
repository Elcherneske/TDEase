import sys
import time
import os
import subprocess
import webbrowser
from PyQt5.QtWidgets import (QWidget, QTabWidget, QHBoxLayout,
                             QApplication, QMessageBox)
from PyQt5.QtCore import QThread, pyqtSignal
from Args import Args
from GUI.ToolsTab import ToolsTab
from GUI import MSConvertConfigTab
from GUI import WorkflowConfigTab
from GUI import RunTab
from GUI import ToppicConfigTab
from GUI import InformedProteomicsConfigTab
from GUI import SpectrumProcessingTab
from Workflow.WorkflowManager import WorkflowManager

class StreamlitThread(QThread):
    output_signal = pyqtSignal(str)
    started_signal = pyqtSignal()
    error_signal = pyqtSignal(str)

    def __init__(self, python_path, streamlit_file):
        super().__init__()
        self.python_path = python_path
        self.streamlit_file = streamlit_file
        self.process = None

    def run(self):
        try:
            self.output_signal.emit("Starting Streamlit server...\n")
            
            self.process = subprocess.Popen(
                [self.python_path, "-m", "streamlit", "run", self.streamlit_file],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )

            # 等待一小段时间让Streamlit启动
            time.sleep(1)
            
            if self.process.poll() is None:  # 如果进程还在运行
                self.output_signal.emit("Streamlit server started successfully.\n")
                self.started_signal.emit()
            else:
                error = self.process.stderr.read()
                self.error_signal.emit(f"Failed to start Streamlit server: {error}")

            # 持续读取输出
            while self.process.poll() is None:
                output = self.process.stdout.readline()
                if output:
                    self.output_signal.emit(output.strip())
                error = self.process.stderr.readline()
                if error:
                    self.output_signal.emit(f"Error: {error.strip()}")

        except Exception as e:
            self.error_signal.emit(f"Error starting Streamlit: {str(e)}")

    def stop(self):
        if self.process and self.process.poll() is None:
            try:
                self.process.terminate()
                time.sleep(0.25)
                if self.process.poll() is None:
                    self.process.kill()
                self.output_signal.emit("Streamlit server stopped.\n")
            except Exception as e:
                self.error_signal.emit(f"Error stopping Streamlit: {str(e)}")

class AppGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.args = Args()  # 创建Args实例
        self.tabs = None
        self.output_tab = None
        self.streamlit_thread = None
        self._init_ui()
    
    def _init_ui(self):
        self.setWindowTitle('Top-Down Mass Spectrometry Analysis Pipeline')
        self.setGeometry(100, 100, 1200, 1200)

        # 创建标签页
        self.tabs = QTabWidget()
        
        # 创建各个标签页实例
        self.tools_tab = ToolsTab(self.args)
        self.workflow_config_tab = WorkflowConfigTab(self.args)
        self.msconvert_config_tab = MSConvertConfigTab(self.args)
        self.toppic_config_tab = ToppicConfigTab(self.args)
        self.informed_proteomics_config_tab = InformedProteomicsConfigTab(self.args)
        self.run_tab = RunTab(self.args)
        self.spectrum_processing_tab = SpectrumProcessingTab(self.args)

        # 添加标签页
        self.tabs.addTab(self.tools_tab, "Tools")
        self.tabs.addTab(self.workflow_config_tab, "Workflow")
        self.tabs.addTab(self.msconvert_config_tab, "MSConvert")
        self.tabs.addTab(self.toppic_config_tab, "Toppic")
        self.tabs.addTab(self.informed_proteomics_config_tab, "Informed Proteomics")
        self.tabs.addTab(self.spectrum_processing_tab, "Spectrum Processing")
        self.tabs.addTab(self.run_tab, "Run")
        
        # 添加运行接口
        self.run_btn = self.run_tab.run_btn
        self.stop_btn = self.run_tab.stop_btn
        self.run_btn.clicked.connect(self._run_process)
        self.stop_btn.clicked.connect(self._stop_process)
        
        # 添加可视化按钮的点击事件
        self.vis_btn = self.run_tab.vis_btn
        self.vis_btn.clicked.connect(self._streamlit_process)

        # 主布局
        layout = QHBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.addWidget(self.tabs)
        self.setLayout(layout)

    def update_output(self, text):
        self.run_tab.update_output(text)
    
    def _run_process(self):
        mode = self.args.get_config('workflow', None)
        self.workflow = WorkflowManager.create_workflow(mode, self.args)
        self.workflow.output_received.connect(self.update_output)
        self.workflow.start()
    
    def _stop_process(self):
        if hasattr(self, 'workflow') and self.workflow and self.workflow.isRunning():
            # 首先终止当前正在运行的子进程
            if hasattr(self.workflow, 'process') and self.workflow.process:
                try:
                    self.workflow.commands = []
                    self.workflow.process.terminate()
                    
                    # 给进程一点时间来正常关闭
                    time.sleep(0.5)
                    
                    # 检查进程是否仍在运行
                    if self.workflow.process and self.workflow.process.poll() is None:
                        self.workflow.process.kill()

                    self.update_output("Process has been interrupted.")
                except Exception as e:
                    self.update_output(f"Error interrupting subprocess: {str(e)}")
            
            # 然后终止工作流线程
            try:
                self.workflow.terminate()
                self.update_output("Workflow has been stopped.")
            except Exception as e:
                self.update_output(f"Error stopping workflow: {str(e)}")
                
            self.update_output("Processing has been interrupted.")
        
    def _streamlit_process(self):
        # 如果线程尚未创建或已经终止，则创建并启动线程
        if self.streamlit_thread is None or not self.streamlit_thread.isRunning():
            dirname = os.path.dirname(os.path.dirname(__file__))
            filename = os.path.join(dirname, 'TDVis', 'MainPage.py')
            if not os.path.exists(filename):
                QMessageBox.warning(self, "Warning", "Streamlit file not found.")
                return
            if not self.args.get_config('tools', 'python'):
                QMessageBox.warning(self, "Warning", "Python path not set.")
                return
            
            # 创建并启动Streamlit线程
            self.streamlit_thread = StreamlitThread(
                self.args.get_config('tools', 'python'),
                filename
            )
            
            # 连接信号
            self.streamlit_thread.output_signal.connect(self.update_output)
            self.streamlit_thread.error_signal.connect(lambda msg: QMessageBox.warning(self, "Error", msg))
            self.streamlit_thread.started_signal.connect(lambda: webbrowser.open('http://localhost:8501'))
            
            # 启动线程
            self.streamlit_thread.start()
        else:
            # 如果Streamlit已经在运行，直接打开浏览器
            webbrowser.open('http://localhost:8501')
    
    def closeEvent(self, event):
        # 窗口关闭时终止streamlit线程
        if self.streamlit_thread and self.streamlit_thread.isRunning():
            self.streamlit_thread.stop()
            self.streamlit_thread.wait()  # 等待线程结束
        event.accept()
        
