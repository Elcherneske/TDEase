from .BaseWorkflow import BaseWorkflow

class PromexWorkflow(BaseWorkflow):
    def __init__(self, args):
        super().__init__()
        self.args = args
        self.input_files = args.get_config('msfile', None)

    def prepare_workflow(self):
        self.commands = []
        for input_file in self.input_files:
            command = self._promex_command(input_file)
            if command:
                self.commands.append(command)
    
    def _promex_command(self, input_file):
        if not self.args.get_config('tools', 'promex'):
            self.log("Promex path is empty, please check the configuration.")
            return None
        
        promex_command = [self.args.get_config('tools', 'promex')]
        
        # Required input file
        promex_command.append('-i')
        promex_command.append(input_file)
        
        if self.args.get_config('output', None):
            promex_command.append('-o')
            promex_command.append(self.args.get_config('output', None))

        # Optional charge range
        if self.args.get_config('promex', 'MinCharge'):
            promex_command.append('-MinCharge')
            promex_command.append(str(self.args.get_config('promex', 'MinCharge')))
        
        if self.args.get_config('promex', 'MaxCharge'):
            promex_command.append('-MaxCharge')
            promex_command.append(str(self.args.get_config('promex', 'MaxCharge')))

        # Optional mass range
        if self.args.get_config('promex', 'MinMass'):
            promex_command.append('-MinMass')
            promex_command.append(str(self.args.get_config('promex', 'MinMass')))
        
        if self.args.get_config('promex', 'MaxMass'):
            promex_command.append('-MaxMass')
            promex_command.append(str(self.args.get_config('promex', 'MaxMass')))

        # Optional feature map
        if self.args.get_config('promex', 'FeatureMap') is not None:
            promex_command.append('-FeatureMap')
            if not self.args.get_config('promex', 'FeatureMap'):
                promex_command.append('false')

        # Optional score output
        if self.args.get_config('promex', 'Score'):
            promex_command.append('-Score')

        # Optional thread count
        if self.args.get_config('promex', 'MaxThreads'):
            promex_command.append('-MaxThreads')
            promex_command.append(str(self.args.get_config('promex', 'MaxThreads')))

        # Optional CSV output
        if self.args.get_config('promex', 'Csv'):
            promex_command.append('-Csv')

        # Optional bin resolution
        if self.args.get_config('promex', 'BinResPPM'):
            promex_command.append('-BinResPPM')
            promex_command.append(str(self.args.get_config('promex', 'BinResPPM')))

        # Optional score threshold
        if self.args.get_config('promex', 'ScoreThreshold'):
            promex_command.append('-ScoreThreshold')
            promex_command.append(str(self.args.get_config('promex', 'ScoreThreshold')))

        # Optional ms1ft file
        if self.args.get_config('promex', 'ms1ft'):
            promex_command.append('-ms1ft')
            promex_command.append(self.args.get_config('promex', 'ms1ft'))

        # Optional parameter file
        if self.args.get_config('promex', 'ParamFile'):
            promex_command.append('-ParamFile')
            promex_command.append(self.args.get_config('promex', 'ParamFile'))

        return promex_command
