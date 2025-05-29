from .BaseWorkflow import BaseWorkflow

class MSpathfinderWorkflow(BaseWorkflow):
    def __init__(self, args):
        super().__init__()
        self.args = args
        self.input_files = args.get_config('msfile', None)
        self.fasta_file = args.get_config('fasta', None)

    def prepare_workflow(self):
        self.commands = []
        command = self._mspathfinder_command()
        if command:
            self.commands.append(command)
    
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

