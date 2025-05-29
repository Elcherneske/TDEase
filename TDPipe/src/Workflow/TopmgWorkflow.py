from .BaseWorkflow import BaseWorkflow

class TopmgWorkflow(BaseWorkflow):
    def __init__(self, args):
        super().__init__()
        self.args = args
        self.input_files = args.get_config('msfile', None)
        self.fasta_file = args.get_config('fasta', None)

    def prepare_workflow(self):
        self.commands = []
        command = self._topmg_command()
        if command:
            self.commands.append(command)
    
    def _topmg_command(self):
        if not self.args.get_config('tools', 'topmg'):
            self.log("TopMG路径为空，请检查配置。")
            return None
        
        topmg_command = [self.args.get_config('tools', 'topmg')]
        
        if self.args.get_config('topmg', 'activation'):
            topmg_command.append('--activation')
            topmg_command.append(self.args.get_config('topmg', 'activation'))
        
        if self.args.get_config('topmg', 'fixed-mod'):
            topmg_command.append('--fixed-mod')
            topmg_command.append(self.args.get_config('topmg', 'fixed-mod'))

        if self.args.get_config('topmg', 'n-terminal-form'):
            topmg_command.append('--n-terminal-form')
            topmg_command.append(self.args.get_config('topmg', 'n-terminal-form'))

        if self.args.get_config('topmg', 'decoy'):
            topmg_command.append('--decoy')

        if self.args.get_config('topmg', 'mass-error-tolerance'):
            topmg_command.append('--mass-error-tolerance')
            topmg_command.append(str(self.args.get_config('topmg', 'mass-error-tolerance')))

        if self.args.get_config('topmg', 'proteoform-error-tolerance'):
            topmg_command.append('--proteoform-error-tolerance')
            topmg_command.append(str(self.args.get_config('topmg', 'proteoform-error-tolerance')))

        if self.args.get_config('topmg', 'max-shift'):
            topmg_command.append('--max-shift')
            topmg_command.append(str(self.args.get_config('topmg', 'max-shift')))

        if self.args.get_config('topmg', 'spectrum-cutoff-type'):
            topmg_command.append('--spectrum-cutoff-type')
            topmg_command.append(self.args.get_config('topmg', 'spectrum-cutoff-type'))
        
        if self.args.get_config('topmg', 'spectrum-cutoff-value'):
            topmg_command.append('--spectrum-cutoff-value')
            topmg_command.append(str(self.args.get_config('topmg', 'spectrum-cutoff-value')))

        if self.args.get_config('topmg', 'proteoform-cutoff-type'):
            topmg_command.append('--proteoform-cutoff-type')
            topmg_command.append(self.args.get_config('topmg', 'proteoform-cutoff-type'))

        if self.args.get_config('topmg', 'proteoform-cutoff-value'):
            topmg_command.append('--proteoform-cutoff-value')
            topmg_command.append(str(self.args.get_config('topmg', 'proteoform-cutoff-value')))

        if self.args.get_config('topmg', 'mod-file-name'):
            topmg_command.append('--mod-file-name')
            topmg_command.append(self.args.get_config('topmg', 'mod-file-name'))

        if self.args.get_config('topmg', 'thread-number'):
            topmg_command.append('--thread-number')
            topmg_command.append(str(self.args.get_config('topmg', 'thread-number')))

        if self.args.get_config('topmg', 'no-topfd-feature'):
            topmg_command.append('--no-topfd-feature')

        if self.args.get_config('topmg', 'proteo-graph-gap'):
            topmg_command.append('--proteo-graph-gap')
            topmg_command.append(str(self.args.get_config('topmg', 'proteo-graph-gap')))

        if self.args.get_config('topmg', 'var-ptm-in-gap'):
            topmg_command.append('--var-ptm-in-gap')
            topmg_command.append(str(self.args.get_config('topmg', 'var-ptm-in-gap')))

        if self.args.get_config('topmg', 'use-asf-diagonal'):
            topmg_command.append('--use-asf-diagonal')

        if self.args.get_config('topmg', 'var-ptm'):
            topmg_command.append('--var-ptm')
            topmg_command.append(str(self.args.get_config('topmg', 'var-ptm')))

        if self.args.get_config('topmg', 'num-shift'):
            topmg_command.append('--num-shift')
            topmg_command.append(str(self.args.get_config('topmg', 'num-shift')))

        if self.args.get_config('topmg', 'whole-protein-only'):
            topmg_command.append('--whole-protein-only')

        if self.args.get_config('topmg', 'combined-file-name'):
            topmg_command.append('--combined-file-name')
            topmg_command.append(self.args.get_config('topmg', 'combined-file-name'))

        if self.args.get_config('topmg', 'keep-temp-files'):
            topmg_command.append('--keep-temp-files')

        if self.args.get_config('topmg', 'keep-decoy-ids'):
            topmg_command.append('--keep-decoy-ids')

        if self.args.get_config('topmg', 'skip-html-folder'):
            topmg_command.append('--skip-html-folder')

        topmg_command.append(self.fasta_file)

        for file in self.input_files:
            topmg_command.append(file)

        return topmg_command
