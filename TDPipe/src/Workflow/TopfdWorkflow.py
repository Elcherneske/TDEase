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
        for input_file in self.input_files:
            topfd_command.append(input_file)

        return topfd_command

if __name__ == '__main__':
    pass
