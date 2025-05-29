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
        
        # Required input file
        pbfgen_command.append('-i')
        pbfgen_command.append(input_file)
        
        if self.args.get_config('output', None):
            pbfgen_command.append('-o')
            pbfgen_command.append(self.args.get_config('output', None)) 

        # Optional start scan
        if self.args.get_config('pbfgen', 'start'):
            pbfgen_command.append('-start')
            pbfgen_command.append(str(self.args.get_config('pbfgen', 'start')))

        # Optional end scan
        if self.args.get_config('pbfgen', 'end'):
            pbfgen_command.append('-end')
            pbfgen_command.append(str(self.args.get_config('pbfgen', 'end')))

        # Optional parameter file
        if self.args.get_config('pbfgen', 'ParamFile'):
            pbfgen_command.append('-ParamFile')
            pbfgen_command.append(self.args.get_config('pbfgen', 'ParamFile'))

        return pbfgen_command
