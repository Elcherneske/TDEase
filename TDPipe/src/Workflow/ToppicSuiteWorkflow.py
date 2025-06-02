from .BaseWorkflow import BaseWorkflow

class ToppicSuitWorkflow(BaseWorkflow):
    def __init__(self, args):
        super().__init__()
        self.args = args
        self.input_files = args.get_config('msfile', None)
        self.fasta_file = args.get_config('fasta', None)
        self.output_dir = args.get_config('output', None)

    def prepare_workflow(self):
        self.commands = []
        self.check_fns = []
        self.gap_nums = []

        # msconvert
        command = self._msconvert_command(self.input_files)
        if command:
            self.commands.append(command)
            self.check_fns.append(None)
            self.gap_nums.append(0)

        mzml_files = []
        for input_file in self.input_files:
            mzml_files.append(f"{self.output_dir}/{input_file.split('/')[-1].rsplit('.', 1)[0]}.mzML")
            
        command = self._topfd_command(mzml_files)
        if command:
            self.commands.append(command)
            self.check_fns.append(
                lambda text: 
                    ("Processing MS1 spectrum scan" in text and "%" in text) or
                    ("Processing feature" in text and "%" in text) or
                    ("Additional feature search MS1 spectrum scan" in text and "%" in text) or
                    ("Processing MS/MS spectrum scan" in text and "%" in text)
            )
            self.gap_nums.append(500)

        msalign_files = []
        for mzml_file in mzml_files:
            msalign_files.append(f"{self.output_dir}/{mzml_file.split('/')[-1].rsplit('.', 1)[0]}_ms2.msalign")

        command = self._toppic_command(msalign_files)
        if command:
            self.commands.append(command)
            self.check_fns.append(
                lambda text: 
                    ("unexpected shift filtering - processing" in text and "%" in text) or
                    ("unexpected shift search - processing" in text)
            )
            self.gap_nums.append(20000)

    def _msconvert_command(self, input_files: list[str]):
        if not self.args.get_config('tools', 'msconvert'):
            self.log("MSConvert path is empty, please check the configuration.")
            return None
        
        msconvert_command = [self.args.get_config('tools', 'msconvert')]

        msconvert_command.append('--zlib')
        
        if self.args.get_config('msconvert', 'output_format') == "mzML":
            msconvert_command.append('--mzML')
        elif self.args.get_config('msconvert', 'output_format') == "mzXML":
            msconvert_command.append('--mzXML')
        elif self.args.get_config('msconvert', 'output_format') == "mgf":
            msconvert_command.append('--mgf')
        elif self.args.get_config('msconvert', 'output_format') == "ms1":
            msconvert_command.append('--ms1')
        elif self.args.get_config('msconvert', 'output_format') == "ms2":
            msconvert_command.append('--ms2')
        elif self.args.get_config('msconvert', 'output_format') == "cms1":
            msconvert_command.append('--cms1')
        elif self.args.get_config('msconvert', 'output_format') == "cms2":
            msconvert_command.append('--cms2')
        else:
            msconvert_command.append('--mzML')
        
        if self.args.get_config('msconvert', 'mz_precision') == "64":
            msconvert_command.append('--mz64')
        elif self.args.get_config('msconvert', 'mz_precision') == "32":
            msconvert_command.append('--mz32')
        else:
            msconvert_command.append('--mz32')
        
        if self.args.get_config('msconvert', 'intensity_precision') == "64":
            msconvert_command.append('--inten64')
        elif self.args.get_config('msconvert', 'intensity_precision') == "32":
            msconvert_command.append('--inten32')
        else:
            msconvert_command.append('--inten32')

        if self.args.output_dir:
            msconvert_command.append('-o')
            msconvert_command.append(self.args.output_dir)

        # 处理peakPicking
        if self.args.get_config('msconvert', 'peak_picking_enabled'):
            msconvert_command.append('--filter')
            
            # 构建peakPicking过滤器
            if self.args.get_config('msconvert', 'peak_picking_algorithm'):
                algorithm = self.args.get_config('msconvert', 'peak_picking_algorithm')
            else:
                algorithm = 'vendor'

            if self.args.get_config('msconvert', 'peak_picking_ms_level_min'):
                ms_level_min = self.args.get_config('msconvert', 'peak_picking_ms_level_min')
            else:
                ms_level_min = '1'

            if self.args.get_config('msconvert', 'peak_picking_ms_level_max'):
                ms_level_max = self.args.get_config('msconvert', 'peak_picking_ms_level_max')
            else:
                ms_level_max = '1000000'
            
            peak_picking_filter = f'"peakPicking {algorithm} msLevel={ms_level_min}-{ms_level_max}'
            
            # 如果是cwt算法，添加特有参数
            if algorithm == 'cwt':
                min_snr = self.args.get_config('msconvert', 'peak_picking_min_snr')
                if min_snr is not None:
                    peak_picking_filter += f" snr={min_snr}"
                
                peak_spacing = self.args.get_config('msconvert', 'peak_picking_peak_spacing')
                if peak_spacing is not None:
                    peak_picking_filter += f" peakSpace={peak_spacing}"
            
            peak_picking_filter += '"'
            msconvert_command.append(peak_picking_filter)

        # 添加scan summing过滤器
        if self.args.get_config('msconvert', 'scan_summing_enabled'):
            msconvert_command.append('--filter')
            
            scan_summing_filter = '"scanSumming '
            
            # 添加precursor tolerance参数
            if self.args.get_config('msconvert', 'scan_summing_precursor_tol'):
                scan_summing_filter += f"precursorTol={self.args.get_config('msconvert', 'scan_summing_precursor_tol')} "
            
            # 添加scan time tolerance参数
            if self.args.get_config('msconvert', 'scan_summing_scan_time_tol'):
                scan_summing_filter += f"scanTimeTol={self.args.get_config('msconvert', 'scan_summing_scan_time_tol')} "
            
            # 添加ion mobility tolerance参数
            if self.args.get_config('msconvert', 'scan_summing_ion_mobility_tol'):
                scan_summing_filter += f"ionMobilityTol={self.args.get_config('msconvert', 'scan_summing_ion_mobility_tol')} "
            
            # 添加sum MS1 scans参数
            if self.args.get_config('msconvert', 'scan_summing_sum_ms1'):
                scan_summing_filter += "sumMs1=1 "
            else:
                scan_summing_filter += "sumMs1=0 "
            
            scan_summing_filter = scan_summing_filter.strip() + '"'
            msconvert_command.append(scan_summing_filter)

        # 添加subset过滤器
        if self.args.get_config('msconvert', 'subset_enabled'):

            # 添加MS Level参数
            if self.args.get_config('msconvert', 'subset_ms_level_min') or self.args.get_config('msconvert', 'subset_ms_level_max'):
                msconvert_command.append('--filter')
                filter_name = 'msLevel '
                if self.args.get_config('msconvert', 'subset_ms_level_min'):
                    filter_name += f"{self.args.get_config('msconvert', 'subset_ms_level_min')}"
                filter_name += '-'
                if self.args.get_config('msconvert', 'subset_ms_level_max'):
                    filter_name += f"{self.args.get_config('msconvert', 'subset_ms_level_max')}"
                filter_name = f'"{filter_name}"'
                msconvert_command.append(filter_name)

            # 添加Scan Number参数
            if self.args.get_config('msconvert', 'subset_scan_number_min') or self.args.get_config('msconvert', 'subset_scan_number_max'):
                msconvert_command.append('--filter')
                filter_name = 'scanNumber '
                if self.args.get_config('msconvert', 'subset_scan_number_min'):
                    filter_name += f"{self.args.get_config('msconvert', 'subset_scan_number_min')}"
                filter_name += '-'
                if self.args.get_config('msconvert', 'subset_scan_number_max'):
                    filter_name += f"{self.args.get_config('msconvert', 'subset_scan_number_max')}"
                filter_name = f'"{filter_name}"'
                msconvert_command.append(filter_name)

            # 添加Scan Time参数
            if self.args.get_config('msconvert', 'subset_scan_time_min') or self.args.get_config('msconvert', 'subset_scan_time_max'):
                msconvert_command.append('--filter')
                filter_name = 'scanTime '
                if self.args.get_config('msconvert', 'subset_scan_time_min'):
                    filter_name += f"[{self.args.get_config('msconvert', 'subset_scan_time_min')}"
                else:
                    filter_name += '[0'
                filter_name += ','
                if self.args.get_config('msconvert', 'subset_scan_time_max'):
                    filter_name += f"{self.args.get_config('msconvert', 'subset_scan_time_max')}]"
                else:
                    filter_name += '1e8]'
                filter_name = f'"{filter_name}"'
                msconvert_command.append(filter_name)

            # 添加Scan Events参数
            if self.args.get_config('msconvert', 'subset_scan_events_min') or self.args.get_config('msconvert', 'subset_scan_events_max'):
                msconvert_command.append('--filter')
                filter_name = 'scanEvent '
                if self.args.get_config('msconvert', 'subset_scan_events_min'):
                    filter_name += f"{self.args.get_config('msconvert', 'subset_scan_events_min')}"
                filter_name += '-'
                if self.args.get_config('msconvert', 'subset_scan_events_max'):
                    filter_name += f"{self.args.get_config('msconvert', 'subset_scan_events_max')}"
                filter_name = f'"{filter_name}"'
                msconvert_command.append(filter_name)

            # 添加Charge States参数
            if self.args.get_config('msconvert', 'subset_charge_states_min') or self.args.get_config('msconvert', 'subset_charge_states_max'):
                msconvert_command.append('--filter')
                filter_name = 'chargeState '
                if self.args.get_config('msconvert', 'subset_charge_states_min'):
                    filter_name += f"{self.args.get_config('msconvert', 'subset_charge_states_min')}"
                filter_name += '-'
                if self.args.get_config('msconvert', 'subset_charge_states_max'):
                    filter_name += f"{self.args.get_config('msconvert', 'subset_charge_states_max')}"
                filter_name = f'"{filter_name}"'
                msconvert_command.append(filter_name)

            # 添加Number of Data Points参数
            if self.args.get_config('msconvert', 'subset_data_points_min') or self.args.get_config('msconvert', 'subset_data_points_max'):
                msconvert_command.append('--filter')
                filter_name = 'defaultArrayLength '
                if self.args.get_config('msconvert', 'subset_data_points_min'):
                    filter_name += f"{self.args.get_config('msconvert', 'subset_data_points_min')}"
                filter_name += '-'
                if self.args.get_config('msconvert', 'subset_data_points_max'):
                    filter_name += f"{self.args.get_config('msconvert', 'subset_data_points_max')}"
                filter_name = f'"{filter_name}"'
                msconvert_command.append(filter_name)

            # 添加Collision Energy参数
            if self.args.get_config('msconvert', 'subset_collision_energy_min') and self.args.get_config('msconvert', 'subset_collision_energy_max'):
                msconvert_command.append('--filter')
                filter_name = 'collisionEnergy '
                filter_name += f"low={self.args.get_config('msconvert', 'subset_collision_energy_min')}"
                filter_name += f" high={self.args.get_config('msconvert', 'subset_collision_energy_max')}"
                filter_name += f" acceptNonCID=True acceptMissingCE=False"
                filter_name = f'"{filter_name}"'
                msconvert_command.append(filter_name)
            
            # 添加Scan Polarity参数
            if self.args.get_config('msconvert', 'subset_scan_polarity') and self.args.get_config('msconvert', 'subset_scan_polarity') != "Any":
                msconvert_command.append('--filter')
                filter_name = f"polarity {self.args.get_config('msconvert', 'subset_scan_polarity')} "
                msconvert_command.append(filter_name)

            # 添加Activation Type参数
            if self.args.get_config('msconvert', 'subset_activation_type') and self.args.get_config('msconvert', 'subset_activation_type') != "Any":
                msconvert_command.append('--filter')
                filter_name = f"activationType {self.args.get_config('msconvert', 'subset_activation_type')} "
                msconvert_command.append(filter_name)
            
            # 添加Analysis Type参数
            if self.args.get_config('msconvert', 'subset_analysis_type') and self.args.get_config('msconvert', 'subset_analysis_type') != "Any":
                analysis_type = self.args.get_config('msconvert', 'subset_analysis_type')
                msconvert_command.append('--filter')
                filter_name = f"analyzerType {analysis_type} "
                msconvert_command.append(filter_name)

        msconvert_command.append('--filter')
        msconvert_command.append('"titleMaker <RunId>.<ScanNumber>.<ScanNumber>.<ChargeState> File:"""^<SourcePath^>""", NativeID:"""^<Id^>""""')

        for input_file in input_files:
            msconvert_command.append(input_file)

        return msconvert_command
    
    def _topfd_command(self, input_files: list[str]):
        if not self.args.get_config('tools', 'topfd'):
            self.log("TopFD path is empty, please check the configuration.")
            return None
        
        topfd_command = [self.args.get_config('tools', 'topfd')]
        
        # Add all command line options based on configuration
        options = {
            'activation': ('--activation', str),
            'max-charge': ('--max-charge', str),
            'max-mass': ('--max-mass', str),
            'mz-error': ('--mz-error', str),
            'ms-one-sn-ratio': ('--ms-one-sn-ratio', str),
            'ms-two-sn-ratio': ('--ms-two-sn-ratio', str),
            'precursor-window': ('--precursor-window', str),
            'ecscore-cutoff': ('--ecscore-cutoff', str),
            'min-scan-number': ('--min-scan-number', str),
            'thread-number': ('--thread-number', str)
        }
        
        # Add options with values
        for key, (flag, converter) in options.items():
            value = self.args.get_config('topfd', key)
            if value:
                topfd_command.extend([flag, converter(value)])
        
        # Add boolean flags
        bool_flags = {
            'missing-level-one': '--missing-level-one',
            'msdeconv': '--msdeconv',
            'single-scan-noise': '--single-scan-noise',
            'disable-additional-feature-search': '--disable-additional-feature-search',
            'disable-final-filtering': '--disable-final-filtering',
            'skip-html-folder': '--skip-html-folder'
        }
        
        for key, flag in bool_flags.items():
            if self.args.get_config('topfd', key):
                topfd_command.append(flag)
        
        # Add input files
        for input_file in input_files:
            topfd_command.append(input_file)

        return topfd_command

    def _toppic_command(self, input_files: list[str]):
        if not self.args.get_config('tools', 'toppic'):
            self.log("TopPIC path is empty, please check the configuration.")
            return None
        
        toppic_command = [self.args.get_config('tools', 'toppic')]
        
        # Add all command line options with values
        options = {
            'activation': ('--activation', str),
            'fixed-mod': ('--fixed-mod', str),
            'n-terminal-form': ('--n-terminal-form', str),
            'num-shift': ('--num-shift', str),
            'min-shift': ('--min-shift', str),
            'max-shift': ('--max-shift', str),
            'variable-ptm-num': ('--variable-ptm-num', str),
            'variable-ptm-file-name': ('--variable-ptm-file-name', str),
            'mass-error-tolerance': ('--mass-error-tolerance', str),
            'proteoform-error-tolerance': ('--proteoform-error-tolerance', str),
            'spectrum-cutoff-type': ('--spectrum-cutoff-type', str),
            'spectrum-cutoff-value': ('--spectrum-cutoff-value', str),
            'proteoform-cutoff-type': ('--proteoform-cutoff-type', str),
            'proteoform-cutoff-value': ('--proteoform-cutoff-value', str),
            'local-ptm-file-name': ('--local-ptm-file-name', str),
            'miscore-threshold': ('--miscore-threshold', str),
            'thread-number': ('--thread-number', str),
            'num-combined-spectra': ('--num-combined-spectra', str),
            'combined-file-name': ('--combined-file-name', str)
        }
        
        # Add options with values
        for key, (flag, converter) in options.items():
            value = self.args.get_config('toppic', key)
            if value and (key != 'fixed-mod' or value != 'Custom'):
                toppic_command.extend([flag, converter(value)])
        
        # Add boolean flags
        bool_flags = {
            'decoy': '--decoy',
            'approximate-spectra': '--approximate-spectra',
            'lookup-table': '--lookup-table',
            'no-topfd-feature': '--no-topfd-feature',
            'keep-temp-files': '--keep-temp-files',
            'keep-decoy-ids': '--keep-decoy-ids',
            'skip-html-folder': '--skip-html-folder'
        }
        
        for key, flag in bool_flags.items():
            if self.args.get_config('toppic', key):
                toppic_command.append(flag)
        
        # Add fasta file
        toppic_command.append(self.fasta_file)
        
        # Add input files
        for input_file in input_files:
            toppic_command.append(input_file)

        return toppic_command


if __name__ == '__main__':
    pass

