from PyQt5.QtWidgets import (QWidget, QPushButton, QLabel, QVBoxLayout,
                            QHBoxLayout, QGroupBox, QLineEdit, QFileDialog,
                            QMessageBox, QProgressDialog, QTextEdit)
from PyQt5.QtCore import QCoreApplication, Qt, QThread, pyqtSignal
from .Setting import ToolsSetting
import os
import subprocess
import tempfile
import sys
from PyQt5.QtGui import QFont

class InstallThread(QThread):
    output_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(bool, str)  # success, message

    def __init__(self, python_path, install_script_path):
        super().__init__()
        self.python_path = python_path
        self.install_script_path = install_script_path

    def run(self):
        try:
            self.output_signal.emit("Starting library installation...\n")
            
            process = subprocess.Popen(
                [self.python_path, self.install_script_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )

            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    self.output_signal.emit(output.strip())

            return_code = process.poll()
            
            if return_code == 0:
                self.output_signal.emit("\nInstallation completed successfully!")
                self.finished_signal.emit(True, "All required libraries have been installed successfully!")
            else:
                error_output = process.stderr.read()
                self.output_signal.emit(f"\nError during installation:\n{error_output}")
                self.finished_signal.emit(False, f"Some libraries failed to install:\n{error_output}")

        except Exception as e:
            error_msg = f"\nAn error occurred: {str(e)}"
            self.output_signal.emit(error_msg)
            self.finished_signal.emit(False, f"An error occurred during installation: {str(e)}")

class ToolsTab(QWidget):
    def __init__(self, args):
        super().__init__()
        self.args = args
        self.setting = ToolsSetting()
        self._init_ui()
    
    def _init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)
        # 各工具路径分组
        group_creators = [
            self._create_msconvert_group,
            self._create_toppic_group,
            self._create_topfd_group,
            self._create_topmg_group,
            self._create_topdiff_group,
            self._create_pbfgen_group,
            self._create_promex_group,
            self._create_mspathfinder_group,
            self._create_python_group
        ]
        for creator in group_creators:
            group = creator()
            layout.addWidget(group)
        layout.addStretch()
        self.setLayout(layout)
    
    def _create_msconvert_group(self):
        group = QGroupBox("MSConvert Setting")
        layout = QHBoxLayout()
        msconvert_path = QLineEdit()
        if self.setting.get_config('Tools', 'msconvert'):
            msconvert_path.setText(self.setting.get_config('Tools', 'msconvert'))
            self.args.set_config('tools', 'msconvert', self.setting.get_config('Tools', 'msconvert'))
        else:
            msconvert_path.setPlaceholderText("Please select the path of MSConvert")
        msconvert_path.textChanged.connect(lambda text: (self.args.set_config('tools', 'msconvert', text), self.setting.set_config('Tools', 'msconvert', text)))
        browse_btn = QPushButton("Browse")
        update_btn = QPushButton("Update")
        browse_btn.clicked.connect(lambda: self._browse_file(msconvert_path))
        
        layout.addWidget(QLabel("MSConvert path:"))
        layout.addWidget(msconvert_path)
        layout.addWidget(browse_btn)
        layout.addWidget(update_btn)
        group.setLayout(layout)
        return group
    
    def _create_toppic_group(self):
        group = QGroupBox("TopPIC setting")
        layout = QHBoxLayout()
        toppic_path = QLineEdit()
        if self.setting.get_config('Tools', 'toppic'):
            toppic_path.setText(self.setting.get_config('Tools', 'toppic'))
            self.args.set_config('tools', 'toppic', self.setting.get_config('Tools', 'toppic'))
        else:
            toppic_path.setPlaceholderText("Please select the path of TopPIC")
        toppic_path.textChanged.connect(lambda text: (self.args.set_config('tools', 'toppic', text), self.setting.set_config('Tools', 'toppic', text)))
        browse_btn = QPushButton("browse")
        update_btn = QPushButton("update")
        browse_btn.clicked.connect(lambda: self._browse_file(toppic_path))
        
        layout.addWidget(QLabel("TopPIC path:"))
        layout.addWidget(toppic_path)
        layout.addWidget(browse_btn)
        layout.addWidget(update_btn)
        group.setLayout(layout)
        return group
    
    def _create_topfd_group(self):
        group = QGroupBox("TopFD setting")
        layout = QHBoxLayout()
        topfd_path = QLineEdit()
        if self.setting.get_config('Tools', 'topfd'):
            topfd_path.setText(self.setting.get_config('Tools', 'topfd'))
            self.args.set_config('tools', 'topfd', self.setting.get_config('Tools', 'topfd'))
        else:
            topfd_path.setPlaceholderText("Please select the path of TopFD")
        topfd_path.textChanged.connect(lambda text: (self.args.set_config('tools', 'topfd', text), self.setting.set_config('Tools', 'topfd', text)))
        browse_btn = QPushButton("browse")
        update_btn = QPushButton("update")
        browse_btn.clicked.connect(lambda: self._browse_file(topfd_path))

        layout.addWidget(QLabel("TopFD path:"))
        layout.addWidget(topfd_path)
        layout.addWidget(browse_btn)
        layout.addWidget(update_btn)
        group.setLayout(layout)
        return group
    
    def _create_topmg_group(self):
        group = QGroupBox("TopMG setting")
        layout = QHBoxLayout()
        topmg_path = QLineEdit()
        if self.setting.get_config('Tools', 'topmg'):
            topmg_path.setText(self.setting.get_config('Tools', 'topmg'))
            self.args.set_config('tools', 'topmg', self.setting.get_config('Tools', 'topmg'))
        else:
            topmg_path.setPlaceholderText("Please select the path of TopMG")
        topmg_path.textChanged.connect(lambda text: (self.args.set_config('tools', 'topmg', text), self.setting.set_config('Tools', 'topmg', text)))
        browse_btn = QPushButton("browse")
        update_btn = QPushButton("update")
        browse_btn.clicked.connect(lambda: self._browse_file(topmg_path))

        layout.addWidget(QLabel("TopMG path:"))
        layout.addWidget(topmg_path)
        layout.addWidget(browse_btn)
        layout.addWidget(update_btn)
        group.setLayout(layout)
        return group

    def _create_topdiff_group(self):
        group = QGroupBox("TopDiff setting")
        layout = QHBoxLayout()
        topdiff_path = QLineEdit()
        if self.setting.get_config('Tools', 'topdiff'):
            topdiff_path.setText(self.setting.get_config('Tools', 'topdiff'))
            self.args.set_config('tools', 'topdiff', self.setting.get_config('Tools', 'topdiff'))
        else:
            topdiff_path.setPlaceholderText("Please select the path of TopDiff")
        topdiff_path.textChanged.connect(lambda text: (self.args.set_config('tools', 'topdiff', text), self.setting.set_config('Tools', 'topdiff', text)))
        browse_btn = QPushButton("browse")
        update_btn = QPushButton("update")
        browse_btn.clicked.connect(lambda: self._browse_file(topdiff_path))

        layout.addWidget(QLabel("TopDiff path:"))
        layout.addWidget(topdiff_path)
        layout.addWidget(browse_btn)
        layout.addWidget(update_btn)
        group.setLayout(layout)
        return group

    def _create_pbfgen_group(self):
        group = QGroupBox("Pbfgen setting")
        layout = QHBoxLayout()
        pbfgen_path = QLineEdit()
        if self.setting.get_config('Tools', 'pbfgen'):
            pbfgen_path.setText(self.setting.get_config('Tools', 'pbfgen'))
            self.args.set_config('tools', 'pbfgen', self.setting.get_config('Tools', 'pbfgen'))
        else:
            pbfgen_path.setPlaceholderText("Please select the path of PBFGen")
        pbfgen_path.textChanged.connect(lambda text: (self.args.set_config('tools', 'pbfgen', text), self.setting.set_config('Tools', 'pbfgen', text)))
        browse_btn = QPushButton("browse")
        update_btn = QPushButton("update")
        browse_btn.clicked.connect(lambda: self._browse_file(pbfgen_path))
        
        layout.addWidget(QLabel("PBFGen path:"))
        layout.addWidget(pbfgen_path)
        layout.addWidget(browse_btn)
        layout.addWidget(update_btn)
        group.setLayout(layout)
        return group
    
    def _create_promex_group(self):
        group = QGroupBox("Promex setting")
        layout = QHBoxLayout()
        promex_path = QLineEdit()
        if self.setting.get_config('Tools', 'promex'):
            promex_path.setText(self.setting.get_config('Tools', 'promex'))
            self.args.set_config('tools', 'promex', self.setting.get_config('Tools', 'promex'))
        else:
            promex_path.setPlaceholderText("Please select the path of Promex")
        promex_path.textChanged.connect(lambda text: (self.args.set_config('tools', 'promex', text), self.setting.set_config('Tools', 'promex', text)))
        browse_btn = QPushButton("browse")
        update_btn = QPushButton("update")
        browse_btn.clicked.connect(lambda: self._browse_file(promex_path))
        
        layout.addWidget(QLabel("Promex path:"))
        layout.addWidget(promex_path)
        layout.addWidget(browse_btn)
        layout.addWidget(update_btn)
        group.setLayout(layout)
        return group

    def _create_mspathfinder_group(self):
        group = QGroupBox("MSPathfinder setting")
        layout = QHBoxLayout()
        mspathfinder_path = QLineEdit()
        if self.setting.get_config('Tools', 'mspathfinder'):
            mspathfinder_path.setText(self.setting.get_config('Tools', 'mspathfinder'))
            self.args.set_config('tools', 'mspathfinder', self.setting.get_config('Tools', 'mspathfinder'))
        else:
            mspathfinder_path.setPlaceholderText("Please select the path of MSPathfinder")
        mspathfinder_path.textChanged.connect(lambda text: (self.args.set_config('tools', 'mspathfinder', text), self.setting.set_config('Tools', 'mspathfinder', text)))
        browse_btn = QPushButton("browse")
        update_btn = QPushButton("update")
        browse_btn.clicked.connect(lambda: self._browse_file(mspathfinder_path))
        
        layout.addWidget(QLabel("MSPathfinder path:"))
        layout.addWidget(mspathfinder_path)
        layout.addWidget(browse_btn)
        layout.addWidget(update_btn)
        group.setLayout(layout)
        return group
    
    def _create_python_group(self):
        group = QGroupBox("Python Setting")
        layout = QVBoxLayout()
        
        # Python path input row
        path_layout = QHBoxLayout()
        python_path = QLineEdit()
        if self.setting.get_config('Tools', 'python'):
            python_path.setText(self.setting.get_config('Tools', 'python'))
            self.args.set_config('tools', 'python', self.setting.get_config('Tools', 'python'))
        else:
            python_path.setPlaceholderText("Please select the path of Python executable")
        python_path.textChanged.connect(lambda text: (self.args.set_config('tools', 'python', text), self.setting.set_config('Tools', 'python', text)))
        
        browse_btn = QPushButton("browse")
        check_btn = QPushButton("check")
        install_btn = QPushButton("install libraries")
        
        path_layout.addWidget(QLabel("Python path:"))
        path_layout.addWidget(python_path)
        path_layout.addWidget(browse_btn)
        path_layout.addWidget(check_btn)
        path_layout.addWidget(install_btn)
        
        # Required libraries info
        req_label = QLabel("Required libraries: pandas, streamlit, pyopenms, numpy, psycopg2, polars, sqlalchemy, pymysql, scipy, plotly, pyteomics")
        # req_label.setStyleSheet("color: #666; font-style: italic;")
        cmd_label = QLabel("To install manually via cmd:\npip install pandas streamlit pyopenms numpy psycopg2 polars sqlalchemy pymysql scipy plotly pyteomics")
        cmd_label.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard)
        
        # Output text box
        output_text = QTextEdit()
        output_text.setMaximumHeight(100)  # Set maximum height to about 3-5 lines
        output_text.setReadOnly(True)
        output_text.setVisible(False)  # Initially hidden

        browse_btn.clicked.connect(lambda: self._browse_file(python_path))
        check_btn.clicked.connect(lambda: self._check_python(python_path.text()))
        install_btn.clicked.connect(lambda: self._install_libraries(python_path.text(), output_text))
        
        layout.addLayout(path_layout)
        layout.addWidget(req_label)
        layout.addWidget(cmd_label)
        layout.addWidget(output_text)
        
        group.setLayout(layout)
        return group
    
    def _check_python(self, python_path):
        if not python_path:
            QMessageBox.warning(self, "Warning", "Please select a Python path first.")
            return
        try:
            check_script_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "Tools", "check_library.py")
            if not os.path.exists(check_script_path):
                QMessageBox.warning(self, "Warning", "check_library.py not found.")
                return
            # Check Python version and libraries
            result = subprocess.run([python_path, check_script_path], capture_output=True, text=True)

            output = result.stdout.strip()
            if result.returncode == 0:
                QMessageBox.information(self, "Success", f"Python check passed!\n\n{output}")
            else:
                QMessageBox.warning(self, "Warning", f"Python found, but missing required libraries:\n\n{output}")
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")
    
    def _install_libraries(self, python_path, output_text):
        if not python_path:
            QMessageBox.warning(self, "Warning", "Please select a Python path first.")
            return

        install_script_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "Tools", "install_library.py")
        if not os.path.exists(install_script_path):
            QMessageBox.warning(self, "Warning", "install_library.py not found.")
            return

        # Show the output text box
        output_text.setVisible(True)
        output_text.clear()

        # Create and start the installation thread
        self.install_thread = InstallThread(python_path, install_script_path)
        
        # Connect signals
        self.install_thread.output_signal.connect(lambda text: self._update_output(text, output_text))
        self.install_thread.finished_signal.connect(self._handle_installation_finished)
        
        # Start the thread
        self.install_thread.start()

    def _update_output(self, text, output_text):
        output_text.append(text)
        # Scroll to the bottom
        output_text.verticalScrollBar().setValue(output_text.verticalScrollBar().maximum())
        QCoreApplication.processEvents()

    def _handle_installation_finished(self, success, message):
        if success:
            QMessageBox.information(self, "Success", message)
        else:
            QMessageBox.warning(self, "Warning", message)
    
    def _browse_file(self, line_edit):
        from PyQt5.QtWidgets import QFileDialog
        filename, _ = QFileDialog.getOpenFileName(self, "Select file")
        if filename:
            line_edit.setText(filename)