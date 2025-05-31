from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, 
                            QLabel, QLineEdit, QComboBox, QCheckBox, 
                            QScrollArea, QPushButton, QSpinBox, QDoubleSpinBox,
                            QFileDialog, QMessageBox, QFrame, QGridLayout)
from PyQt5.QtGui import QFont, QPalette, QColor
from PyQt5.QtCore import Qt
from .Setting import Setting

class InformedProteomicsConfigTab(QWidget):
    def __init__(self, args):
        super().__init__()
        self.args = args
        # 用于保存所有UI控件
        self.ui = {
            'pbfgen': {},
            'promex': {},
            'mspathfinder': {}
        }
        self._init_ui()
    
    def _init_ui(self):

        # 创建主布局
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)  # 增加主要组件之间的间距
        
        # Add reference text with clickable link
        reference_label = QLabel()
        reference_label.setText('<a href="https://github.com/PNNL-Comp-Mass-Spec/Informed-Proteomics" style="color: blue; font-style: italic;">For detailed parameter descriptions, please refer to the official documentation</a>')
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
        
        # PbfGen 配置组
        pbfgen_group = self._create_pbfgen_group()
        pbfgen_group.setStyleSheet("""
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
        scroll_layout.addWidget(pbfgen_group)
        
        # 添加分隔线
        line1 = QFrame()
        line1.setFrameShape(QFrame.HLine)
        line1.setFrameShadow(QFrame.Sunken)
        line1.setStyleSheet("background-color: #4682b4;")
        scroll_layout.addWidget(line1)
        
        # ProMex 配置组
        promex_group = self._create_promex_group()
        promex_group.setStyleSheet("""
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
        scroll_layout.addWidget(promex_group)
        
        # 添加分隔线
        line2 = QFrame()
        line2.setFrameShape(QFrame.HLine)
        line2.setFrameShadow(QFrame.Sunken)
        line2.setStyleSheet("background-color: #db7093;")
        scroll_layout.addWidget(line2)
        
        # MSPathFinder 配置组
        mspathfinder_group = self._create_mspathfinder_group()
        mspathfinder_group.setStyleSheet("""
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
        scroll_layout.addWidget(mspathfinder_group)
        
        scroll_widget.setLayout(scroll_layout)
        scroll.setWidget(scroll_widget)
        main_layout.addWidget(scroll)
        self.setLayout(main_layout)

    def _create_pbfgen_group(self):
        group = QGroupBox("PbfGen Configuration")
        group_layout = QGridLayout()
        group_layout.setHorizontalSpacing(10)
        group_layout.setVerticalSpacing(8)
        row = 0
        
        # 扫描范围设置
        grid1 = QGridLayout()
        grid1.setHorizontalSpacing(10)
        grid1.setVerticalSpacing(8)
        grid1.addWidget(QLabel("Start scan number:"), row, 0)
        start_scan = self._create_number_input("pbfgen", "start_scan", -1, 999999, -1)
        grid1.addWidget(start_scan, row, 1)
        grid1.addWidget(QLabel("End scan number:"), row, 2)
        end_scan = self._create_number_input("pbfgen", "end_scan", -1, 999999, -1)
        grid1.addWidget(end_scan, row, 3)
        group_layout.addLayout(grid1, row, 0, 1, 4)
        row += 1
        
        # 参数文件设置
        grid2 = QGridLayout()
        grid2.setHorizontalSpacing(10)
        grid2.setVerticalSpacing(8)
        grid2.addWidget(QLabel("Parameter file:"), row, 0)
        param_file_edit = QLineEdit()
        param_file_edit.setPlaceholderText("Please select the path of parameter file")
        param_file_edit.textChanged.connect(lambda text: self.args.set_config('pbfgen', 'ParamFile', text))
        browse_btn = QPushButton("Browse")
        browse_btn.clicked.connect(lambda: self._browse_file(param_file_edit))
        grid2.addWidget(param_file_edit, row, 1)
        grid2.addWidget(browse_btn, row, 2)
        self.ui['pbfgen']['ParamFile'] = param_file_edit
        group_layout.addLayout(grid2, row, 0, 1, 4)
        row += 1
        group.setLayout(group_layout)
        return group

    def _create_promex_group(self):
        group = QGroupBox("ProMex Configuration")
        layout = QVBoxLayout()
        grid = QGridLayout()
        grid.setHorizontalSpacing(10)
        grid.setVerticalSpacing(8)
        row = 0
        
        # 电荷态范围
        grid.addWidget(QLabel("Minimum charge:"), row, 0)
        min_charge = self._create_number_input("promex", "MinCharge", 1, 60, 1)
        grid.addWidget(min_charge, row, 1)
        grid.addWidget(QLabel("Maximum charge:"), row, 2)
        max_charge = self._create_number_input("promex", "MaxCharge", 1, 99, 60)
        grid.addWidget(max_charge, row, 3)
        row += 1
        
        # 质量范围
        grid.addWidget(QLabel("Minimum mass (Da):"), row, 0)
        min_mass = self._create_number_input("promex", "MinMass", 600, 100000, 2000)
        grid.addWidget(min_mass, row, 1)
        grid.addWidget(QLabel("Maximum mass (Da):"), row, 2)
        max_mass = self._create_number_input("promex", "MaxMass", 600, 100000, 50000)
        grid.addWidget(max_mass, row, 3)
        row += 1
        
        # 其他参数
        grid.addWidget(QLabel("Score threshold:"), row, 0)
        score_threshold = self._create_number_input("promex", "ScoreThreshold", -100, 100, -10, double=True)
        grid.addWidget(score_threshold, row, 1)
        grid.addWidget(QLabel("Max threads:"), row, 2)
        max_threads = self._create_number_input("promex", "MaxThreads", 0, 32, 0)
        grid.addWidget(max_threads, row, 3)
        row += 1
        
        # BinResPPM下拉框
        grid.addWidget(QLabel("Binning resolution (PPM):"), row, 0)
        bin_res = QComboBox()
        bin_res.addItems(["1", "2", "4", "8", "16", "32", "64", "128"])
        bin_res.setCurrentText("16")
        bin_res.currentTextChanged.connect(lambda text: self.args.set_config('promex', 'BinResPPM', int(text)))
        grid.addWidget(bin_res, row, 1)
        self.ui['promex']['BinResPPM'] = bin_res
        row += 1
        
        # 复选框选项
        bool_layout = QGridLayout()
        bool_items = [
            ("Output feature heatmap", "FeatureMap", True),
            ("Output extended scoring", "Score", True),
            ("Write feature data to CSV", "csv", True)
        ]
        for idx, (label, key, default) in enumerate(bool_items):
            cb = QCheckBox(label)
            cb.setChecked(default)
            self.args.set_config('promex', key, default)
            cb.stateChanged.connect(lambda state, k=key: self.args.set_config('promex', k, bool(state)))
            self.ui['promex'][key] = cb
            bool_layout.addWidget(cb, 0, idx)
        grid.addLayout(bool_layout, row, 0, 1, 4)
        row += 1
        
        # 文件选择
        file_layout = QGridLayout()
        file_layout.setHorizontalSpacing(10)
        file_layout.setVerticalSpacing(8)
        file_layout_row = 0
        file_layout.addWidget(QLabel("MS1FT file:"), file_layout_row, 0)
        ms1ft_edit = QLineEdit()
        ms1ft_edit.setPlaceholderText("Path to MS1FT file")
        ms1ft_edit.textChanged.connect(lambda text: self.args.set_config('promex', 'ms1ft', text))
        browse_ms1ft = QPushButton("Browse")
        browse_ms1ft.clicked.connect(lambda: self._browse_file(ms1ft_edit))
        file_layout.addWidget(ms1ft_edit, file_layout_row, 1)
        file_layout.addWidget(browse_ms1ft, file_layout_row, 2)
        self.ui['promex']['ms1ft'] = ms1ft_edit
        file_layout_row += 1

        file_layout.addWidget(QLabel("Parameter file:"), file_layout_row, 0)
        param_file_edit = QLineEdit()
        param_file_edit.setPlaceholderText("Path to parameter file")
        param_file_edit.textChanged.connect(lambda text: self.args.set_config('promex', 'ParamFile', text))
        browse_param = QPushButton("Browse")
        browse_param.clicked.connect(lambda: self._browse_file(param_file_edit))
        file_layout.addWidget(param_file_edit, file_layout_row, 1)
        file_layout.addWidget(browse_param, file_layout_row, 2)
        self.ui['promex']['ParamFile'] = param_file_edit
        grid.addLayout(file_layout, row, 0, 1, 4)
        row += 1
        
        layout.addLayout(grid)
        group.setLayout(layout)
        return group

    def _create_mspathfinder_group(self):
        group = QGroupBox("MSPathFinder Configuration")
        layout = QVBoxLayout()
        
        # Basic Parameters
        basic_group = QGroupBox("Basic Parameters")
        basic_layout = QGridLayout()
        basic_layout.setHorizontalSpacing(10)
        basic_layout.setVerticalSpacing(8)
        row = 0
        
        # 搜索模式和激活方法
        basic_layout.addWidget(QLabel("Search Mode:"), row, 0)
        search_mode = QComboBox()
        search_mode.addItems(["NoInternalCleavage", "SingleInternalCleavage", "MultipleInternalCleavages"])
        search_mode.setCurrentText("SingleInternalCleavage")
        search_mode.currentTextChanged.connect(lambda text: self.args.set_config('mspathfinder', 'ic', text))
        basic_layout.addWidget(search_mode, row, 1)
        self.ui['mspathfinder']['ic'] = search_mode
        
        basic_layout.addWidget(QLabel("Activation Method:"), row, 2)
        activation = QComboBox()
        activation.addItems(["CID", "ETD", "HCD", "ECD", "PQD", "UVPD", "Unknown"])
        activation.setCurrentText("Unknown")
        activation.currentTextChanged.connect(lambda text: self.args.set_config('mspathfinder', 'ActivationMethod', text))
        basic_layout.addWidget(activation, row, 3)
        self.ui['mspathfinder']['ActivationMethod'] = activation
        row += 1
        
        # 数值参数
        basic_layout.addWidget(QLabel("Memory matches:"), row, 0)
        mem_matches = self._create_number_input("mspathfinder", "MemMatches", 1, 100, 3)
        basic_layout.addWidget(mem_matches, row, 1)
        basic_layout.addWidget(QLabel("Matches per spectrum:"), row, 2)
        num_matches = self._create_number_input("mspathfinder", "NumMatchesPerSpec", 1, 100, 1)
        basic_layout.addWidget(num_matches, row, 3)
        row += 1
        
        # 容差设置
        basic_layout.addWidget(QLabel("Precursor tolerance (PPM):"), row, 0)
        pmt_tolerance = self._create_number_input("mspathfinder", "PMTolerance", 0, 100, 10)
        basic_layout.addWidget(pmt_tolerance, row, 1)
        basic_layout.addWidget(QLabel("Fragment tolerance (PPM):"), row, 2)
        frag_tolerance = self._create_number_input("mspathfinder", "FragTolerance", 0, 100, 10)
        basic_layout.addWidget(frag_tolerance, row, 3)
        row += 1
        
        # 序列长度范围
        basic_layout.addWidget(QLabel("Minimum sequence length:"), row, 0)
        min_length = self._create_number_input("mspathfinder", "MinLength", 0, 1000, 21)
        basic_layout.addWidget(min_length, row, 1)
        basic_layout.addWidget(QLabel("Maximum sequence length:"), row, 2)
        max_length = self._create_number_input("mspathfinder", "MaxLength", 0, 1000, 500)
        basic_layout.addWidget(max_length, row, 3)
        row += 1
        
        # 电荷态范围
        basic_layout.addWidget(QLabel("Minimum charge:"), row, 0)
        min_charge = self._create_number_input("mspathfinder", "MinCharge", 1, 99, 2)
        basic_layout.addWidget(min_charge, row, 1)
        basic_layout.addWidget(QLabel("Maximum charge:"), row, 2)
        max_charge = self._create_number_input("mspathfinder", "MaxCharge", 1, 99, 50)
        basic_layout.addWidget(max_charge, row, 3)
        row += 1
        
        # 碎片电荷态范围
        basic_layout.addWidget(QLabel("Minimum fragment charge:"), row, 0)
        min_frag_charge = self._create_number_input("mspathfinder", "MinFragCharge", 1, 99, 1)
        basic_layout.addWidget(min_frag_charge, row, 1)
        basic_layout.addWidget(QLabel("Maximum fragment charge:"), row, 2)
        max_frag_charge = self._create_number_input("mspathfinder", "MaxFragCharge", 1, 99, 20)
        basic_layout.addWidget(max_frag_charge, row, 3)
        row += 1
        
        # 质量范围和线程数
        basic_layout.addWidget(QLabel("Minimum mass (Da):"), row, 0)
        min_mass = self._create_number_input("mspathfinder", "MinMass", 0, 100000, 3000)
        basic_layout.addWidget(min_mass, row, 1)
        basic_layout.addWidget(QLabel("Maximum mass (Da):"), row, 2)
        max_mass = self._create_number_input("mspathfinder", "MaxMass", 0, 100000, 50000)
        basic_layout.addWidget(max_mass, row, 3)
        row += 1
        
        basic_layout.addWidget(QLabel("Maximum number of threads:"), row, 0)
        thread_count = self._create_number_input("mspathfinder", "ThreadCount", 0, 100, 0)
        basic_layout.addWidget(thread_count, row, 1)
        row += 1
        
        # 复选框选项
        bool_layout = QGridLayout()
        bool_layout.setHorizontalSpacing(10)
        bool_layout.setVerticalSpacing(8)
        bool_items = [
            ("Include Tag-based Search", "TagSearch", True),
            ("Include decoy results", "IncludeDecoys", False),
            ("Use FLIP scoring", "UseFlipScoring", False),
            ("Search decoy database", "tda", False),
            ("Overwrite existing results", "overwrite", False)
        ]
        for idx, (label, key, default) in enumerate(bool_items):
            cb = QCheckBox(label)
            cb.setChecked(default)
            self.args.set_config('mspathfinder', key, default)
            cb.stateChanged.connect(lambda state, k=key: self.args.set_config('mspathfinder', k, bool(state)))
            self.ui['mspathfinder'][key] = cb
            bool_layout.addWidget(cb, idx // 3, idx % 3)
        basic_layout.addLayout(bool_layout, row, 0, 1, 4)
        row += 1
        
        # 文件选择
        file_layout = QGridLayout()
        file_layout.setHorizontalSpacing(10)
        file_layout.setVerticalSpacing(8)
        file_layout_row = 0
        file_layout.addWidget(QLabel("Modification file:"), file_layout_row, 0)
        mod_file_edit = QLineEdit()
        mod_file_edit.setPlaceholderText("Please select the path of modification file")
        mod_file_edit.textChanged.connect(lambda text: self.args.set_config('mspathfinder', 'ModificationFile', text))
        browse_mod = QPushButton("Browse")
        browse_mod.clicked.connect(lambda: self._browse_file(mod_file_edit))
        file_layout.addWidget(mod_file_edit, file_layout_row, 1)
        file_layout.addWidget(browse_mod, file_layout_row, 2)
        self.ui['mspathfinder']['ModificationFile'] = mod_file_edit
        file_layout_row += 1
        
        file_layout.addWidget(QLabel("Feature file:"), file_layout_row, 0)
        feature_file_edit = QLineEdit()
        feature_file_edit.setPlaceholderText("Please select the path of feature file")
        feature_file_edit.textChanged.connect(lambda text: self.args.set_config('mspathfinder', 'FeatureFile', text))
        browse_feature = QPushButton("Browse")
        browse_feature.clicked.connect(lambda: self._browse_file(feature_file_edit))
        file_layout.addWidget(feature_file_edit, file_layout_row, 1)
        file_layout.addWidget(browse_feature, file_layout_row, 2)
        self.ui['mspathfinder']['FeatureFile'] = feature_file_edit
        file_layout_row += 1
        
        file_layout.addWidget(QLabel("Scans file:"), file_layout_row, 0)
        scans_file_edit = QLineEdit()
        scans_file_edit.setPlaceholderText("Please select the path of scans file")
        scans_file_edit.textChanged.connect(lambda text: self.args.set_config('mspathfinder', 'ScansFilePath', text))
        browse_scans = QPushButton("Browse")
        browse_scans.clicked.connect(lambda: self._browse_file(scans_file_edit))
        file_layout.addWidget(scans_file_edit, file_layout_row, 1)
        file_layout.addWidget(browse_scans, file_layout_row, 2)
        self.ui['mspathfinder']['ScansFile'] = scans_file_edit
        file_layout_row += 1
        
        file_layout.addWidget(QLabel("Parameter file:"), file_layout_row, 0)
        param_file_edit = QLineEdit()
        param_file_edit.setPlaceholderText("Please select the path of parameter file")
        param_file_edit.textChanged.connect(lambda text: self.args.set_config('mspathfinder', 'ParamFile', text))
        browse_param = QPushButton("Browse")
        browse_param.clicked.connect(lambda: self._browse_file(param_file_edit))
        file_layout.addWidget(param_file_edit, file_layout_row, 1)
        file_layout.addWidget(browse_param, file_layout_row, 2)
        self.ui['mspathfinder']['ParamFile'] = param_file_edit
        basic_layout.addLayout(file_layout, row, 0, 1, 4)
        row += 1
        
        basic_group.setLayout(basic_layout)
        layout.addWidget(basic_group)
        group.setLayout(layout)
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

    def _save_settings(self):
        """Save current settings to file"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save InformedProteomics Settings", "", "Settings File (*.ini);;All Files (*)"
        )
        
        if not file_path:
            QMessageBox.information(self, "Error", "No save path selected!")
            return
            
        try:
            # Collect current settings from self.ui
            settings = {
                'pbfgen': self._collect_pbfgen_settings(),
                'promex': self._collect_promex_settings(),
                'mspathfinder': self._collect_mspathfinder_settings()
            }
            
            # Use Setting class to save settings
            Setting.save(file_path, settings)
            QMessageBox.information(self, "Success", "Settings saved successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save settings: {str(e)}")
    
    def _collect_pbfgen_settings(self):
        """Collect PbfGen settings"""
        settings = {}
        for key, widget in self.ui['pbfgen'].items():
            if isinstance(widget, QSpinBox) or isinstance(widget, QDoubleSpinBox):
                settings[key] = str(widget.value())
            elif isinstance(widget, QLineEdit):
                settings[key] = widget.text()
            elif isinstance(widget, QComboBox):
                settings[key] = widget.currentText()
            elif isinstance(widget, QCheckBox):
                settings[key] = str(widget.isChecked())
        return settings
    
    def _collect_promex_settings(self):
        """Collect ProMex settings"""
        settings = {}
        for key, widget in self.ui['promex'].items():
            if isinstance(widget, QSpinBox) or isinstance(widget, QDoubleSpinBox):
                settings[key] = str(widget.value())
            elif isinstance(widget, QLineEdit):
                settings[key] = widget.text()
            elif isinstance(widget, QComboBox):
                settings[key] = widget.currentText()
            elif isinstance(widget, QCheckBox):
                settings[key] = str(widget.isChecked())
        return settings
    
    def _collect_mspathfinder_settings(self):
        """Collect MSPathFinder settings"""
        settings = {}
        for key, widget in self.ui['mspathfinder'].items():
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
        """Load settings from file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Load InformedProteomics Settings", "", "Settings File (*.ini);;All Files (*)"
        )
        
        if not file_path:
            QMessageBox.information(self, "Error", "No load path selected!")
            return
            
        try:
            # Create Setting instance to load configuration
            setting_instance = Setting(file_path)
            
            # Update PbfGen settings
            self._update_pbfgen_settings(setting_instance)
            
            # Update ProMex settings
            self._update_promex_settings(setting_instance)
            
            # Update MSPathFinder settings
            self._update_mspathfinder_settings(setting_instance)
            
            QMessageBox.information(self, "Success", "Settings loaded successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load settings: {str(e)}")
    
    def _update_pbfgen_settings(self, setting_instance):
        """从配置更新PbfGen设置"""
        for key, widget in self.ui['pbfgen'].items():
            value = setting_instance.get('pbfgen', key)
            if value:
                if isinstance(widget, QSpinBox):
                    widget.setValue(int(value))
                    self.args.set_config('pbfgen', key, int(value))
                elif isinstance(widget, QDoubleSpinBox):
                    widget.setValue(float(value))
                    self.args.set_config('pbfgen', key, float(value))
                elif isinstance(widget, QLineEdit):
                    widget.setText(value)
                    self.args.set_config('pbfgen', key, value)
                elif isinstance(widget, QComboBox):
                    widget.setCurrentText(value)
                    self.args.set_config('pbfgen', key, value)
                elif isinstance(widget, QCheckBox):
                    widget.setChecked(value.lower() == 'true')
                    self.args.set_config('pbfgen', key, value.lower() == 'true')
            else:
                if isinstance(widget, QLineEdit):
                    widget.setText(value)
                    self.args.set_config('pbfgen', key, value)
    
    def _update_promex_settings(self, setting_instance):
        """从配置更新ProMex设置"""
        for key, widget in self.ui['promex'].items():
            value = setting_instance.get('promex', key)
            if value:
                if isinstance(widget, QSpinBox):
                    widget.setValue(int(value))
                    self.args.set_config('promex', key, int(value))
                elif isinstance(widget, QDoubleSpinBox):
                    widget.setValue(float(value))
                    self.args.set_config('promex', key, float(value))
                elif isinstance(widget, QLineEdit):
                    widget.setText(value)
                    self.args.set_config('promex', key, value)
                elif isinstance(widget, QComboBox):
                    widget.setCurrentText(value)
                    self.args.set_config('promex', key, value)
                elif isinstance(widget, QCheckBox):
                    widget.setChecked(value.lower() == 'true')
                    self.args.set_config('promex', key, value.lower() == 'true')
            else:
                if isinstance(widget, QLineEdit):
                    widget.setText(value)
                    self.args.set_config('promex', key, value)
    
    def _update_mspathfinder_settings(self, setting_instance):
        """从配置更新MSPathFinder设置"""
        for key, widget in self.ui['mspathfinder'].items():
            value = setting_instance.get('mspathfinder', key)
            if value:
                if isinstance(widget, QSpinBox):
                    widget.setValue(int(value))
                    self.args.set_config('mspathfinder', key, int(value))
                elif isinstance(widget, QDoubleSpinBox):
                    widget.setValue(float(value))
                    self.args.set_config('mspathfinder', key, float(value))
                elif isinstance(widget, QLineEdit):
                    widget.setText(value)
                    self.args.set_config('mspathfinder', key, value)
                elif isinstance(widget, QComboBox):
                    widget.setCurrentText(value)
                    self.args.set_config('mspathfinder', key, value)
                elif isinstance(widget, QCheckBox):
                    widget.setChecked(value.lower() == 'true')
                    self.args.set_config('mspathfinder', key, value.lower() == 'true')
                else:
                    if isinstance(widget, QLineEdit):
                        widget.setText(value)
                        self.args.set_config('mspathfinder', key, value)

