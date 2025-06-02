from .BaseWorkflow import BaseWorkflow

class TopmgWorkflow(BaseWorkflow):
    def __init__(self, args):
        super().__init__()
        self.args = args
        self.input_files = args.get_config('msfile', None)
        self.fasta_file = args.get_config('fasta', None)

    def prepare_workflow(self):
        self.commands = []
        self.check_fns = []
        self.gap_nums = []
        command = self._topmg_command()
        if command:
            self.commands.append(command)
            self.check_fns.append(None)
            self.gap_nums.append(0)
    
    def _topmg_command(self):
        if not self.args.get_config('tools', 'topmg'):
            self.log("TopMG路径为空，请检查配置。")
            return None
        
        topmg_command = [self.args.get_config('tools', 'topmg')]
        
        # Add all command line options with values
        options = {
            'activation': ('--activation', str),
            'fixed-mod': ('--fixed-mod', str),
            'n-terminal-form': ('--n-terminal-form', str),
            'mass-error-tolerance': ('--mass-error-tolerance', str),
            'proteoform-error-tolerance': ('--proteoform-error-tolerance', str),
            'max-shift': ('--max-shift', str),
            'spectrum-cutoff-type': ('--spectrum-cutoff-type', str),
            'spectrum-cutoff-value': ('--spectrum-cutoff-value', str),
            'proteoform-cutoff-type': ('--proteoform-cutoff-type', str),
            'proteoform-cutoff-value': ('--proteoform-cutoff-value', str),
            'mod-file-name': ('--mod-file-name', str),
            'thread-number': ('--thread-number', str),
            'proteo-graph-gap': ('--proteo-graph-gap', str),
            'var-ptm-in-gap': ('--var-ptm-in-gap', str),
            'var-ptm': ('--var-ptm', str),
            'num-shift': ('--num-shift', str),
            'combined-file-name': ('--combined-file-name', str)
        }
        
        # Add options with values
        for key, (flag, converter) in options.items():
            value = self.args.get_config('topmg', key)
            if value:
                topmg_command.extend([flag, converter(value)])
        
        # Add boolean flags
        bool_flags = {
            'decoy': '--decoy',
            'no-topfd-feature': '--no-topfd-feature',
            'use-asf-diagonal': '--use-asf-diagonal',
            'whole-protein-only': '--whole-protein-only',
            'keep-temp-files': '--keep-temp-files',
            'keep-decoy-ids': '--keep-decoy-ids',
            'skip-html-folder': '--skip-html-folder'
        }
        
        for key, flag in bool_flags.items():
            if self.args.get_config('topmg', key):
                topmg_command.append(flag)
        
        # Add fasta file
        topmg_command.append(self.fasta_file)
        
        # Add input files
        for input_file in self.input_files:
            topmg_command.append(input_file)

        return topmg_command
