from .BaseWorkflow import BaseWorkflow

class PbfgenWorkflow(BaseWorkflow):
    def __init__(self, args):
        super().__init__()
        self.args = args
        self.input_files = args.get_config('msfile', None)

    def prepare_workflow(self):
        self.commands = []
        for input_file in self.input_files:
            command = self._pbfgen_command(input_file)
            if command:
                self.commands.append(command)

    
    def _pbfgen_command(self, input_file):
        if not self.args.get_config('tools', 'pbfgen'):
            self.log("PBFGen path is empty, please check the configuration.")
            return None
        
        pbfgen_command = [self.args.get_config('tools', 'pbfgen')]
        
        # Add all command line options with values
        options = {
            'start': ('-start', str),
            'end': ('-end', str),
            'ParamFile': ('-ParamFile', str)
        }
        
        # Add options with values
        for key, (flag, converter) in options.items():
            value = self.args.get_config('pbfgen', key)
            if value:
                pbfgen_command.extend([flag, converter(value)])
        
        # Add required input file
        pbfgen_command.extend(['-i', input_file])
        
        # Add output directory if specified
        if self.args.get_config('output', None):
            pbfgen_command.extend(['-o', self.args.get_config('output', None)])

        return pbfgen_command
