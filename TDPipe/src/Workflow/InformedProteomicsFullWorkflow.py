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
        for input_file in self.input_files:
            command = self._pbfgen_command(input_file)
            if command:
                self.commands.append(command)

        pbf_files = []
        for input_file in self.input_files:
            pbf_files.append(f"{self.output_dir}/{input_file.split('/')[-1].rsplit('.', 1)[0]}.pbf")
            
        for pbf_file in pbf_files:
            command = self._promex_command(pbf_file)
            if command:
                self.commands.append(command)
        
        for pbf_file in pbf_files:
            command = self._mspathfinder_command(pbf_file)
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
    
    def _mspathfinder_command(self, input_file):
        if not self.args.get_config('tools', 'mspathfinder'):
            self.log("MSPathFinder path is empty, please check the configuration.")
            return None
        
        mspathfinder_command = [self.args.get_config('tools', 'mspathfinder')]
        
        # Required input file
        mspathfinder_command.append('-i')
        mspathfinder_command.append(input_file)

        # Required database file
        mspathfinder_command.append('-d')
        mspathfinder_command.append(self.fasta_file)

        if self.args.get_config('output', None):
            mspathfinder_command.append('-o')
            mspathfinder_command.append(self.args.get_config('output', None))

        # Optional internal cleavage mode
        if self.args.get_config('mspathfinder', 'ic'):
            mspathfinder_command.append('-ic')
            mspathfinder_command.append(str(self.args.get_config('mspathfinder', 'ic')))

        # Optional tag search
        if self.args.get_config('mspathfinder', 'TagSearch') is not None:
            mspathfinder_command.append('-TagSearch')
            mspathfinder_command.append(str(self.args.get_config('mspathfinder', 'TagSearch')).lower())

        # Optional memory matches
        if self.args.get_config('mspathfinder', 'MemMatches'):
            mspathfinder_command.append('-MemMatches')
            mspathfinder_command.append(str(self.args.get_config('mspathfinder', 'MemMatches')))

        # Optional number of matches per spectrum
        if self.args.get_config('mspathfinder', 'NumMatchesPerSpec'):
            mspathfinder_command.append('-n')
            mspathfinder_command.append(str(self.args.get_config('mspathfinder', 'NumMatchesPerSpec')))

        # Optional include decoys
        if self.args.get_config('mspathfinder', 'IncludeDecoys'):
            mspathfinder_command.append('-IncludeDecoys')

        # Optional modification file
        if self.args.get_config('mspathfinder', 'ModificationFile'):
            mspathfinder_command.append('-mod')
            mspathfinder_command.append(self.args.get_config('mspathfinder', 'ModificationFile'))

        # Optional TDA mode
        if self.args.get_config('mspathfinder', 'tda') is not None:
            mspathfinder_command.append('-tda')
            mspathfinder_command.append('1' if self.args.get_config('mspathfinder', 'tda') else '0')

        # Optional overwrite
        if self.args.get_config('mspathfinder', 'overwrite'):
            mspathfinder_command.append('-overwrite')

        # Optional tolerances
        if self.args.get_config('mspathfinder', 'PMTolerance'):
            mspathfinder_command.append('-t')
            mspathfinder_command.append(str(self.args.get_config('mspathfinder', 'PMTolerance')))

        if self.args.get_config('mspathfinder', 'FragTolerance'):
            mspathfinder_command.append('-f')
            mspathfinder_command.append(str(self.args.get_config('mspathfinder', 'FragTolerance')))

        # Optional sequence length range
        if self.args.get_config('mspathfinder', 'MinLength'):
            mspathfinder_command.append('-MinLength')
            mspathfinder_command.append(str(self.args.get_config('mspathfinder', 'MinLength')))

        if self.args.get_config('mspathfinder', 'MaxLength'):
            mspathfinder_command.append('-MaxLength')
            mspathfinder_command.append(str(self.args.get_config('mspathfinder', 'MaxLength')))

        # Optional charge ranges
        if self.args.get_config('mspathfinder', 'MinCharge'):
            mspathfinder_command.append('-MinCharge')
            mspathfinder_command.append(str(self.args.get_config('mspathfinder', 'MinCharge')))

        if self.args.get_config('mspathfinder', 'MaxCharge'):
            mspathfinder_command.append('-MaxCharge')
            mspathfinder_command.append(str(self.args.get_config('mspathfinder', 'MaxCharge')))

        if self.args.get_config('mspathfinder', 'MinFragCharge'):
            mspathfinder_command.append('-MinFragCharge')
            mspathfinder_command.append(str(self.args.get_config('mspathfinder', 'MinFragCharge')))

        if self.args.get_config('mspathfinder', 'MaxFragCharge'):
            mspathfinder_command.append('-MaxFragCharge')
            mspathfinder_command.append(str(self.args.get_config('mspathfinder', 'MaxFragCharge')))

        # Optional mass range
        if self.args.get_config('mspathfinder', 'MinMass'):
            mspathfinder_command.append('-MinMass')
            mspathfinder_command.append(str(self.args.get_config('mspathfinder', 'MinMass')))

        if self.args.get_config('mspathfinder', 'MaxMass'):
            mspathfinder_command.append('-MaxMass')
            mspathfinder_command.append(str(self.args.get_config('mspathfinder', 'MaxMass')))

        # Optional feature file
        if self.args.get_config('mspathfinder', 'FeatureFile'):
            mspathfinder_command.append('-feature')
            mspathfinder_command.append(self.args.get_config('mspathfinder', 'FeatureFile'))

        # Optional thread count
        if self.args.get_config('mspathfinder', 'ThreadCount'):
            mspathfinder_command.append('-threads')
            mspathfinder_command.append(str(self.args.get_config('mspathfinder', 'ThreadCount')))

        # Optional activation method
        if self.args.get_config('mspathfinder', 'ActivationMethod'):
            mspathfinder_command.append('-act')
            mspathfinder_command.append(str(self.args.get_config('mspathfinder', 'ActivationMethod')))

        # Optional scans file
        if self.args.get_config('mspathfinder', 'ScansFile'):
            mspathfinder_command.append('-scansFile')
            mspathfinder_command.append(self.args.get_config('mspathfinder', 'ScansFile'))

        # Optional flip scoring
        if self.args.get_config('mspathfinder', 'UseFlipScoring'):
            mspathfinder_command.append('-flip')

        # Optional parameter file
        if self.args.get_config('mspathfinder', 'ParamFile'):
            mspathfinder_command.append('-ParamFile')
            mspathfinder_command.append(self.args.get_config('mspathfinder', 'ParamFile'))

        return mspathfinder_command