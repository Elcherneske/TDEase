from .BaseWorkflow import BaseWorkflow

class InformedProteomicsFullWorkflow(BaseWorkflow):
    def __init__(self, args):
        super().__init__()
        self.args = args
        self.input_files = args.get_config('msfile', None)
        self.fasta_file = args.get_config('fasta', None)
        self.output_dir = args.get_config('output', None)

    def prepare_workflow(self):
        self.commands = []
        self.check_fns = []
        self.gap_nums = []

        for input_file in self.input_files:
            command = self._pbfgen_command(input_file)
            if command:
                self.commands.append(command)
                self.check_fns.append(None)
                self.gap_nums.append(0)

        pbf_files = []
        for input_file in self.input_files:
            pbf_files.append(f"{self.output_dir}/{input_file.split('/')[-1].rsplit('.', 1)[0]}.pbf")
            
        for pbf_file in pbf_files:
            command = self._promex_command(pbf_file)
            if command:
                self.commands.append(command)
                self.check_fns.append(None)
                self.gap_nums.append(0)
        

        command = self._mspathfinder_command(pbf_files)
        if command:
            self.commands.append(command)
            self.check_fns.append(None)
            self.gap_nums.append(0)
    

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
    
    def _mspathfinder_command(self, input_files: list[str]):
        if not self.args.get_config('tools', 'mspathfinder'):
            self.log("MSPathFinder path is empty, please check the configuration.")
            return None
        
        mspathfinder_command = [self.args.get_config('tools', 'mspathfinder')]
        
        # Required input file
        mspathfinder_command.append('-i')
        for file in input_files:
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