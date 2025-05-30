class Args:
    def __init__(self):
        
        self.workflow = None
        self.msfile = []
        self.fasta_path = None
        self.output_dir = None

        self.args = {
            'tools': {   # 存储各种工具的路径
                'msconvert': None,
                'toppic': None,
                'topfd': None,
                'topmg': None,
                'topdiff': None,
                'pbfgen': None,
                'promex': None,
                'mspathfinder': None,
                'python': None,  # 添加Python路径
            },
            'msconvert': {
                'output_format': None,
                'mz_precision': None,
                'intensity_precision': None,
                'peak_picking_enabled': None,
                'peak_picking_algorithm': None,
                'peak_picking_ms_level_min': None,
                'peak_picking_ms_level_max': None,
                'peak_picking_min_snr': None,
                'peak_picking_peak_spacing': None,
                'scan_summing_enabled': None,
                'scan_summing_precursor_tol': None,
                'scan_summing_scan_time_tol': None,
                'scan_summing_ion_mobility_tol': None,
                'scan_summing_sum_ms1': None,
                'subset_enabled': None,
                'subset_ms_level_min': None,
                'subset_ms_level_max': None,
                'subset_scan_number_min': None,
                'subset_scan_number_max': None,
                'subset_scan_time_min': None,
                'subset_scan_time_max': None,
                'subset_scan_events_min': None,
                'subset_scan_events_max': None,
                'subset_charge_states_min': None,
                'subset_charge_states_max': None,
                'subset_data_points_min': None,
                'subset_data_points_max': None,
                'subset_collision_energy_min': None,
                'subset_collision_energy_max': None,
                'subset_scan_polarity': None,
                'subset_activation_type': None,
                'subset_analysis_type': None,
            },
            'toppic': {
                'activation': None,
                'fixed-mod': None,
                'fixed-mod-file': None,
                'variable-ptm-file-name': None,
                'n-terminal-form': None,
                'num-shift': None,
                'min-shift': None,
                'max-shift': None,
                'variable-ptm-num': None,
                'decoy': None,
                'mass-error-tolerance': None,
                'proteoform-error-tolerance': None,
                'spectrum-cutoff-type': None,
                'spectrum-cutoff-value': None,
                'proteoform-cutoff-type': None,
                'proteoform-cutoff-value': None,
                'thread-number': None,
                'num-combined-spectra': None,
                'approximate-spectra': None,
                'lookup-table': None,
                'local-ptm-file-name': None,
                'miscore-threshold': None,
                'keep-temp-files': None,
                'keep-decoy-ids': None,
                'skip-html-folder': None,
                'no-topfd-feature': None,
                'combined-file-name': None
            },
            'topfd': {
                'activation': None,
                'max-charge': None,
                'max-mass': None,
                'mz-error': None,
                'ms-one-sn-ratio': None,
                'ms-two-sn-ratio': None,
                'missing-level-one': None,
                'msdeconv': None,
                'precursor-window': None,
                'ecscore-cutoff': None,
                'min-scan-number': None,
                'single-scan-noise': None,
                'disable-additional-feature-search': None,
                'disable-final-filtering': None,
                'thread-number': None,
                'skip-html-folder': None
            },
            'topmg': {
                'activation': None,   
                'fixed-mod': None,   
                'n-terminal-form': None,   
                'decoy': None,   
                'mass-error-tolerance': None,   
                'proteoform-error-tolerance': None,   
                'max-shift': None,   
                'spectrum-cutoff-type': None,   
                'spectrum-cutoff-value': None,   
                'proteoform-cutoff-type': None,   
                'proteoform-cutoff-value': None,   
                'mod-file-name': None,   
                'thread-number': None,   
                'no-topfd-feature': None,   
                'proteo-graph-gap': None,   
                'var-ptm-in-gap': None,   
                'use-asf-diagonal': None,   
                'var-ptm': None,   
                'num-shift': None,   
                'whole-protein-only': None,   
                'combined-file-name': None,   
                'keep-temp-files': None,   
                'keep-decoy-ids': None,   
                'skip-html-folder': None,
            },
            'pbfgen': {
                'start': None,
                'end': None,
                'ParamFile': None
            },
            'promex': {
                'MinCharge': None,  
                'MaxCharge': None, 
                'MinMass': None, 
                'MaxMass': None, 
                'FeatureMap': None, 
                'Score': None,  
                'MaxThreads': None,  
                'csv': None,  
                'BinResPPM': None,  
                'ScoreThreshold': None,  
                'ms1ft': None,  
                'ParamFile': None  
            },
            'mspathfinder': {
                'ic': None,  
                'TagSearch': None,  
                'MemMatches': None,  
                'NumMatchesPerSpec': None,  
                'IncludeDecoys': None,  
                'ModificationFile': None,  
                'tda': None,  
                'overwrite': None,  
                'PMTolerance': None,  
                'FragTolerance': None,  
                'MinLength': None,  
                'MaxLength': None,  
                'MinCharge': None,  
                'MaxCharge': None,  
                'MinFragCharge': None,  
                'MaxFragCharge': None,  
                'MinMass': None,  
                'MaxMass': None,  
                'FeatureFile': None,  
                'ThreadCount': None,  
                'ActivationMethod': None,  
                'ScansFilePath': None,  
                'UseFlipScoring': None,  
                'ParamFile': None  
            },
            'spectrum_sum': {
                'tool':None,
                'method': None,
                'block_size': None,
                'start_scan': None,
                'end_scan': None,
                'ms_level': None,
                'precursor_mz': None,
                'precursor_rt': None,
            }

        }

        # self.mode = None
        # self.ms_file_path = []
        # self.fasta_path = None
        # self.output_dir = None
        
        # self.tool_paths = {   # 存储各种工具的路径
        #     'msconvert': None,
        #     'toppic': None,
        #     'topfd': None,
        #     'topmg': None,
        #     'topdiff': None,
        #     'pbfgen': None,
        #     'promex': None,
        #     'mspathfinder': None,
        #     'python': None,  # 添加Python路径
        # }
        
        # self.msconvert_config_options = {
        #     'output_format': None,
        #     'mz_precision': None,
        #     'intensity_precision': None,
        #     'peak_picking_enabled': None,
        #     'peak_picking_algorithm': None,
        #     'peak_picking_ms_level_min': None,
        #     'peak_picking_ms_level_max': None,
        #     'peak_picking_min_snr': None,
        #     'peak_picking_peak_spacing': None,
        #     'scan_summing_enabled': None,
        #     'scan_summing_precursor_tol': None,
        #     'scan_summing_scan_time_tol': None,
        #     'scan_summing_ion_mobility_tol': None,
        #     'scan_summing_sum_ms1': None,
        #     'subset_enabled': None,
        #     'subset_ms_level_min': None,
        #     'subset_ms_level_max': None,
        #     'subset_scan_number_min': None,
        #     'subset_scan_number_max': None,
        #     'subset_scan_time_min': None,
        #     'subset_scan_time_max': None,
        #     'subset_scan_events_min': None,
        #     'subset_scan_events_max': None,
        #     'subset_charge_states_min': None,
        #     'subset_charge_states_max': None,
        #     'subset_data_points_min': None,
        #     'subset_data_points_max': None,
        #     'subset_collision_energy_min': None,
        #     'subset_collision_energy_max': None,
        #     'subset_scan_polarity': None,
        #     'subset_activation_type': None,
        #     'subset_analysis_type': None,
        # }
        
        # self.topfd_config_options = {
        #     'activation': None,
        #     'ms1_sn': None,
        #     'ms2_sn': None,
        #     'max_charge': None,
        #     'max_mass': None,
        #     'mz_error': None,
        #     'precursor_window': None,
        #     'ecscore_cutoff': None,
        #     'min_scan_number': None,
        #     'thread_number': None,
        #     'skip_html_folder': None,
        #     'disable_additional_feature_search': None,
        #     'disable_final_filtering': None
        # }

        # self.topmg_config_options = {
        #     'activation': None,   
        #     'fixed-mod': None,   
        #     'n-terminal-form': None,   
        #     'decoy': None,   
        #     'mass-error-tolerance': None,   
        #     'proteoform-error-tolerance': None,   
        #     'max-shift': None,   
        #     'spectrum-cutoff-type': None,   
        #     'spectrum-cutoff-value': None,   
        #     'proteoform-cutoff-type': None,   
        #     'proteoform-cutoff-value': None,   
        #     'mod-file-name': None,   
        #     'thread-number': None,   
        #     'no-topfd-feature': None,   
        #     'proteo-graph-gap': None,   
        #     'var-ptm-in-gap': None,   
        #     'use-asf-diagonal': None,   
        #     'var-ptm': None,   
        #     'num-shift': None,   
        #     'whole-protein-only': None,   
        #     'combined-file-name': None,   
        #     'keep-temp-files': None,   
        #     'keep-decoy-ids': None,   
        #     'skip-html-folder': None,
        # }

        # self.toppic_config_options = {
        #     'activation': None,
        #     'fixed_mod': None,
        #     'fixed_mod_file': None,
        #     'variable_ptm_file': None,
        #     'n_terminal_forms': None,
        #     'num_shift': None,
        #     'min_shift': None,
        #     'max_shift': None,
        #     'variable_ptm_num': None,
        #     'variable_ptm_file_name': None,
        #     'decoy': None,
        #     'mass_error_tolerance': None,
        #     'proteoform_error_tolerance': None,
        #     'spectrum_cutoff_type': None,
        #     'spectrum_cutoff_value': None,
        #     'proteoform_cutoff_type': None,
        #     'proteoform_cutoff_value': None,
        #     'thread_number': None,
        #     'num_combined_spectra': None,
        #     'approximate_spectra': None,
        #     'lookup_table': None,
        #     'local_ptm_file_name': None,
        #     'miscore_threshold': None,
        #     'keep_temp_files': None,
        #     'keep_decoy_ids': None,
        #     'skip_html_folder': None,
        #     'no_topfd_feature': None,
        #     'combined_file_name': None
        # }

        # self.pbfgen_config_options = {
        #     'start': None,  
        #     'end': None,    
        #     'ParamFile': None
        # }
        
        # self.promex_config_options = {
        #     'MinCharge': None,  
        #     'MaxCharge': None, 
        #     'MinMass': None, 
        #     'MaxMass': None, 
        #     'FeatureMap': None, 
        #     'Score': None,  
        #     'MaxThreads': None,  
        #     'csv': None,  
        #     'BinResPPM': None,  
        #     'ScoreThreshold': None,  
        #     'ms1ft': None,  
        #     'ParamFile': None  
        # }

        # self.mspathfinder_config_options = {
        #     'ic': None,  
        #     'TagSearch': None,  
        #     'MemMatches': None,  
        #     'NumMatchesPerSpec': None,  
        #     'IncludeDecoys': None,  
        #     'ModificationFile': None,  
        #     'tda': None,  
        #     'overwrite': None,  
        #     'PMTolerance': None,  
        #     'FragTolerance': None,  
        #     'MinLength': None,  
        #     'MaxLength': None,  
        #     'MinCharge': None,  
        #     'MaxCharge': None,  
        #     'MinFragCharge': None,  
        #     'MaxFragCharge': None,  
        #     'MinMass': None,  
        #     'MaxMass': None,  
        #     'FeatureFile': None,  
        #     'ThreadCount': None,  
        #     'ActivationMethod': None,  
        #     'ScansFilePath': None,  
        #     'UseFlipScoring': None,  
        #     'ParamFile': None  
        # }

        # self.spectrum_sum_config_options = {
        #     'tool':None,
        #     'method': None,
        #     'block_size': None,
        #     'start_scan': None,
        #     'end_scan': None,
        #     'ms_level': None,
        #     'precursor_mz': None,
        #     'precursor_rt': None,
        # }
    
    def set_config(self, section, key, value):
        if section == 'workflow':
            self.workflow = value
        elif section == 'msfile':
            self.msfile = value
        elif section == 'fasta':
            self.fasta_path = value
        elif section == 'output':
            self.output_dir = value
        else:
            self.args[section][key] = value
    
    def get_config(self, section, key, default=None):
        if section == 'workflow':
            return self.workflow
        elif section == 'msfile':
            return self.msfile
        elif section == 'fasta':
            return self.fasta_path
        elif section == 'output':
            return self.output_dir
        else:
            if section in self.args and key in self.args[section]:
                return self.args[section][key]
            else:
                return default
            
    def add_msfile(self, path):
        self.msfile.append(path)
    
    def clear_msfile(self):
        self.msfile = []
    
    # def set_ms_file_path(self, text):
    #     filenames = text.split(';')
    #     self.clear_ms_file_path()
    #     for filename in filenames:
    #         self.add_ms_file_path(filename)
    
    # def set_fasta_path(self, path):
    #     self.fasta_path = path
    
    # def get_fasta_path(self):
    #     return self.fasta_path
    
    # def set_output_dir(self, path):
    #     self.output_dir = path
    
    # def get_output_dir(self):
    #     return self.output_dir  
    
    # def set_general_config_option(self, key, value):
    #     self.general_config_options[key] = value
    
    # def get_general_config_option(self, key):
    #     return self.general_config_options.get(key, None)

    # def set_msconvert_config_option(self, key, value):
    #     self.msconvert_config_options[key] = value
    
    # def get_msconvert_config_option(self, key):
    #     return self.msconvert_config_options.get(key, None) 
    
    # def set_toppic_config_option(self, key, value):
    #     self.toppic_config_options[key] = value
    
    # def get_toppic_config_option(self, key):
    #     return self.toppic_config_options.get(key, None)   

    # def set_topfd_config_option(self, key, value):
    #     self.topfd_config_options[key] = value
    
    # def get_topfd_config_option(self, key):
    #     return self.topfd_config_options.get(key, None)

    # def set_topmg_config_option(self, key, value):
    #     self.topmg_config_options[key] = value
    
    # def get_topmg_config_option(self, key):
    #     return self.topmg_config_options.get(key, None)
    
    # def set_pbfgen_config_option(self, key, value):
    #     self.pbfgen_config_options[key] = value
    
    # def get_pbfgen_config_option(self, key):
    #     return self.pbfgen_config_options.get(key, None)
    
    # def set_promex_config_option(self, key, value):
    #     self.promex_config_options[key] = value
    
    # def get_promex_config_option(self, key):
    #     return self.promex_config_options.get(key, None)
    
    # def set_mspathfinder_config_option(self, key, value):
    #     self.mspathfinder_config_options[key] = value
    
    # def get_mspathfinder_config_option(self, key):
    #     return self.mspathfinder_config_options.get(key, None)

    # def set_spectrum_sum_config_option(self, key, value):
    #     self.spectrum_sum_config_options[key] = value

    # def get_spectrum_sum_config_option(self, key):
    #     return self.spectrum_sum_config_options.get(key, None)