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
        
        # Add all command line options with values
        options = {
            'MinCharge': ('-MinCharge', str),
            'MaxCharge': ('-MaxCharge', str),
            'MinMass': ('-MinMass', str),
            'MaxMass': ('-MaxMass', str),
            'MaxThreads': ('-MaxThreads', str),
            'BinResPPM': ('-BinResPPM', str),
            'ScoreThreshold': ('-ScoreThreshold', str),
            'ms1ft': ('-ms1ft', str),
            'ParamFile': ('-ParamFile', str)
        }
        
        # Add options with values
        for key, (flag, converter) in options.items():
            value = self.args.get_config('promex', key)
            if value:
                promex_command.extend([flag, converter(value)])
        
        # Add boolean flags
        bool_flags = {
            'Score': '-Score',
            'csv': '-csv'
        }
        
        for key, flag in bool_flags.items():
            if self.args.get_config('promex', key):
                promex_command.append(flag)
        
        # Special handling for FeatureMap
        if self.args.get_config('promex', 'FeatureMap') is not None and not self.args.get_config('promex', 'FeatureMap'):
            promex_command.append('-FeatureMap:false')

        # Add required input file
        promex_command.extend(['-i', input_file])
        
        # Add output directory if specified
        if self.args.get_config('output', None):
            promex_command.extend(['-o', self.args.get_config('output', None)])

        return promex_command
