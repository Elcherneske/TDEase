from .BaseWorkflow import BaseWorkflow
import os
import sys

class SpectrumSumWorkflow(BaseWorkflow):
    def __init__(self, args):
        super().__init__()
        self.args = args
        self.input_files = args.get_config('msfile', None)
        self.output_dir = args.get_config('output', None)
    
    def prepare_workflow(self):
        self.commands = []
        for input_file in self.input_files:
            command = self._sum_spectrum_command(input_file)
            if command:
                self.commands.append(command)
    
    def _sum_spectrum_command(self, input_file):
        python_path = self.args.get_config('tools', 'python')
        if not python_path:
            self.log("Python path is not set. Please configure it in the Tools tab.")
            return None

        script_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "Tools", "spectrum_sum.py")

        sum_spectrum_command = [python_path, script_path]
        
        # Add all command line options with values
        options = {
            'tool': ('--tool', str),
            'method': ('--method', str),
            'block_size': ('--block-size', str),
            'start_scan': ('--start-scan', str),
            'end_scan': ('--end-scan', str),
            'ms_level': ('--ms-level', str),
            'rt_tolerance': ('--rt-tolerance', str),
            'mz_tolerance': ('--mz-tolerance', str)
        }
        
        # Add options with values
        for key, (flag, converter) in options.items():
            value = self.args.get_config('spectrum_sum', key)
            if value:
                sum_spectrum_command.extend([flag, converter(value)])

        # Add required input file
        sum_spectrum_command.extend(["--input", input_file])
        
        # Add output directory if specified
        if self.output_dir:
            sum_spectrum_command.extend(["--output-dir", self.output_dir])
        
        return sum_spectrum_command
        
        
        
        
        
