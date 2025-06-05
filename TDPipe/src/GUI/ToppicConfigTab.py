from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, 
                            QLabel, QLineEdit, QComboBox, QCheckBox, 
                            QScrollArea, QPushButton, QSpinBox, QDoubleSpinBox,
                            QFileDialog, QMessageBox, QFrame, QGridLayout)
from PyQt5.QtGui import QFont, QPalette, QColor
from PyQt5.QtCore import Qt
from .Setting import Setting

class ToppicConfigTab(QWidget):
    def __init__(self, args):
        super().__init__()
        self.args = args
        # 用于保存所有UI控件
        self.ui = {
            'topfd': {},
            'toppic': {},
            'topmg': {}
        }
        # 初始化UI
        self._init_ui()
    
    def _init_ui(self):

        # 创建主布局
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)  # 增加主要组件之间的间距
        
        # Add reference text with clickable link
        reference_label = QLabel()
        reference_label.setText('<a href="https://www.toppic.org/software/toppic/manual.html" style="color: blue; font-style: italic;">For detailed parameter descriptions, please refer to the official documentation</a>')
        reference_label.setOpenExternalLinks(True)
        reference_label.setWordWrap(True)
        main_layout.addWidget(reference_label)
        
        # 添加保存/加载按钮
        buttons_layout = QHBoxLayout()
        save_button = QPushButton("Save Settings")
        load_button = QPushButton("Load Settings")
        save_button.clicked.connect(self._save_settings)
        load_button.clicked.connect(self._load_settings)
        buttons_layout.addWidget(save_button)
        buttons_layout.addWidget(load_button)
        main_layout.addLayout(buttons_layout)
        
        # 创建滚动区域
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout()
        scroll_layout.setSpacing(30)  # 增加配置组之间的间距
        
        # TopFD 配置组
        topfd_group = self._create_topfd_group()
        topfd_group.setStyleSheet("""
            QGroupBox {
                background-color: #f0f8ff;
                border: 2px solid #4682b4;
                border-radius: 6px;
                margin-top: 12px;
                font-weight: bold;
            }
            QGroupBox::title {
                color: #4682b4;
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        scroll_layout.addWidget(topfd_group)
        
        # 添加分隔线
        line1 = QFrame()
        line1.setFrameShape(QFrame.HLine)
        line1.setFrameShadow(QFrame.Sunken)
        line1.setStyleSheet("background-color: #4682b4;")
        scroll_layout.addWidget(line1)
        
        # TopPIC 配置组
        toppic_group = self._create_toppic_configuration_group()
        toppic_group.setStyleSheet("""
            QGroupBox {
                background-color: #fff0f5;
                border: 2px solid #db7093;
                border-radius: 6px;
                margin-top: 12px;
                font-weight: bold;
            }
            QGroupBox::title {
                color: #db7093;
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        scroll_layout.addWidget(toppic_group)
        
        # 添加分隔线
        line2 = QFrame()
        line2.setFrameShape(QFrame.HLine)
        line2.setFrameShadow(QFrame.Sunken)
        line2.setStyleSheet("background-color: #db7093;")
        scroll_layout.addWidget(line2)
        
        # TopMG 配置组
        topmg_group = self._create_topmg_configuration_group()
        topmg_group.setStyleSheet("""
            QGroupBox {
                background-color: #f0fff0;
                border: 2px solid #2e8b57;
                border-radius: 6px;
                margin-top: 12px;
                font-weight: bold;
            }
            QGroupBox::title {
                color: #2e8b57;
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        scroll_layout.addWidget(topmg_group)
        
        scroll_widget.setLayout(scroll_layout)
        scroll.setWidget(scroll_widget)
        main_layout.addWidget(scroll)
        self.setLayout(main_layout)
    
    def _save_settings(self):
        """保存当前设置到文件"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Toppic Settings", "", "Settings File (*.ini);;All Files (*)"
        )
        
        if not file_path:
            QMessageBox.information(self, "Error", "No save path selected!")
            return
            
        try:
            # 从self.ui收集当前设置
            settings = {
                'topfd': self._collect_topfd_settings(),
                'toppic': self._collect_toppic_settings(),
                'topmg': self._collect_topmg_settings()
            }
            
            # 使用Setting类保存设置
            Setting.save(file_path, settings)
            QMessageBox.information(self, "Success", "Settings saved successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save settings: {str(e)}")
    
    def _collect_topfd_settings(self):
        """收集TopFD设置"""
        settings = {}
        for key, widget in self.ui['topfd'].items():
            if isinstance(widget, QSpinBox) or isinstance(widget, QDoubleSpinBox):
                settings[key] = str(widget.value())
            elif isinstance(widget, QLineEdit):
                settings[key] = widget.text()
            elif isinstance(widget, QComboBox):
                settings[key] = widget.currentText()
            elif isinstance(widget, QCheckBox):
                settings[key] = str(widget.isChecked())
        return settings
    
    def _collect_toppic_settings(self):
        """收集TopPIC设置"""
        settings = {}
        for key, widget in self.ui['toppic'].items():
            if isinstance(widget, QSpinBox) or isinstance(widget, QDoubleSpinBox):
                settings[key] = str(widget.value())
            elif isinstance(widget, QLineEdit):
                settings[key] = widget.text()
            elif isinstance(widget, QComboBox):
                settings[key] = widget.currentText()
            elif isinstance(widget, QCheckBox):
                settings[key] = str(widget.isChecked())
        return settings
    
    def _collect_topmg_settings(self):
        """收集TopMG设置"""
        settings = {}
        for key, widget in self.ui['topmg'].items():
            if isinstance(widget, QSpinBox) or isinstance(widget, QDoubleSpinBox):
                settings[key] = str(widget.value())
            elif isinstance(widget, QLineEdit):
                settings[key] = widget.text()
            elif isinstance(widget, QComboBox):
                settings[key] = widget.currentText()
            elif isinstance(widget, QCheckBox):
                settings[key] = str(widget.isChecked())
        return settings
    
    def _load_settings(self):
        """从文件加载设置"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Load Toppic Settings", "", "Settings File (*.ini);;All Files (*)"
        )
        
        if not file_path:
            QMessageBox.information(self, "Error", "No load path selected!")
            return
            
        try:
            # 创建Setting实例加载配置
            setting_instance = Setting(file_path)
            
            # 更新TopFD设置
            self._update_topfd_settings(setting_instance)
            
            # 更新TopPIC设置
            self._update_toppic_settings(setting_instance)
            
            # 更新TopMG设置
            self._update_topmg_settings(setting_instance)
            
            QMessageBox.information(self, "Success", "Settings loaded successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load settings: {str(e)}")
    
    def _update_topfd_settings(self, setting_instance):
        """从配置更新TopFD设置"""
        for key, widget in self.ui['topfd'].items():
            value = setting_instance.get('topfd', key)
            if value:
                if isinstance(widget, QSpinBox):
                    widget.setValue(int(value))
                    self.args.set_config('topfd', key, int(value))
                elif isinstance(widget, QDoubleSpinBox):
                    widget.setValue(float(value))
                    self.args.set_config('topfd', key, float(value))
                elif isinstance(widget, QLineEdit):
                    widget.setText(value)
                    self.args.set_config('topfd', key, value)
                elif isinstance(widget, QComboBox):
                    widget.setCurrentText(value)
                    self.args.set_config('topfd', key, value)
                elif isinstance(widget, QCheckBox):
                    widget.setChecked(value.lower() == 'true')
                    self.args.set_config('topfd', key, value.lower() == 'true')
            else:
                if isinstance(widget, QLineEdit):
                    widget.setText(value)
                    self.args.set_config('topfd', key, value)
    
    def _update_toppic_settings(self, setting_instance):
        """从配置更新TopPIC设置"""
        for key, widget in self.ui['toppic'].items():
            value = setting_instance.get('toppic', key)
            if value:
                if isinstance(widget, QSpinBox):
                    widget.setValue(int(value))
                    self.args.set_config('toppic', key, int(value))
                elif isinstance(widget, QDoubleSpinBox):
                    widget.setValue(float(value))
                    self.args.set_config('toppic', key, float(value))
                elif isinstance(widget, QLineEdit):
                    widget.setText(value)
                    self.args.set_config('toppic', key, value)
                elif isinstance(widget, QComboBox):
                    widget.setCurrentText(value)
                    self.args.set_config('toppic', key, value)
                elif isinstance(widget, QCheckBox):
                    widget.setChecked(value.lower() == 'true')
                    self.args.set_config('toppic', key, value.lower() == 'true')
            else:
                if isinstance(widget, QLineEdit):
                    widget.setText(value)
                    self.args.set_config('toppic', key, value)
    
    def _update_topmg_settings(self, setting_instance):
        """从配置更新TopMG设置"""
        for key, widget in self.ui['topmg'].items():
            value = setting_instance.get('topmg', key)
            if value:
                if isinstance(widget, QSpinBox):
                    widget.setValue(int(value))
                    self.args.set_config('topmg', key, int(value))
                elif isinstance(widget, QDoubleSpinBox):
                    widget.setValue(float(value))
                    self.args.set_config('topmg', key, float(value))
                elif isinstance(widget, QLineEdit):
                    widget.setText(value)
                    self.args.set_config('topmg', key, value)
                elif isinstance(widget, QComboBox):
                    widget.setCurrentText(value)
                    self.args.set_config('topmg', key, value)
                elif isinstance(widget, QCheckBox):
                    widget.setChecked(value.lower() == 'true')
                    self.args.set_config('topmg', key, value.lower() == 'true')
            else:
                if isinstance(widget, QLineEdit):
                    widget.setText(value)
                    self.args.set_config('topmg', key, value)

    def _create_topfd_group(self):
        group = QGroupBox("TopFD Configuration")
        layout = QVBoxLayout()
        grid = QGridLayout()
        row = 0

        # 添加 TopFD 相关参数
        grid.addWidget(QLabel("Maximum charge:"), row, 0)
        max_charge = self._create_number_input('topfd', "max-charge", 2, 99, 50)
        grid.addWidget(max_charge, row, 1)
        grid.addWidget(QLabel("MS1 S/N ratio:"), row, 2)
        ms1_sn = self._create_number_input('topfd', "ms-one-sn-ratio", 1, 1000, 3, double=True)
        grid.addWidget(ms1_sn, row, 3)
        grid.addWidget(QLabel("Default precursor window (m/z):"), row, 4)
        precursor_window = self._create_number_input('topfd', "precursor-window", 0.1, 10.0, 3.0, double=True)
        grid.addWidget(precursor_window, row, 5)
        row += 1

        grid.addWidget(QLabel("Maximum mass (Da):"), row, 0)
        max_mass = self._create_number_input('topfd', "max-mass", 1000, 1000000, 70000, double=True)
        grid.addWidget(max_mass, row, 1)
        grid.addWidget(QLabel("MS2 S/N ratio:"), row, 2)
        ms2_sn = self._create_number_input('topfd', "ms-two-sn-ratio", 1, 1000, 1, double=True)
        grid.addWidget(ms2_sn, row, 3)
        grid.addWidget(QLabel("Fragmentation:"), row, 4)
        activation_combo = QComboBox()
        activation_combo.addItems(["FILE", "CID", "ETD", "HCD", "MPD", "UVPD"])
        self.args.set_config('topfd', 'activation', 'FILE')
        activation_combo.currentTextChanged.connect(lambda text: self.args.set_config('topfd', 'activation', text))
        self.ui['topfd']['activation'] = activation_combo
        grid.addWidget(activation_combo, row, 5)
        row += 1

        grid.addWidget(QLabel("M/z error:"), row, 0)
        mz_error = self._create_number_input('topfd', "mz-error", 0.01, 10.0, 0.02, double=True)
        grid.addWidget(mz_error, row, 1)
        grid.addWidget(QLabel("ECScore cutoff:"), row, 2)
        ecscore_cutoff = self._create_number_input('topfd', "ecscore-cutoff", 0, 1, 0.5, double=True)
        grid.addWidget(ecscore_cutoff, row, 3)
        grid.addWidget(QLabel("Thread number:"), row, 4)
        thread_number = self._create_number_input('topfd', "thread-number", 1, 16, 1)
        grid.addWidget(thread_number, row, 5)
        row += 1
        
        grid.addWidget(QLabel("Minimum scan number:"), row, 0)
        min_scan_number = self._create_number_input('topfd', "min-scan-number", 1, 3, 3)
        grid.addWidget(min_scan_number, row, 1)
        layout.addLayout(grid)

        # Additional settings group
        additional_group = QGroupBox("Additional settings")
        additional_layout = QGridLayout()
        # 布尔参数及其标签
        bool_items = [
            ("Missing MS1 spectra", "missing-level-one", False),
            ("Generation of HTML files", "skip-html-folder", True),
            ("Use MS-Deconv score", "msdeconv", False),
            ("Disable final filtering", "disable-final-filtering", False),
            ("Disable additional feature search", "disable-additional-feature-search", False),
            ("Use single scan noise level", "single-scan-noise", False),
        ]
        for idx, (label, key, default) in enumerate(bool_items):
            cb = QCheckBox(label)
            cb.setChecked(default)
            if key == "skip-html-folder":
                self.args.set_config('topfd', key, not default)
                cb.stateChanged.connect(lambda state, k=key: (self.args.set_config('topfd', k, not bool(state))))
            else:
                self.args.set_config('topfd', key, default)
                cb.stateChanged.connect(lambda state, k=key: (self.args.set_config('topfd', k, bool(state))))
            self.ui['topfd'][key] = cb
            additional_layout.addWidget(cb, idx // 3, idx % 3)
        additional_group.setLayout(additional_layout)
        layout.addWidget(additional_group)
        group.setLayout(layout)
        return group

    def _create_topmg_configuration_group(self):
        group = QGroupBox("TopMG Configuration")
        layout = QVBoxLayout()
        basic_layout = QGridLayout()
        basic_layout.setHorizontalSpacing(10)
        basic_layout.setVerticalSpacing(8)    
        row = 0

        grid1 = QGridLayout()
        grid1.setHorizontalSpacing(10)
        grid1.setVerticalSpacing(8)
        grid1_row = 0

        # Fixed modification
        grid1.addWidget(QLabel("Fixed modification:"), grid1_row, 0)
        fixed_mod_combo = QComboBox()
        fixed_mod_combo.addItems(["Custom", "C57", "C58"])
        self.args.set_config('topmg', 'fixed-mod', 'Custom')
        fixed_mod_combo.currentTextChanged.connect(
            lambda text: self.args.set_config('topmg', 'fixed-mod', text)
        )
        grid1.addWidget(fixed_mod_combo, grid1_row, 1)
        self.ui['topmg']['fixed-mod'] = fixed_mod_combo
        fixed_mod_file = QLineEdit()
        fixed_mod_file.textChanged.connect(
            lambda text: self.args.set_config('topmg', 'fixed-mod-file', text)
        )
        browse_fixed_mod = QPushButton("Browse")
        browse_fixed_mod.clicked.connect(
            lambda: self._browse_file(fixed_mod_file)
        )
        grid1.addWidget(fixed_mod_file, grid1_row, 2)
        grid1.addWidget(browse_fixed_mod, grid1_row, 3)
        self.ui['topmg']['fixed-mod-file'] = fixed_mod_file
        grid1_row += 1

        # Modification file name
        grid1.addWidget(QLabel("Modification file name:"), grid1_row, 0)
        mod_file_name_input = QLineEdit()
        mod_file_name_input.textChanged.connect(
            lambda text: self.args.set_config('topmg', 'mod-file-name', text)
        )
        browse_mod_file = QPushButton("Browse")
        browse_mod_file.clicked.connect(
            lambda: self._browse_file(mod_file_name_input)
        )
        grid1.addWidget(mod_file_name_input, grid1_row, 1, 1, 2)
        grid1.addWidget(browse_mod_file, grid1_row, 3)
        self.ui['topmg']['mod-file-name'] = mod_file_name_input
        grid1_row += 1

        # N-terminal forms
        grid1.addWidget(QLabel("N-terminal forms:"), grid1_row, 0)
        n_terminal_form_input = QLineEdit()
        n_terminal_form_input.setText("NONE,NME,NME_ACETYLATION,M_ACETYLATION")
        n_terminal_form_input.textChanged.connect(
            lambda text: self.args.set_config('topmg', 'n-terminal-form', text)
        )
        grid1.addWidget(n_terminal_form_input, grid1_row, 1)
        self.ui['topmg']['n-terminal-form'] = n_terminal_form_input

        # Fragmentation Method
        grid1.addWidget(QLabel("Activation method:"), grid1_row, 2)
        activation_combo = QComboBox()
        activation_combo.addItems(["FILE", "CID", "ETD", "HCD", "UVPD"])
        self.args.set_config('topmg', 'activation', 'FILE')
        activation_combo.currentTextChanged.connect(
            lambda text: self.args.set_config('topmg', 'activation', text)
        )
        grid1.addWidget(activation_combo, grid1_row, 3)
        self.ui['topmg']['activation'] = activation_combo
        grid1_row += 1

        basic_layout.addLayout(grid1, row, 0, 1, 4)
        row += 1

        grid2 = QGridLayout()
        grid2.setHorizontalSpacing(10)
        grid2.setVerticalSpacing(8)
        grid2_row = 0

        # Mass error tolerance (PPM)
        grid2.addWidget(QLabel("Mass error tolerance (PPM):"), grid2_row, 0)
        mass_error_tolerance = self._create_number_input('topmg', "mass-error-tolerance", 1, 100, 10)
        grid2.addWidget(mass_error_tolerance, grid2_row, 1)
        # Proteoform error tolerance (Dalton)
        grid2.addWidget(QLabel("Proteoform error tolerance (Dalton):"), grid2_row, 2)
        proteoform_error_tolerance = self._create_number_input('topmg', "proteoform-error-tolerance", 0.1, 10.0, 1.2, double=True)
        grid2.addWidget(proteoform_error_tolerance, grid2_row, 3)
        grid2_row += 1

        # Maximum shift (Dalton)
        grid2.addWidget(QLabel("Maximum shift (Dalton):"), grid2_row, 0)
        max_shift = self._create_number_input('topmg', "max-shift", 0, 2000, 500, double=True)
        grid2.addWidget(max_shift, grid2_row, 1)
        # Thread number
        grid2.addWidget(QLabel("Thread number:"), grid2_row, 2)
        thread_number = self._create_number_input('topmg', "thread-number", 1, 16, 1)
        grid2.addWidget(thread_number, grid2_row, 3)
        grid2_row += 1

        # Spectrum cutoff type and value
        grid2.addWidget(QLabel("Spectrum cutoff type:"), grid2_row, 0)
        spectrum_cutoff_type_combo = QComboBox()
        spectrum_cutoff_type_combo.addItems(["EVALUE", "FDR"])
        self.args.set_config('topmg', 'spectrum-cutoff-type', 'EVALUE')
        spectrum_cutoff_type_combo.currentTextChanged.connect(
            lambda text: self.args.set_config('topmg', 'spectrum-cutoff-type', text)
        )
        grid2.addWidget(spectrum_cutoff_type_combo, grid2_row, 1)
        self.ui['topmg']['spectrum-cutoff-type'] = spectrum_cutoff_type_combo
        grid2.addWidget(QLabel("Spectrum cutoff value:"), grid2_row, 2)
        spectrum_cutoff_value = self._create_number_input('topmg', "spectrum-cutoff-value", 0.001, 1.0, 0.01, double=True)
        grid2.addWidget(spectrum_cutoff_value, grid2_row, 3)
        grid2_row += 1

        # Proteoform cutoff type and value
        grid2.addWidget(QLabel("Proteoform cutoff type:"), grid2_row, 0)
        proteoform_cutoff_type_combo = QComboBox()
        proteoform_cutoff_type_combo.addItems(["EVALUE", "FDR"])
        self.args.set_config('topmg', 'proteoform-cutoff-type', 'EVALUE')
        proteoform_cutoff_type_combo.currentTextChanged.connect(
            lambda text: self.args.set_config('topmg', 'proteoform-cutoff-type', text)
        )
        grid2.addWidget(proteoform_cutoff_type_combo, grid2_row, 1)
        self.ui['topmg']['proteoform-cutoff-type'] = proteoform_cutoff_type_combo
        grid2.addWidget(QLabel("Proteoform cutoff value:"), grid2_row, 2)
        proteoform_cutoff_value = self._create_number_input('topmg', "proteoform-cutoff-value", 0.001, 1.0, 0.01, double=True)
        grid2.addWidget(proteoform_cutoff_value, grid2_row, 3)
        grid2_row += 1

        # Proteoform graph gap and variable PTMs in gap
        grid2.addWidget(QLabel("Proteoform graph gap:"), grid2_row, 0)
        proteo_graph_gap = self._create_number_input('topmg', "proteo-graph-gap", 0, 100, 40, double=True)
        grid2.addWidget(proteo_graph_gap, grid2_row, 1)
        grid2.addWidget(QLabel("Variable PTMs in gap:"), grid2_row, 2)
        var_ptm_in_gap = self._create_number_input('topmg', "var-ptm-in-gap", 0, 10, 5)
        grid2.addWidget(var_ptm_in_gap, grid2_row, 3)
        grid2_row += 1

        # Maximum number of variable PTMs and unexpected modifications
        grid2.addWidget(QLabel("Maximum number of variable PTMs:"), grid2_row, 0)
        max_var_ptm = self._create_number_input('topmg', "var-ptm", 0, 10, 5)
        grid2.addWidget(max_var_ptm, grid2_row, 1)
        grid2.addWidget(QLabel("Maximum number of unexpected modifications:"), grid2_row, 2)
        num_shift_combo = QComboBox()
        num_shift_combo.addItems(["0", "1", "2"])
        self.args.set_config('topmg', 'num-shift', '0')
        num_shift_combo.currentTextChanged.connect(
            lambda text: self.args.set_config('topmg', 'num-shift', int(text))
        )
        grid2.addWidget(num_shift_combo, grid2_row, 3)
        self.ui['topmg']['num-shift'] = num_shift_combo
        grid2_row += 1

        # Combined file name
        grid2.addWidget(QLabel("Combined file name:"), grid2_row, 0)
        combined_file_name_input = QLineEdit()
        combined_file_name_input.textChanged.connect(
            lambda text: self.args.set_config('topmg', 'combined-file-name', text)
        )
        grid2.addWidget(combined_file_name_input, grid2_row, 1, 1, 3)
        self.ui['topmg']['combined-file-name'] = combined_file_name_input
        basic_layout.addLayout(grid2, row, 0, 1, 4)
        row += 1

        # Additional settings group
        additional_group = QGroupBox("Additional settings")
        additional_layout = QGridLayout()
        # 布尔参数及其标签
        bool_items = [
            ("Use decoy database", "decoy", False),
            ("Generation of HTML files", "skip-html-folder", True),
            ("Keep temporary files", "keep-temp-files", False),
            ("Keep decoy identifications", "keep-decoy-ids", False),
            ("Report only proteoforms from whole proteins", "whole-protein-only", False),
            ("Use ASF-DIAGONAL method", "use-asf-diagonal", False),
            ("No TopFD feature file for proteoform identification", "no-topfd-feature", False)
        ]
        for idx, (label, key, default) in enumerate(bool_items):
            cb = QCheckBox(label)
            cb.setChecked(default)
            if key == "skip-html-folder":
                self.args.set_config('topmg', key, not default)
                cb.stateChanged.connect(lambda state, k=key: (self.args.set_config('topmg', k, not bool(state))))
            else:
                self.args.set_config('topmg', key, default)
                cb.stateChanged.connect(lambda state, k=key: (self.args.set_config('topmg', k, bool(state))))
            self.ui['topmg'][key] = cb
            additional_layout.addWidget(cb, idx // 3, idx % 3)
        additional_group.setLayout(additional_layout)
        basic_layout.addWidget(additional_group, row, 0, 1, 4)
        row += 1
        group.setLayout(basic_layout)
        return group

    def _create_toppic_configuration_group(self):
        group = QGroupBox("TopPIC Configuration")
        main_layout = QVBoxLayout()

        # Basic Parameters
        basic_group = QGroupBox("Basic Parameters")
        basic_layout = QGridLayout()
        basic_layout.setHorizontalSpacing(10)
        basic_layout.setVerticalSpacing(8)
        row = 0

        grid1 = QGridLayout()
        grid1.setHorizontalSpacing(10)
        grid1.setVerticalSpacing(8)
        grid1_row = 0
        # Fixed modifications
        grid1.addWidget(QLabel("Fixed modifications:"), grid1_row, 0)
        fixed_mod_combo = QComboBox()
        fixed_mod_combo.addItems(["Custom", "C57", "C58"])
        self.args.set_config('toppic', 'fixed-mod', 'Custom')
        fixed_mod_combo.currentTextChanged.connect(
            lambda text: self.args.set_config('toppic', 'fixed-mod', text)
        )
        self.ui['toppic']['fixed-mod'] = fixed_mod_combo
        grid1.addWidget(fixed_mod_combo, grid1_row, 1)
        fixed_mod_file = QLineEdit()
        fixed_mod_file.textChanged.connect(
            lambda text: self.args.set_config('toppic', 'fixed-mod-file', text)
        )
        self.ui['toppic']['fixed-mod-file'] = fixed_mod_file
        grid1.addWidget(fixed_mod_file, grid1_row, 2)
        browse_fixed_mod = QPushButton("Browse")
        browse_fixed_mod.clicked.connect(lambda: self._browse_file(fixed_mod_file))
        grid1.addWidget(browse_fixed_mod, grid1_row, 3)
        grid1_row += 1

        # Variable PTM file
        grid1.addWidget(QLabel("Variable PTM file:"), grid1_row, 0)
        variable_ptm_file = QLineEdit()
        variable_ptm_file.textChanged.connect(
            lambda text: self.args.set_config('toppic', 'variable-ptm-file-name', text)
        )
        self.ui['toppic']['variable-ptm-file-name'] = variable_ptm_file
        grid1.addWidget(variable_ptm_file, grid1_row, 1, 1, 2)
        browse_variable_ptm = QPushButton("Browse")
        browse_variable_ptm.clicked.connect(lambda: self._browse_file(variable_ptm_file))
        grid1.addWidget(browse_variable_ptm, grid1_row, 3)
        grid1_row += 1
        basic_layout.addLayout(grid1, row, 0, 1, 4)
        row += 1

        grid2 = QGridLayout()
        grid2.setHorizontalSpacing(10)
        grid2.setVerticalSpacing(8)
        grid2_row = 0
        # Max variable PTM number
        grid2.addWidget(QLabel("Max variable PTM number:"), grid2_row, 0)
        var_ptm_num = self._create_number_input('toppic', 'variable-ptm-num', 0, 10, 3)
        grid2.addWidget(var_ptm_num, grid2_row, 1)
        # Mass error tolerance
        grid2.addWidget(QLabel("Mass error tolerance (PPM):"), grid2_row, 2)
        mass_error = self._create_number_input('toppic', 'mass-error-tolerance', 1, 100, 10, True)
        grid2.addWidget(mass_error, grid2_row, 3)
        grid2_row += 1
        # PrSM cluster error tolerance
        grid2.addWidget(QLabel("PrSM cluster error tolerance (Da):"), grid2_row, 0)
        proteoform_error = self._create_number_input('toppic', 'proteoform-error-tolerance', 0.1, 10.0, 1.2, True)
        grid2.addWidget(proteoform_error, grid2_row, 1)
        # Thread number
        grid2.addWidget(QLabel("Thread number:"), grid2_row, 2)
        thread_num = self._create_number_input('toppic', 'thread-number', 1, 32, 1)
        grid2.addWidget(thread_num, grid2_row, 3)
        grid2_row += 1
        basic_layout.addLayout(grid2, row, 0, 1, 4)
        row += 1

        bool_layout = QGridLayout()
        bool_items = [
            ("Decoy database", "decoy", False),
            ("Missing MS1 feature file", "no-topfd-feature", False),
            ("Use approximate spectra", "approximate-spectra", False)
        ]
        for idx, (label, key, default) in enumerate(bool_items):
            cb = QCheckBox(label)
            cb.setChecked(default)
            self.args.set_config('toppic', key, default)
            cb.stateChanged.connect(lambda state, key=key: self.args.set_config('toppic', key, bool(state)))
            self.ui['toppic'][key] = cb
            bool_layout.addWidget(cb, idx // 3, idx % 3)
        basic_layout.addLayout(bool_layout, row, 0, 1, 4)
        row += 1

        # Cutoff settings
        cutoff_group = QGroupBox("Cutoff settings")
        cutoff_layout = QGridLayout()
        cutoff_layout.setHorizontalSpacing(10)
        cutoff_layout.setVerticalSpacing(8)
        cutoff_layout.addWidget(QLabel("Spectrum level:"), 0, 0)
        spectrum_type = QComboBox()
        spectrum_type.addItems(["EVALUE", "FDR"])
        self.args.set_config('toppic', 'spectrum-cutoff-type', 'EVALUE')
        spectrum_type.currentTextChanged.connect(lambda text: self.args.set_config('toppic', 'spectrum-cutoff-type', text))
        self.ui['toppic']['spectrum-cutoff-type'] = spectrum_type
        cutoff_layout.addWidget(spectrum_type, 0, 1)
        cutoff_layout.addWidget(QLabel("Proteoform level:"), 0, 2)
        proteoform_type = QComboBox()
        proteoform_type.addItems(["EVALUE", "FDR"])
        self.args.set_config('toppic', 'proteoform-cutoff-type', 'EVALUE')
        proteoform_type.currentTextChanged.connect(lambda text: self.args.set_config('toppic', 'proteoform-cutoff-type', text))
        self.ui['toppic']['proteoform-cutoff-type'] = proteoform_type
        cutoff_layout.addWidget(proteoform_type, 0, 3)
        cutoff_layout.addWidget(QLabel(""), 1, 0)  # 占位
        spectrum_value = self._create_number_input('toppic', 'spectrum-cutoff-value', 0.0001, 1.0, 0.01, True)
        cutoff_layout.addWidget(spectrum_value, 1, 1)
        proteoform_value = self._create_number_input('toppic', 'proteoform-cutoff-value', 0.0001, 1.0, 0.01, True)
        cutoff_layout.addWidget(proteoform_value, 1, 3)
        cutoff_group.setLayout(cutoff_layout)
        basic_layout.addWidget(cutoff_group, row, 0, 1, 4)
        row += 1
        basic_group.setLayout(basic_layout)

        # Advanced Parameters
        advanced_group = QGroupBox("Advanced Parameters")
        advanced_layout = QGridLayout()
        advanced_layout.setHorizontalSpacing(10)
        advanced_layout.setVerticalSpacing(8)
        row = 0

        # Maximum number of mass shifts
        advanced_layout.addWidget(QLabel("Maximum number of mass shifts:"), row, 0)
        num_shift = self._create_number_input('toppic', 'num-shift', 0, 2, 1)
        advanced_layout.addWidget(num_shift, row, 1)
        # Minimum mass shift
        advanced_layout.addWidget(QLabel("Minimum mass shift (Da):"), row, 2)
        min_shift = self._create_number_input('toppic', 'min-shift', -2000, 0, -500, True)
        advanced_layout.addWidget(min_shift, row, 3)
        row += 1

        # Maximum mass shift
        advanced_layout.addWidget(QLabel("Maximum mass shift (Da):"), row, 0)
        max_shift = self._create_number_input('toppic', 'max-shift', 0, 2000, 500, True)
        advanced_layout.addWidget(max_shift, row, 1)
        # Number of combined spectra
        advanced_layout.addWidget(QLabel("Number of combined spectra:"), row, 2)
        num_combined_spectra = self._create_number_input('toppic', 'num-combined-spectra', 1, 10, 1)
        advanced_layout.addWidget(num_combined_spectra, row, 3)
        row += 1

        # Fragmentation
        advanced_layout.addWidget(QLabel("Fragmentation:"), row, 0)
        activation_combo = QComboBox()
        activation_combo.addItems(["FILE", "CID", "ETD", "HCD", "UVPD"])
        self.args.set_config('toppic', 'activation', 'FILE')
        activation_combo.currentTextChanged.connect(lambda text: self.args.set_config('toppic', 'activation', text))
        self.ui['toppic']['activation'] = activation_combo
        advanced_layout.addWidget(activation_combo, row, 1)
        row += 1

        # N-terminal forms
        advanced_layout.addWidget(QLabel("N-terminal forms:"), row, 0)
        n_terminal_form_input = QLineEdit()
        n_terminal_form_input.setText("NONE,NME,NME_ACETYLATION,M_ACETYLATION")
        n_terminal_form_input.textChanged.connect(lambda text: self.args.set_config('toppic', 'n-terminal-form', text))
        self.ui['toppic']['n-terminal-form'] = n_terminal_form_input
        advanced_layout.addWidget(n_terminal_form_input, row, 1, 1, 3)
        row += 1

        
        bool_layout = QGridLayout()
        # 布尔参数及其标签
        bool_items = [
            ("Generation of HTML files", "skip-html-folder", True),
            ("Lookup table for E-value computation", "lookup-table", False),
            ("Keep decoy identifications", "keep-decoy-ids", False),
            ("Keep intermediate files", "keep-temp-files", False),
        ]
        for idx, (label, key, default) in enumerate(bool_items):
            cb = QCheckBox(label)
            cb.setChecked(default)
            if key == "skip-html-folder":
                self.args.set_config('toppic', key, not default)
                cb.stateChanged.connect(lambda state, k=key: (self.args.set_config('toppic', k, not bool(state))))
            else:
                self.args.set_config('toppic', key, default)
                cb.stateChanged.connect(lambda state, k=key: (self.args.set_config('toppic', k, bool(state))))
            self.ui['toppic'][key] = cb
            bool_layout.addWidget(cb, 0, idx)
        advanced_layout.addLayout(bool_layout, row, 0, 1, 4)
        row += 1

        # Modification localization
        modloc_group = QGroupBox("Modification localization")
        modloc_layout = QGridLayout()
        modloc_layout.setHorizontalSpacing(10)
        modloc_layout.setVerticalSpacing(8)
        modloc_layout_row = 0
        file_layout = QGridLayout()
        file_layout.setHorizontalSpacing(10)
        file_layout.setVerticalSpacing(8)
        file_layout_row = 0
        file_layout.addWidget(QLabel("PTM file for localization:"), file_layout_row, 0)
        local_ptm_file = QLineEdit()
        local_ptm_file.textChanged.connect(lambda text: self.args.set_config('toppic', 'local-ptm-file-name', text))
        self.ui['toppic']['local-ptm-file-name'] = local_ptm_file
        file_layout.addWidget(local_ptm_file, file_layout_row, 1)
        browse_local_ptm = QPushButton("Browse")
        browse_local_ptm.clicked.connect(lambda: self._browse_file(local_ptm_file))
        file_layout.addWidget(browse_local_ptm, file_layout_row, 2)
        modloc_layout.addLayout(file_layout, modloc_layout_row, 0, 1, 4)
        modloc_layout_row += 1

        modloc_layout.addWidget(QLabel("MIScore threshold:"), modloc_layout_row, 0)
        miscore_threshold = self._create_number_input('toppic', 'miscore-threshold', 0.0, 1.0, 0.15, True)
        modloc_layout.addWidget(miscore_threshold, modloc_layout_row, 1)
        modloc_group.setLayout(modloc_layout)
        advanced_layout.addWidget(modloc_group, row, 0, 1, 4)

        advanced_group.setLayout(advanced_layout)

        main_layout.addWidget(basic_group)
        main_layout.addWidget(advanced_group)
        group.setLayout(main_layout)
        return group

    def _create_number_input(self, group, arg, min_val, max_val, default, double=False):
        if double:
            spinbox = QDoubleSpinBox()
            spinbox.setDecimals(4)
            spinbox.setRange(float(min_val), float(max_val))
            spinbox.setValue(float(default))
            self.args.set_config(group, arg, float(default))
            spinbox.valueChanged.connect(
                lambda text: self.args.set_config(group, arg, float(text))
            )
        else:
            spinbox = QSpinBox()
            spinbox.setRange(int(min_val), int(max_val))
            spinbox.setValue(int(default))
            self.args.set_config(group, arg, int(default))
            spinbox.valueChanged.connect(
                lambda text: self.args.set_config(group, arg, int(text))
            )   
        self.ui[group][arg] = spinbox
        return spinbox

    def _browse_file(self, line_edit, file_type="All Files (*.*)"):
        filename, _ = QFileDialog.getOpenFileName(self, "Select File", "", file_type)
        if filename:
            line_edit.setText(filename) 