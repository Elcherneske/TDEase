from .BaseWorkflow import BaseWorkflow

class ToppicWorkflow(BaseWorkflow):
    def __init__(self, args):
        super().__init__()
        self.args = args
        self.input_files = args.get_config('msfile', None)
        self.fasta_file = args.get_config('fasta', None)

    def prepare_workflow(self):
        self.commands = []
        self.check_fns = []
        self.gap_nums = []

        command = self._toppic_command()
        if command:
            self.commands.append(command)
            self.check_fns.append(
                lambda text: 
                    ("unexpected shift filtering - processing" in text and "%" in text) or
                    ("unexpected shift search - processing" in text)
            )
            self.gap_nums.append(20000)
    
    def _toppic_command(self):
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
        for input_file in self.input_files:
            toppic_command.append(input_file)

        return toppic_command

