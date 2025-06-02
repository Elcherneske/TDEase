from .BaseWorkflow import BaseWorkflow

class MSpathfinderWorkflow(BaseWorkflow):
    def __init__(self, args):
        super().__init__()
        self.args = args
        self.input_files = args.get_config('msfile', None)
        self.fasta_file = args.get_config('fasta', None)

    def prepare_workflow(self):
        self.commands = []
        self.check_fns = []
        self.gap_nums = []
        command = self._mspathfinder_command()
        if command:
            self.commands.append(command)
            self.check_fns.append(None)
            self.gap_nums.append(0)
    
    def _mspathfinder_command(self):
        if not self.args.get_config('tools', 'mspathfinder'):
            self.log("MSPathFinder path is empty, please check the configuration.")
            return None
        
        mspathfinder_command = [self.args.get_config('tools', 'mspathfinder')]
        
        # Required input file
        mspathfinder_command.append('-i')
        for file in self.input_files:
            mspathfinder_command.append(file)

        # Required database file
        mspathfinder_command.append('-d')
        mspathfinder_command.append(self.fasta_file)

        if self.args.get_config('output', None):
            mspathfinder_command.append('-o')
            mspathfinder_command.append(self.args.get_config('output', None))

        # Add all command line options with values
        options = {
            'ic': ('-ic', str),
            'TagSearch': ('-TagSearch', lambda x: str(x).lower()),
            'MemMatches': ('-MemMatches', str),
            'NumMatchesPerSpec': ('-n', str),
            'ModificationFile': ('-mod', str),
            'PMTolerance': ('-t', str),
            'FragTolerance': ('-f', str),
            'MinLength': ('-MinLength', str),
            'MaxLength': ('-MaxLength', str),
            'MinCharge': ('-MinCharge', str),
            'MaxCharge': ('-MaxCharge', str),
            'MinFragCharge': ('-MinFragCharge', str),
            'MaxFragCharge': ('-MaxFragCharge', str),
            'MinMass': ('-MinMass', str),
            'MaxMass': ('-MaxMass', str),
            'FeatureFile': ('-feature', str),
            'ThreadCount': ('-threads', str),
            'ActivationMethod': ('-act', str),
            'ScansFile': ('-scansFile', str),
            'ParamFile': ('-ParamFile', str)
        }
        
        # Add options with values
        for key, (flag, converter) in options.items():
            value = self.args.get_config('mspathfinder', key)
            if value is not None:
                mspathfinder_command.extend([flag, converter(value)])

        # Add boolean flags
        bool_flags = {
            'IncludeDecoys': '-IncludeDecoys',
            'overwrite': '-overwrite',
            'UseFlipScoring': '-flip'
        }
        
        for key, flag in bool_flags.items():
            if self.args.get_config('mspathfinder', key):
                mspathfinder_command.append(flag)

        # Special handling for TDA mode
        if self.args.get_config('mspathfinder', 'tda') is not None:
            mspathfinder_command.extend(['-tda', '1' if self.args.get_config('mspathfinder', 'tda') else '0'])

        return mspathfinder_command

