from .BaseWorkflow import BaseWorkflow

class ToppicSuitWorkflow(BaseWorkflow):
    def __init__(self, args):
        super().__init__()
        self.args = args
        self.input_files = args.get_ms_file_path()
        self.fasta_file = args.get_fasta_path()
        self.output_dir = args.get_output_dir()

    def prepare_workflow(self):
        self.commands = []
        command = self._msconvert_command(self.input_files)
        if command:
            self.commands.append(command)

        mzml_files = []
        for input_file in self.input_files:
            mzml_files.append(f"{self.output_dir}/{input_file.split('/')[-1].rsplit('.', 1)[0]}.mzML")
            
        command = self._topfd_command(mzml_files)
        if command:
            self.commands.append(command)

        msalign_files = []
        for mzml_file in mzml_files:
            msalign_files.append(f"{self.output_dir}/{mzml_file.split('/')[-1].rsplit('.', 1)[0]}_ms2.msalign")

        command = self._toppic_command(msalign_files)
        if command:
            self.commands.append(command)
    
    def _msconvert_command(self, input_files):
        if not self.args.tool_paths['msconvert']:
            self.log("MSConvert path is empty, please check the configuration.")
            return None
        
        msconvert_command = [self.args.tool_paths['msconvert']]

        msconvert_command.append('--zlib')
        
        if self.args.get_msconvert_config_option('output_format') == "mzML":
            msconvert_command.append('--mzML')
        elif self.args.get_msconvert_config_option('output_format') == "mzXML":
            msconvert_command.append('--mzXML')
        elif self.args.get_msconvert_config_option('output_format') == "mgf":
            msconvert_command.append('--mgf')
        elif self.args.get_msconvert_config_option('output_format') == "ms1":
            msconvert_command.append('--ms1')
        elif self.args.get_msconvert_config_option('output_format') == "ms2":
            msconvert_command.append('--ms2')
        elif self.args.get_msconvert_config_option('output_format') == "cms1":
            msconvert_command.append('--cms1')
        elif self.args.get_msconvert_config_option('output_format') == "cms2":
            msconvert_command.append('--cms2')
        else:
            msconvert_command.append('--mzML')
        
        if self.args.get_msconvert_config_option('mz_precision') == "64":
            msconvert_command.append('--mz64')
        elif self.args.get_msconvert_config_option('mz_precision') == "32":
            msconvert_command.append('--mz32')
        else:
            msconvert_command.append('--mz32')
        
        if self.args.get_msconvert_config_option('intensity_precision') == "64":
            msconvert_command.append('--inten64')
        elif self.args.get_msconvert_config_option('intensity_precision') == "32":
            msconvert_command.append('--inten32')
        else:
            msconvert_command.append('--inten32')

        if self.args.output_dir:
            msconvert_command.append('-o')
            msconvert_command.append(self.args.output_dir)

        # 处理peakPicking
        if self.args.get_msconvert_config_option('peak_picking_enabled'):
            msconvert_command.append('--filter')
            
            # 构建peakPicking过滤器
            if self.args.get_msconvert_config_option('peak_picking_algorithm'):
                algorithm = self.args.get_msconvert_config_option('peak_picking_algorithm')
            else:
                algorithm = 'vendor'

            if self.args.get_msconvert_config_option('peak_picking_ms_level_min'):
                ms_level_min = self.args.get_msconvert_config_option('peak_picking_ms_level_min')
            else:
                ms_level_min = '1'

            if self.args.get_msconvert_config_option('peak_picking_ms_level_max'):
                ms_level_max = self.args.get_msconvert_config_option('peak_picking_ms_level_max')
            else:
                ms_level_max = '1000000'
            
            peak_picking_filter = f'"peakPicking {algorithm} msLevel={ms_level_min}-{ms_level_max}'
            
            # 如果是cwt算法，添加特有参数
            if algorithm == 'cwt':
                min_snr = self.args.get_msconvert_config_option('peak_picking_min_snr')
                if min_snr is not None:
                    peak_picking_filter += f" snr={min_snr}"
                
                peak_spacing = self.args.get_msconvert_config_option('peak_picking_peak_spacing')
                if peak_spacing is not None:
                    peak_picking_filter += f" peakSpace={peak_spacing}"
            
            peak_picking_filter += '"'
            msconvert_command.append(peak_picking_filter)

        # 添加scan summing过滤器
        if self.args.get_msconvert_config_option('scan_summing_enabled'):
            msconvert_command.append('--filter')
            
            scan_summing_filter = '"scanSumming '
            
            # 添加precursor tolerance参数
            if self.args.get_msconvert_config_option('scan_summing_precursor_tol'):
                scan_summing_filter += f"precursorTol={self.args.get_msconvert_config_option('scan_summing_precursor_tol')} "
            
            # 添加scan time tolerance参数
            if self.args.get_msconvert_config_option('scan_summing_scan_time_tol'):
                scan_summing_filter += f"scanTimeTol={self.args.get_msconvert_config_option('scan_summing_scan_time_tol')} "
            
            # 添加ion mobility tolerance参数
            if self.args.get_msconvert_config_option('scan_summing_ion_mobility_tol'):
                scan_summing_filter += f"ionMobilityTol={self.args.get_msconvert_config_option('scan_summing_ion_mobility_tol')} "
            
            # 添加sum MS1 scans参数
            if self.args.get_msconvert_config_option('scan_summing_sum_ms1'):
                scan_summing_filter += "sumMs1=1 "
            else:
                scan_summing_filter += "sumMs1=0 "
            
            scan_summing_filter = scan_summing_filter.strip() + '"'
            msconvert_command.append(scan_summing_filter)

        # 添加subset过滤器
        if self.args.get_msconvert_config_option('subset_enabled'):

            # 添加MS Level参数
            if self.args.get_msconvert_config_option('subset_ms_level_min') or self.args.get_msconvert_config_option('subset_ms_level_max'):
                msconvert_command.append('--filter')
                filter_name = 'msLevel '
                if self.args.get_msconvert_config_option('subset_ms_level_min'):
                    filter_name += f"{self.args.get_msconvert_config_option('subset_ms_level_min')}"
                filter_name += '-'
                if self.args.get_msconvert_config_option('subset_ms_level_max'):
                    filter_name += f"{self.args.get_msconvert_config_option('subset_ms_level_max')}"
                filter_name = f'"{filter_name}"'
                msconvert_command.append(filter_name)

            # 添加Scan Number参数
            if self.args.get_msconvert_config_option('subset_scan_number_min') or self.args.get_msconvert_config_option('subset_scan_number_max'):
                msconvert_command.append('--filter')
                filter_name = 'scanNumber '
                if self.args.get_msconvert_config_option('subset_scan_number_min'):
                    filter_name += f"{self.args.get_msconvert_config_option('subset_scan_number_min')}"
                filter_name += '-'
                if self.args.get_msconvert_config_option('subset_scan_number_max'):
                    filter_name += f"{self.args.get_msconvert_config_option('subset_scan_number_max')}"
                filter_name = f'"{filter_name}"'
                msconvert_command.append(filter_name)

            # 添加Scan Time参数
            if self.args.get_msconvert_config_option('subset_scan_time_min') or self.args.get_msconvert_config_option('subset_scan_time_max'):
                msconvert_command.append('--filter')
                filter_name = 'scanTime '
                if self.args.get_msconvert_config_option('subset_scan_time_min'):
                    filter_name += f"[{self.args.get_msconvert_config_option('subset_scan_time_min')}"
                else:
                    filter_name += '[0'
                filter_name += ','
                if self.args.get_msconvert_config_option('subset_scan_time_max'):
                    filter_name += f"{self.args.get_msconvert_config_option('subset_scan_time_max')}]"
                else:
                    filter_name += '1e8]'
                filter_name = f'"{filter_name}"'
                msconvert_command.append(filter_name)

            # 添加Scan Events参数
            if self.args.get_msconvert_config_option('subset_scan_events_min') or self.args.get_msconvert_config_option('subset_scan_events_max'):
                msconvert_command.append('--filter')
                filter_name = 'scanEvent '
                if self.args.get_msconvert_config_option('subset_scan_events_min'):
                    filter_name += f"{self.args.get_msconvert_config_option('subset_scan_events_min')}"
                filter_name += '-'
                if self.args.get_msconvert_config_option('subset_scan_events_max'):
                    filter_name += f"{self.args.get_msconvert_config_option('subset_scan_events_max')}"
                filter_name = f'"{filter_name}"'
                msconvert_command.append(filter_name)

            # 添加Charge States参数
            if self.args.get_msconvert_config_option('subset_charge_states_min') or self.args.get_msconvert_config_option('subset_charge_states_max'):
                msconvert_command.append('--filter')
                filter_name = 'chargeState '
                if self.args.get_msconvert_config_option('subset_charge_states_min'):
                    filter_name += f"{self.args.get_msconvert_config_option('subset_charge_states_min')}"
                filter_name += '-'
                if self.args.get_msconvert_config_option('subset_charge_states_max'):
                    filter_name += f"{self.args.get_msconvert_config_option('subset_charge_states_max')}"
                filter_name = f'"{filter_name}"'
                msconvert_command.append(filter_name)

            # 添加Number of Data Points参数
            if self.args.get_msconvert_config_option('subset_data_points_min') or self.args.get_msconvert_config_option('subset_data_points_max'):
                msconvert_command.append('--filter')
                filter_name = 'defaultArrayLength '
                if self.args.get_msconvert_config_option('subset_data_points_min'):
                    filter_name += f"{self.args.get_msconvert_config_option('subset_data_points_min')}"
                filter_name += '-'
                if self.args.get_msconvert_config_option('subset_data_points_max'):
                    filter_name += f"{self.args.get_msconvert_config_option('subset_data_points_max')}"
                filter_name = f'"{filter_name}"'
                msconvert_command.append(filter_name)

            # 添加Collision Energy参数
            if self.args.get_msconvert_config_option('subset_collision_energy_min') and self.args.get_msconvert_config_option('subset_collision_energy_max'):
                msconvert_command.append('--filter')
                filter_name = 'collisionEnergy '
                filter_name += f"low={self.args.get_msconvert_config_option('subset_collision_energy_min')}"
                filter_name += f" high={self.args.get_msconvert_config_option('subset_collision_energy_max')}"
                filter_name += f" acceptNonCID=True acceptMissingCE=False"
                filter_name = f'"{filter_name}"'
                msconvert_command.append(filter_name)
            
            # 添加Scan Polarity参数
            if self.args.get_msconvert_config_option('subset_scan_polarity') and self.args.get_msconvert_config_option('subset_scan_polarity') != "Any":
                msconvert_command.append('--filter')
                filter_name = f"polarity {self.args.get_msconvert_config_option('subset_scan_polarity')} "
                msconvert_command.append(filter_name)

            # 添加Activation Type参数
            if self.args.get_msconvert_config_option('subset_activation_type') and self.args.get_msconvert_config_option('subset_activation_type') != "Any":
                msconvert_command.append('--filter')
                filter_name = f"activationType {self.args.get_msconvert_config_option('subset_activation_type')} "
                msconvert_command.append(filter_name)
            
            # 添加Analysis Type参数
            if self.args.get_msconvert_config_option('subset_analysis_type') and self.args.get_msconvert_config_option('subset_analysis_type') != "Any":
                analysis_type = self.args.get_msconvert_config_option('subset_analysis_type')
                msconvert_command.append('--filter')
                filter_name = f"analyzerType {analysis_type} "
                msconvert_command.append(filter_name)

        msconvert_command.append('--filter')
        msconvert_command.append('"titleMaker <RunId>.<ScanNumber>.<ScanNumber>.<ChargeState> File:"""^<SourcePath^>""", NativeID:"""^<Id^>""""')

        for input_file in input_files:
            msconvert_command.append(input_file)

        return msconvert_command
    
    def _topfd_command(self, input_files):
        if not self.args.tool_paths['topfd']:
            self.log("TopFD path is empty, please check the configuration.")
            return None
        
        topfd_command = [self.args.tool_paths['topfd']]
        if self.args.get_topfd_config_option('activation'):
            topfd_command.append('--activation')
            topfd_command.append(self.args.get_topfd_config_option('activation'))
        
        if self.args.get_topfd_config_option('max_charge'):
            topfd_command.append('--max-charge')
            topfd_command.append(str(self.args.get_topfd_config_option('max_charge')))
        
        if self.args.get_topfd_config_option('max_mass'):
            topfd_command.append('--max-mass')
            topfd_command.append(str(self.args.get_topfd_config_option('max_mass')))
        
        if self.args.get_topfd_config_option('mz_error'):
            topfd_command.append('--mz-error')
            topfd_command.append(str(self.args.get_topfd_config_option('mz_error')))
        
        if self.args.get_topfd_config_option('ms1_sn'):
            topfd_command.append('--ms-one-sn-ratio')
            topfd_command.append(str(self.args.get_topfd_config_option('ms1_sn')))
        
        if self.args.get_topfd_config_option('ms2_sn'):
            topfd_command.append('--ms-two-sn-ratio')
            topfd_command.append(str(self.args.get_topfd_config_option('ms2_sn')))
        
        if self.args.get_topfd_config_option('precursor_window'):
            topfd_command.append('--precursor-window')
            topfd_command.append(str(self.args.get_topfd_config_option('precursor_window')))
        
        if self.args.get_topfd_config_option('ecscore_cutoff'):
            topfd_command.append('--ecscore-cutoff')
            topfd_command.append(str(self.args.get_topfd_config_option('ecscore_cutoff')))
        
        if self.args.get_topfd_config_option('min_scan_number'):
            topfd_command.append('--min-scan-number')
            topfd_command.append(str(self.args.get_topfd_config_option('min_scan_number')))
        
        if self.args.get_topfd_config_option('thread_number'):
            topfd_command.append('--thread-number')
            topfd_command.append(str(self.args.get_topfd_config_option('thread_number')))
        
        if self.args.get_topfd_config_option('skip_html_folder'):
            topfd_command.append('--skip-html-folder')
        
        if self.args.get_topfd_config_option('disable_additional_feature_search'):
            topfd_command.append('--disable-additional-feature-search')
        
        if self.args.get_topfd_config_option('disable_final_filtering'):
            topfd_command.append('--disable-final-filtering')

        for input_file in input_files:
            topfd_command.append(input_file)

        return topfd_command

    def _toppic_command(self, input_files):
        if not self.args.tool_paths['toppic']:
            self.log("TopPIC路径为空，请检查配置。")
            return None
        
        toppic_command = [self.args.tool_paths['toppic']]

        if self.args.get_toppic_config_option('activation'):
            toppic_command.append('--activation')
            toppic_command.append(self.args.get_toppic_config_option('activation'))
        
        if self.args.get_toppic_config_option('fixed_mod'):
            toppic_command.append('--fixed-mod')
            toppic_command.append(self.args.get_toppic_config_option('fixed_mod'))

        if self.args.get_toppic_config_option('n_terminal_form'):
            toppic_command.append('--n-terminal-form')
            toppic_command.append(self.args.get_toppic_config_option('n_terminal_form'))

        if self.args.get_toppic_config_option('num_shift'):
            toppic_command.append('--num-shift')
            toppic_command.append(str(self.args.get_toppic_config_option('num_shift')))

        if self.args.get_toppic_config_option('min_shift'):
            toppic_command.append('--min-shift')
            toppic_command.append(str(self.args.get_toppic_config_option('min_shift')))

        if self.args.get_toppic_config_option('max_shift'):
            toppic_command.append('--max-shift')
            toppic_command.append(str(self.args.get_toppic_config_option('max_shift')))

        if self.args.get_toppic_config_option('variable_ptm_num'):
            toppic_command.append('--variable-ptm-num')
            toppic_command.append(str(self.args.get_toppic_config_option('variable_ptm_num')))

        if self.args.get_toppic_config_option('variable_ptm_file_name'):
            toppic_command.append('--variable-ptm-file-name')
            toppic_command.append(self.args.get_toppic_config_option('variable_ptm_file_name'))

        if self.args.get_toppic_config_option('decoy'):
            toppic_command.append('--decoy')

        if self.args.get_toppic_config_option('mass_error_tolerance'):
            toppic_command.append('--mass-error-tolerance')
            toppic_command.append(str(self.args.get_toppic_config_option('mass_error_tolerance')))

        if self.args.get_toppic_config_option('proteoform_error_tolerance'):
            toppic_command.append('--proteoform-error-tolerance')
            toppic_command.append(str(self.args.get_toppic_config_option('proteoform_error_tolerance')))

        if self.args.get_toppic_config_option('spectrum_cutoff_type'):
            toppic_command.append('--spectrum-cutoff-type')
            toppic_command.append(self.args.get_toppic_config_option('spectrum_cutoff_type'))
        
        if self.args.get_toppic_config_option('spectrum_cutoff_value'):
            toppic_command.append('--spectrum-cutoff-value')
            toppic_command.append(str(self.args.get_toppic_config_option('spectrum_cutoff_value')))

        if self.args.get_toppic_config_option('proteoform_cutoff_type'):
            toppic_command.append('--proteoform-cutoff-type')
            toppic_command.append(self.args.get_toppic_config_option('proteoform_cutoff_type'))

        if self.args.get_toppic_config_option('proteoform_cutoff_value'):
            toppic_command.append('--proteoform-cutoff-value')
            toppic_command.append(str(self.args.get_toppic_config_option('proteoform_cutoff_value')))

        if self.args.get_toppic_config_option('approximate_spectra'):
            toppic_command.append('--approximate-spectra')

        if self.args.get_toppic_config_option('lookup_table'):
            toppic_command.append('--lookup-table')

        if self.args.get_toppic_config_option('local_ptm_file_name'):
            toppic_command.append('--local-ptm-file-name')
            toppic_command.append(self.args.get_toppic_config_option('local_ptm_file_name'))

        if self.args.get_toppic_config_option('miscore_threshold'):
            toppic_command.append('--miscore-threshold')
            toppic_command.append(str(self.args.get_toppic_config_option('miscore_threshold')))

        if self.args.get_toppic_config_option('thread_number'):
            toppic_command.append('--thread-number')
            toppic_command.append(str(self.args.get_toppic_config_option('thread_number')))

        if self.args.get_toppic_config_option('num_combined_spectra'):
            toppic_command.append('--num-combined-spectra')
            toppic_command.append(str(self.args.get_toppic_config_option('num_combined_spectra')))

        if self.args.get_toppic_config_option('combined_file_name'):
            toppic_command.append('--combined-file-name')
            toppic_command.append(self.args.get_toppic_config_option('combined_file_name'))

        if self.args.get_toppic_config_option('no_topfd_feature'):
            toppic_command.append('--no-topfd-feature')

        if self.args.get_toppic_config_option('keep_temp_files'):
            toppic_command.append('--keep-temp-files')

        if self.args.get_toppic_config_option('keep_decoy_ids'):
            toppic_command.append('--keep-decoy-ids')

        if self.args.get_toppic_config_option('skip_html_folder'):
            toppic_command.append('--skip-html-folder')
        
        toppic_command.append(self.fasta_file)

        for file in input_files:
            toppic_command.append(file)
        return toppic_command


if __name__ == '__main__':
    pass

