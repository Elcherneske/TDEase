from .BaseWorkflow import BaseWorkflow

class TopfdWorkflow(BaseWorkflow):
    def __init__(self, args):
        super().__init__()
        self.args = args
        self.input_files = args.get_config('msfile', None)

    def prepare_workflow(self):
        self.commands = []
        command = self._topfd_command()
        if command:
            self.commands.append(command)

    def _topfd_command(self):
        if not self.args.get_config('tools', 'topfd'):
            self.log("TopFD path is empty, please check the configuration.")
            return None
        
        topfd_command = [self.args.get_config('tools', 'topfd')]
        if self.args.get_config('topfd', 'activation'):
            topfd_command.append('--activation')
            topfd_command.append(self.args.get_config('topfd', 'activation'))
        
        if self.args.get_config('topfd', 'max_charge'):
            topfd_command.append('--max-charge')
            topfd_command.append(str(self.args.get_config('topfd', 'max_charge')))
        
        if self.args.get_config('topfd', 'max_mass'):
            topfd_command.append('--max-mass')
            topfd_command.append(str(self.args.get_config('topfd', 'max_mass')))
        
        if self.args.get_config('topfd', 'mz_error'):
            topfd_command.append('--mz-error')
            topfd_command.append(str(self.args.get_config('topfd', 'mz_error')))
        
        if self.args.get_config('topfd', 'ms1_sn'):
            topfd_command.append('--ms-one-sn-ratio')
            topfd_command.append(str(self.args.get_config('topfd', 'ms1_sn')))
        
        if self.args.get_config('topfd', 'ms2_sn'):
            topfd_command.append('--ms-two-sn-ratio')
            topfd_command.append(str(self.args.get_config('topfd', 'ms2_sn')))
        
        if self.args.get_config('topfd', 'precursor_window'):
            topfd_command.append('--precursor-window')
            topfd_command.append(str(self.args.get_config('topfd', 'precursor_window')))
        
        if self.args.get_config('topfd', 'ecscore_cutoff'):
            topfd_command.append('--ecscore-cutoff')
            topfd_command.append(str(self.args.get_config('topfd', 'ecscore_cutoff')))
        
        if self.args.get_config('topfd', 'min_scan_number'):
            topfd_command.append('--min-scan-number')
            topfd_command.append(str(self.args.get_config('topfd', 'min_scan_number')))
        
        if self.args.get_config('topfd', 'thread_number'):
            topfd_command.append('--thread-number')
            topfd_command.append(str(self.args.get_config('topfd', 'thread_number')))
        
        if self.args.get_config('topfd', 'skip_html_folder'):
            topfd_command.append('--skip-html-folder')
        
        if self.args.get_config('topfd', 'disable_additional_feature_search'):
            topfd_command.append('--disable-additional-feature-search')
        
        if self.args.get_config('topfd', 'disable_final_filtering'):
            topfd_command.append('--disable-final-filtering')
        
        for input_file in self.input_files:
            topfd_command.append(input_file)

        return topfd_command

if __name__ == '__main__':
    pass
