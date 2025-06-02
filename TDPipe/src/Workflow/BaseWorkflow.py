from PyQt5.QtCore import QThread, pyqtSignal
import subprocess
from abc import abstractmethod
from wakepy import keep 

class BaseWorkflow(QThread):
    # 定义信号用于向GUI发送输出
    output_received = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.process = None
        self.commands = []
        self.check_fns = []
        self.gap_nums = []

    @abstractmethod
    def prepare_workflow(self):
        """准备工作流程，子类必须实现此方法来设置commands"""
        pass
        
    def run(self):         
        self.prepare_workflow()
        with keep.presenting():
            for command, check_fn, gap_num in zip(self.commands, self.check_fns, self.gap_nums):
                self.log("command: " + ' '.join(command))
                self.process = subprocess.Popen(
                    command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                    shell=False
                )

                repeat_num = 0
                while True:
                    output = self.process.stdout.readline()
                    if output == '' and self.process.poll() is not None:
                        break
                    if output:
                        if check_fn == None or not check_fn(output) or repeat_num >= gap_num:
                            self.log(output.strip())
                            repeat_num = 0
                        else:
                            repeat_num += 1
                
                # 等待子进程结束
                self.process.wait()
                self.process = None
                    
        self.log("============Process finished============")

    def log(self, text):
        self.output_received.emit(text)

if __name__ == '__main__':
    pass