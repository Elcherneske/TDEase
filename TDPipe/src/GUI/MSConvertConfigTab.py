from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                            QGroupBox, QLabel, QComboBox, QCheckBox,
                            QPushButton, QFileDialog, QMessageBox, QDoubleSpinBox,
                            QSpinBox, QFormLayout, QLineEdit)
from .Setting import Setting


class MSConvertConfigTab(QWidget):
    def __init__(self, args):
        super().__init__()
        self.args = args
        self.ui = {
            'output_format': None,
            'peak_picking': {},
            'mz_precision': None,
            'intensity_precision': None,
            'scan_summing': {},
            'subset': {}
        }
        self._init_ui()
    
    def _init_ui(self):
        layout = QVBoxLayout()
        
        # 添加保存/加载按钮
        buttons_layout = QHBoxLayout()
        save_button = QPushButton("Save Settings")
        load_button = QPushButton("Load Settings")
        save_button.clicked.connect(self._save_settings)
        load_button.clicked.connect(self._load_settings)
        buttons_layout.addWidget(save_button)
        buttons_layout.addWidget(load_button)
        layout.addLayout(buttons_layout)
        
        # 基本选项分组
        options_group = QGroupBox("MSConvert Basic Options")
        options_layout = QVBoxLayout()
        
        # 添加各种配置选项
        options_layout.addLayout(self._create_output_format_layout())
        options_layout.addLayout(self._create_precision_layout())
        
        options_group.setLayout(options_layout)
        layout.addWidget(options_group)
        
        # 添加Peak Picking分组
        layout.addWidget(self._create_peak_picking_layout())
        
        # 添加Scan Summing功能
        layout.addWidget(self._create_scan_summing_group())
        
        # 添加Subset过滤功能
        layout.addWidget(self._create_subset_group())
        
        layout.addStretch()
        self.setLayout(layout)
    
    def _create_scan_summing_group(self):
        group = QGroupBox("Scan Summing Options")
        group.setCheckable(False)  # 改为不可勾选
        
        layout = QVBoxLayout()
        
        # 添加单独的复选框
        enable_checkbox = QCheckBox("Enable Scan Summing")
        enable_checkbox.setChecked(False)  # 默认不启用
        self.args.set_config('msconvert', 'scan_summing_enabled', False)
        enable_checkbox.stateChanged.connect(
            lambda state: self.args.set_config('msconvert', 'scan_summing_enabled', bool(state))
        )
        layout.addWidget(enable_checkbox)
        self.ui['scan_summing']['enabled'] = enable_checkbox
        
        # Precursor tolerance
        precursor_tol_layout = QHBoxLayout()
        precursor_tol_layout.addWidget(QLabel("Precursor tolerance(m/z):"))
        precursor_tolerance = QDoubleSpinBox()
        precursor_tolerance.setValue(0.05)
        precursor_tolerance.valueChanged.connect(
            lambda value: self.args.set_config('msconvert', 'scan_summing_precursor_tol', value)
        )
        precursor_tol_layout.addWidget(precursor_tolerance)
        layout.addLayout(precursor_tol_layout)
        self.ui['scan_summing']['precursor_tol'] = precursor_tolerance
        
        # Scan time tolerance
        scan_time_tol_layout = QHBoxLayout()
        scan_time_tol_layout.addWidget(QLabel("Scan time tolerance(s):"))
        scan_time_tolerance = QDoubleSpinBox()
        scan_time_tolerance.setValue(5)
        scan_time_tolerance.setDecimals(3)
        scan_time_tolerance.valueChanged.connect(
            lambda value: self.args.set_config('msconvert', 'scan_summing_scan_time_tol', value)
        )
        scan_time_tol_layout.addWidget(scan_time_tolerance)
        layout.addLayout(scan_time_tol_layout)
        self.ui['scan_summing']['scan_time_tol'] = scan_time_tolerance
        
        # Ion mobility tolerance
        ion_mobility_tol_layout = QHBoxLayout()
        ion_mobility_tol_layout.addWidget(QLabel("Ion mobility tolerance(ms or vs/cm^2):"))
        ion_mobility_tolerance = QDoubleSpinBox()
        ion_mobility_tolerance.setValue(5)
        ion_mobility_tolerance.setDecimals(3)
        ion_mobility_tolerance.valueChanged.connect(
            lambda value: self.args.set_config('msconvert', 'scan_summing_ion_mobility_tol', value)
        )
        ion_mobility_tol_layout.addWidget(ion_mobility_tolerance)
        layout.addLayout(ion_mobility_tol_layout)
        self.ui['scan_summing']['ion_mobility_tol'] = ion_mobility_tolerance
        
        # Sum MS1 scans also
        sum_ms1_layout = QHBoxLayout()
        sum_ms1_layout.addWidget(QLabel("Sum MS1 scans also:"))
        sum_ms1_scans = QCheckBox()
        sum_ms1_scans.setChecked(False)
        sum_ms1_scans.stateChanged.connect(
            lambda state: self.args.set_config('msconvert', 'scan_summing_sum_ms1', bool(state))
        )
        sum_ms1_layout.addWidget(sum_ms1_scans)
        layout.addLayout(sum_ms1_layout)
        self.ui['scan_summing']['sum_ms1'] = sum_ms1_scans
        
        group.setLayout(layout)
        return group
    
    def _create_subset_group(self):
        group = QGroupBox("Subset Filter Options")
        group.setCheckable(False)  # 改为不可勾选
        
        layout = QVBoxLayout()
        
        # 添加单独的复选框
        enable_checkbox = QCheckBox("Enable Subset Filter")
        enable_checkbox.setChecked(False)  # 默认不启用
        self.args.set_config('msconvert', 'subset_enabled', False)
        enable_checkbox.stateChanged.connect(
            lambda state: self.args.set_config('msconvert', 'subset_enabled', bool(state))
        )
        layout.addWidget(enable_checkbox)
        self.ui['subset']['enabled'] = enable_checkbox
        
        # MS Level
        ms_level_container = QHBoxLayout()
        ms_level_container.addWidget(QLabel("MS Level:"))
        ms_level_layout = QHBoxLayout()
        ms_level_min = QLineEdit()
        ms_level_min.setPlaceholderText("Minimum")
        ms_level_max = QLineEdit()
        ms_level_max.setPlaceholderText("Maximum")
        ms_level_layout.addWidget(ms_level_min)
        ms_level_layout.addWidget(QLabel("-"))
        ms_level_layout.addWidget(ms_level_max)
        ms_level_container.addLayout(ms_level_layout)
        
        ms_level_min.textChanged.connect(
            lambda text: self.args.set_config('msconvert', 'subset_ms_level_min', text)
        )
        ms_level_max.textChanged.connect(
            lambda text: self.args.set_config('msconvert', 'subset_ms_level_max', text)
        )
        layout.addLayout(ms_level_container)
        self.ui['subset']['ms_level_min'] = ms_level_min
        self.ui['subset']['ms_level_max'] = ms_level_max
        
        # Scan Number
        scan_number_container = QHBoxLayout()
        scan_number_container.addWidget(QLabel("Scan Number:"))
        scan_number_layout = QHBoxLayout()
        scan_number_min = QLineEdit()
        scan_number_min.setPlaceholderText("Minimum")
        scan_number_max = QLineEdit()
        scan_number_max.setPlaceholderText("Maximum")
        scan_number_layout.addWidget(scan_number_min)
        scan_number_layout.addWidget(QLabel("-"))
        scan_number_layout.addWidget(scan_number_max)
        scan_number_container.addLayout(scan_number_layout)
        
        scan_number_min.textChanged.connect(
            lambda text: self.args.set_config('msconvert', 'subset_scan_number_min', text)
        )
        scan_number_max.textChanged.connect(
            lambda text: self.args.set_config('msconvert', 'subset_scan_number_max', text)
        )
        layout.addLayout(scan_number_container)
        self.ui['subset']['scan_number_min'] = scan_number_min
        self.ui['subset']['scan_number_max'] = scan_number_max
        
        # Scan Time
        scan_time_container = QHBoxLayout()
        scan_time_container.addWidget(QLabel("Scan Time (min):"))
        scan_time_layout = QHBoxLayout()
        scan_time_min = QLineEdit()
        scan_time_min.setPlaceholderText("Minimum")
        scan_time_max = QLineEdit()
        scan_time_max.setPlaceholderText("Maximum")
        scan_time_layout.addWidget(scan_time_min)
        scan_time_layout.addWidget(QLabel("-"))
        scan_time_layout.addWidget(scan_time_max)
        scan_time_container.addLayout(scan_time_layout)
                
        scan_time_min.textChanged.connect(
            lambda text: self.args.set_config('msconvert', 'subset_scan_time_min', text)
        )
        scan_time_max.textChanged.connect(
            lambda text: self.args.set_config('msconvert', 'subset_scan_time_max', text)
        )
        layout.addLayout(scan_time_container)
        self.ui['subset']['scan_time_min'] = scan_time_min
        self.ui['subset']['scan_time_max'] = scan_time_max
        
        # Scan Events
        scan_events_container = QHBoxLayout()
        scan_events_container.addWidget(QLabel("Scan Events:"))
        scan_events_layout = QHBoxLayout()
        scan_events_min = QLineEdit()
        scan_events_min.setPlaceholderText("Minimum")
        scan_events_max = QLineEdit()
        scan_events_max.setPlaceholderText("Maximum")
        scan_events_layout.addWidget(scan_events_min)
        scan_events_layout.addWidget(QLabel("-"))
        scan_events_layout.addWidget(scan_events_max)
        scan_events_container.addLayout(scan_events_layout)
        
        scan_events_min.textChanged.connect(
            lambda text: self.args.set_config('msconvert', 'subset_scan_events_min', text)
        )
        scan_events_max.textChanged.connect(
            lambda text: self.args.set_config('msconvert', 'subset_scan_events_max', text)
        )
        layout.addLayout(scan_events_container)
        self.ui['subset']['scan_events_min'] = scan_events_min
        self.ui['subset']['scan_events_max'] = scan_events_max
        
        # Charge States
        charge_states_container = QHBoxLayout()
        charge_states_container.addWidget(QLabel("Charge States:"))
        charge_states_layout = QHBoxLayout()
        charge_states_min = QLineEdit()
        charge_states_min.setPlaceholderText("Minimum")
        charge_states_max = QLineEdit()
        charge_states_max.setPlaceholderText("Maximum")
        charge_states_layout.addWidget(charge_states_min)
        charge_states_layout.addWidget(QLabel("-"))
        charge_states_layout.addWidget(charge_states_max)
        charge_states_container.addLayout(charge_states_layout)

        charge_states_min.textChanged.connect(
            lambda text: self.args.set_config('msconvert', 'subset_charge_states_min', text)
        )
        charge_states_max.textChanged.connect(
            lambda text: self.args.set_config('msconvert', 'subset_charge_states_max', text)
        )
        layout.addLayout(charge_states_container)
        self.ui['subset']['charge_states_min'] = charge_states_min
        self.ui['subset']['charge_states_max'] = charge_states_max
        
        # Number of Data Points
        data_points_container = QHBoxLayout()
        data_points_container.addWidget(QLabel("Number of Data Points:"))
        data_points_layout = QHBoxLayout()
        data_points_min = QLineEdit()
        data_points_min.setPlaceholderText("Minimum")
        data_points_max = QLineEdit()
        data_points_max.setPlaceholderText("Maximum")
        data_points_layout.addWidget(data_points_min)
        data_points_layout.addWidget(QLabel("-"))
        data_points_layout.addWidget(data_points_max)
        data_points_container.addLayout(data_points_layout)
        
        data_points_min.textChanged.connect(
            lambda text: self.args.set_config('msconvert', 'subset_data_points_min', text)
        )
        data_points_max.textChanged.connect(
            lambda text: self.args.set_config('msconvert', 'subset_data_points_max', text)
        )
        layout.addLayout(data_points_container)
        self.ui['subset']['data_points_min'] = data_points_min
        self.ui['subset']['data_points_max'] = data_points_max
        
        # Collision Energy
        collision_energy_container = QHBoxLayout()
        collision_energy_container.addWidget(QLabel("Collision Energy:"))
        collision_energy_layout = QHBoxLayout()
        collision_energy_min = QLineEdit()
        collision_energy_min.setPlaceholderText("Minimum")
        collision_energy_max = QLineEdit()
        collision_energy_max.setPlaceholderText("Maximum")
        collision_energy_layout.addWidget(collision_energy_min)
        collision_energy_layout.addWidget(QLabel("-"))
        collision_energy_layout.addWidget(collision_energy_max)
        collision_energy_container.addLayout(collision_energy_layout)
        
        collision_energy_min.textChanged.connect(
            lambda text: self.args.set_config('msconvert', 'subset_collision_energy_min', text)
        )
        collision_energy_max.textChanged.connect(
            lambda text: self.args.set_config('msconvert', 'subset_collision_energy_max', text)
        )
        layout.addLayout(collision_energy_container)
        self.ui['subset']['collision_energy_min'] = collision_energy_min
        self.ui['subset']['collision_energy_max'] = collision_energy_max
        
        # Scan Polarity
        scan_polarity_layout = QHBoxLayout()
        scan_polarity_layout.addWidget(QLabel("Scan Polarity:"))
        scan_polarity = QComboBox()
        scan_polarity.addItems(["Any", "Positive", "Negative"])
        scan_polarity.setCurrentText("Any")
        scan_polarity.currentTextChanged.connect(
            lambda text: self.args.set_config('msconvert', 'subset_scan_polarity', text)
        )
        scan_polarity_layout.addWidget(scan_polarity)
        layout.addLayout(scan_polarity_layout)
        self.ui['subset']['scan_polarity'] = scan_polarity
        
        # Activation Type
        activation_type_layout = QHBoxLayout()
        activation_type_layout.addWidget(QLabel("Activation Type:"))
        activation_type = QComboBox()
        activation_type.addItems(["Any", "BIRD", "CID", "ECD", "ETD", "ETD+SA", "HCD", "IRMPD", "PD", "PQD", "PSD", "SID", "SORI", "UVPD"])
        activation_type.setCurrentText("Any")
        activation_type.currentTextChanged.connect(
            lambda text: self.args.set_config('msconvert', 'subset_activation_type', text)
        )
        activation_type_layout.addWidget(activation_type)
        layout.addLayout(activation_type_layout)
        self.ui['subset']['activation_type'] = activation_type
        
        # Analysis Type
        analysis_type_layout = QHBoxLayout()
        analysis_type_layout.addWidget(QLabel("Analysis Type:"))
        analysis_type = QComboBox()
        analysis_type.addItems(["Any", "FT", "IT", "orbi", "quad", "TOF"])
        analysis_type.setCurrentText("Any")
        analysis_type.currentTextChanged.connect(
            lambda text: self.args.set_config('msconvert', 'subset_analysis_type', text)
        )
        analysis_type_layout.addWidget(analysis_type)
        layout.addLayout(analysis_type_layout)
        self.ui['subset']['analysis_type'] = analysis_type
        
        group.setLayout(layout)
        return group
    
    def _create_output_format_layout(self):
        layout = QHBoxLayout()
        output_combo = QComboBox()
        output_combo.addItems(["mzML", "mzXML", "mgf", "ms1", "ms2"])
        self.args.set_config('msconvert', 'output_format', 'mzML')
        output_combo.currentTextChanged.connect(
            lambda text: self.args.set_config('msconvert', 'output_format', text)
        )
        layout.addWidget(QLabel("Output Format:"))
        layout.addWidget(output_combo)
        self.ui['output_format'] = output_combo
        return layout
    
    def _create_peak_picking_layout(self):
        group = QGroupBox("Peak Picking Options")
        group.setCheckable(False)  # 改为不可勾选
        
        layout = QVBoxLayout()
        
        # 添加单独的复选框
        enable_checkbox = QCheckBox("Enable Peak Picking")
        enable_checkbox.setChecked(True)  # 默认启用
        self.args.set_config('msconvert', 'peak_picking_enabled', True)  # 默认值设为True
        
        enable_checkbox.stateChanged.connect(
            lambda state: self.args.set_config('msconvert', 'peak_picking_enabled', bool(state))
        )
        layout.addWidget(enable_checkbox)
        self.ui['peak_picking']['enabled'] = enable_checkbox
        
        # 算法选择
        algorithm_layout = QHBoxLayout()
        algorithm_layout.addWidget(QLabel("Algorithm:"))
        algorithm_combo = QComboBox()
        algorithm_combo.addItems(["vendor", "cwt"])
        algorithm_combo.setCurrentText("vendor")
        self.args.set_config('msconvert', 'peak_picking_algorithm', 'vendor')
        algorithm_combo.currentTextChanged.connect(
            lambda text: self.args.set_config('msconvert', 'peak_picking_algorithm', text)
        )
        algorithm_layout.addWidget(algorithm_combo)
        layout.addLayout(algorithm_layout)
        self.ui['peak_picking']['algorithm'] = algorithm_combo
        
        # MS Level range
        ms_level_layout = QHBoxLayout()
        ms_level_layout.addWidget(QLabel("MS Level range:"))
        ms_level_min = QLineEdit()
        ms_level_min.setPlaceholderText("Minimum")
        ms_level_min.setText("1")  # 默认值为1
        ms_level_max = QLineEdit()
        ms_level_max.setPlaceholderText("Maximum")
        ms_level_layout.addWidget(ms_level_min)
        ms_level_layout.addWidget(QLabel("-"))
        ms_level_layout.addWidget(ms_level_max)
                
        ms_level_min.textChanged.connect(
            lambda text: self.args.set_config('msconvert', 'peak_picking_ms_level_min', text)
        )
        ms_level_max.textChanged.connect(
            lambda text: self.args.set_config('msconvert', 'peak_picking_ms_level_max', text)
        )
        layout.addLayout(ms_level_layout)
        self.ui['peak_picking']['ms_level_min'] = ms_level_min
        self.ui['peak_picking']['ms_level_max'] = ms_level_max
        
        # Min SNR
        min_snr_layout = QHBoxLayout()
        min_snr_layout.addWidget(QLabel("Min SNR:"))
        min_snr_spin = QDoubleSpinBox()
        min_snr_spin.setValue(0.1)
        min_snr_spin.setDecimals(2)
        self.args.set_config('msconvert', 'peak_picking_min_snr', 0.1)
        min_snr_spin.valueChanged.connect(
            lambda value: self.args.set_config('msconvert', 'peak_picking_min_snr', value)
        )
        min_snr_layout.addWidget(min_snr_spin)
        layout.addLayout(min_snr_layout)
        self.ui['peak_picking']['min_snr'] = min_snr_spin
        
        # Min Peak Spacing
        peak_spacing_layout = QHBoxLayout()
        peak_spacing_layout.addWidget(QLabel("Min Peak Spacing:"))
        peak_spacing_spin = QDoubleSpinBox()
        peak_spacing_spin.setValue(0.1)
        peak_spacing_spin.setDecimals(2)
        self.args.set_config('msconvert', 'peak_picking_peak_spacing', 0.1)
        peak_spacing_spin.valueChanged.connect(
            lambda value: self.args.set_config('msconvert', 'peak_picking_peak_spacing', value)
        )
        peak_spacing_layout.addWidget(peak_spacing_spin)
        layout.addLayout(peak_spacing_layout)
        self.ui['peak_picking']['peak_spacing'] = peak_spacing_spin
        
        group.setLayout(layout)
        return group

    def _create_precision_layout(self):
        layout = QHBoxLayout()
        
        # mz precision setting
        mz_combo = QComboBox()
        mz_combo.addItems(["32", "64"])
        self.args.set_config('msconvert', 'mz_precision', '32')
        mz_combo.currentTextChanged.connect(
            lambda text: self.args.set_config('msconvert', 'mz_precision', text)
        )
        layout.addWidget(QLabel("m/z Precision:"))
        layout.addWidget(mz_combo)
        self.ui['mz_precision'] = mz_combo
        
        # intensity precision setting 
        intensity_combo = QComboBox()
        intensity_combo.addItems(["32", "64"])
        self.args.set_config('msconvert', 'intensity_precision', '32')
        intensity_combo.currentTextChanged.connect(
            lambda text: self.args.set_config('msconvert', 'intensity_precision', text)
        )
        layout.addWidget(QLabel("Intensity Precision:"))
        layout.addWidget(intensity_combo)
        self.ui['intensity_precision'] = intensity_combo
        
        return layout

    def _save_settings(self):
        """Save current MSConvert settings to file"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save MSConvert Settings", "", "Settings File (*.ini);;All Files (*)"
        )
        
        if not file_path:
            QMessageBox.information(self, "Error", "No save path selected!")
            return
        
        try:
            # Collect current settings from self.ui
            settings = {
                'msconvert': {
                    'output_format': self.ui['output_format'].currentText(),
                    'mz_precision': self.ui['mz_precision'].currentText(),
                    'intensity_precision': self.ui['intensity_precision'].currentText()
                },
                'msconvert_peak_picking': self._collect_peak_picking_settings(),
                'msconvert_scan_summing': self._collect_scan_summing_settings(),
                'msconvert_subset': self._collect_subset_settings()
            }
            
            # Use Setting class to save settings
            Setting.save(file_path, settings)
            QMessageBox.information(self, "Success", "Settings saved successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save settings: {str(e)}")
    
    def _collect_scan_summing_settings(self):
        """Collect scan summing settings"""
        settings = {}
        for key, widget in self.ui['scan_summing'].items():
            if isinstance(widget, QDoubleSpinBox):
                settings[key] = str(widget.value())
            elif isinstance(widget, QCheckBox):
                settings[key] = str(widget.isChecked())
        return settings
    
    def _collect_subset_settings(self):
        """Collect subset settings"""
        settings = {}
        for key, widget in self.ui['subset'].items():
            if isinstance(widget, QLineEdit):
                settings[key] = widget.text()
            elif isinstance(widget, QComboBox):
                settings[key] = widget.currentText()
            elif isinstance(widget, QCheckBox):
                settings[key] = str(widget.isChecked())
        return settings
    
    def _collect_peak_picking_settings(self):
        """Collect peak picking settings"""
        settings = {}
        for key, widget in self.ui['peak_picking'].items():
            if isinstance(widget, QDoubleSpinBox):
                settings[key] = str(widget.value())
            elif isinstance(widget, QLineEdit):
                settings[key] = widget.text()
            elif isinstance(widget, QComboBox):
                settings[key] = widget.currentText()
            elif isinstance(widget, QCheckBox):
                settings[key] = str(widget.isChecked())
        return settings
    
    def _load_settings(self):
        """Load MSConvert settings from file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Load MSConvert Settings", "", "Settings File (*.ini);;All Files (*)"
        )
        
        if not file_path:
            QMessageBox.information(self, "Error", "No load path selected!")
            return
            
        try:
            # Create Setting instance to load configuration
            setting_instance = Setting(file_path)
            
            # Update UI components and args
            output_format = setting_instance.get('msconvert', 'output_format')
            if output_format:
                self.ui['output_format'].setCurrentText(output_format)
                self.args.set_config('msconvert', 'output_format', output_format)
            
            mz_precision = setting_instance.get('msconvert', 'mz_precision')
            if mz_precision:
                self.ui['mz_precision'].setCurrentText(mz_precision)
                self.args.set_config('msconvert', 'mz_precision', mz_precision)
            
            intensity_precision = setting_instance.get('msconvert', 'intensity_precision')
            if intensity_precision:
                self.ui['intensity_precision'].setCurrentText(intensity_precision)
                self.args.set_config('msconvert', 'intensity_precision', intensity_precision)
            
            # Update peak picking settings
            self._update_peak_picking_settings(setting_instance)
            
            # Update scan summing settings
            self._update_scan_summing_settings(setting_instance)
            
            # Update subset settings
            self._update_subset_settings(setting_instance)
            
            QMessageBox.information(self, "Success", "Settings loaded successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load settings: {str(e)}")
    
    def _update_scan_summing_settings(self, setting_instance):
        """Update scan summing settings"""
        # Update whether enabled
        enabled = setting_instance.get('msconvert_scan_summing', 'enabled')
        if enabled and 'enabled' in self.ui['scan_summing']:
            scan_summing_enabled = enabled.lower() == 'true'
            self.ui['scan_summing']['enabled'].setChecked(scan_summing_enabled)
            self.args.set_config('msconvert', 'scan_summing_enabled', scan_summing_enabled)
        
        # Use loop to handle other settings
        for key, widget in self.ui['scan_summing'].items():
            if key == 'enabled':
                continue
                
            setting_value = setting_instance.get('msconvert_scan_summing', key)
            if key in self.ui['scan_summing']:
                if setting_value:
                    if isinstance(widget, QDoubleSpinBox):
                        widget.setValue(float(setting_value))
                        self.args.set_config('msconvert', f'scan_summing_{key}', float(setting_value))
                    elif isinstance(widget, QCheckBox):
                        widget.setChecked(setting_value.lower() == 'true')
                        self.args.set_config('msconvert', f'scan_summing_{key}', setting_value.lower() == 'true')
                else:
                    if isinstance(widget, QLineEdit):
                        widget.setText(setting_value)
                        self.args.set_config('msconvert', f'scan_summing_{key}', setting_value)
    
    def _update_subset_settings(self, setting_instance):
        """Update subset settings"""
        # Update whether enabled
        enabled = setting_instance.get('msconvert_subset', 'enabled')
        if enabled and 'enabled' in self.ui['subset']:
            subset_enabled = enabled.lower() == 'true'
            self.ui['subset']['enabled'].setChecked(subset_enabled)
            self.args.set_config('msconvert', 'subset_enabled', subset_enabled)
        
        # Use loop to handle other settings
        for key, widget in self.ui['subset'].items():
            if key == 'enabled':
                continue
                
            setting_value = setting_instance.get('msconvert_subset', key)
            if key in self.ui['subset']:
                if setting_value:
                    if isinstance(widget, QLineEdit):
                        widget.setText(setting_value)
                        self.args.set_config('msconvert', f'subset_{key}', setting_value)
                    elif isinstance(widget, QComboBox):
                        widget.setCurrentText(setting_value)
                        self.args.set_config('msconvert', f'subset_{key}', setting_value)
                else:
                    if isinstance(widget, QLineEdit):
                        widget.setText(setting_value)
                        self.args.set_config('msconvert', f'subset_{key}', setting_value)

    def _update_peak_picking_settings(self, setting_instance):
        """Update peak picking settings"""
        # Update checkbox state
        enabled = setting_instance.get('msconvert_peak_picking', 'enabled')
        if enabled and 'enabled' in self.ui['peak_picking']:
            peak_picking_enabled = enabled.lower() == 'true'
            self.ui['peak_picking']['enabled'].setChecked(peak_picking_enabled)
            self.args.set_config('msconvert', 'peak_picking_enabled', peak_picking_enabled)
        
        # Use loop to handle other settings
        for key, widget in self.ui['peak_picking'].items():
            if key == 'enabled':
                continue
                
            setting_value = setting_instance.get('msconvert_peak_picking', key)
            if key in self.ui['peak_picking']:
                if setting_value:
                    if isinstance(widget, QComboBox):
                        widget.setCurrentText(setting_value)
                        self.args.set_config('msconvert', f'peak_picking_{key}', setting_value)
                    elif isinstance(widget, QLineEdit):
                        widget.setText(setting_value)
                        self.args.set_config('msconvert', f'peak_picking_{key}', setting_value)
                    elif isinstance(widget, QDoubleSpinBox):
                        widget.setValue(float(setting_value))
                        self.args.set_config('msconvert', f'peak_picking_{key}', float(setting_value))
                else:
                    if isinstance(widget, QLineEdit):
                        widget.setText(setting_value)
                        self.args.set_config('msconvert', f'peak_picking_{key}', setting_value)

