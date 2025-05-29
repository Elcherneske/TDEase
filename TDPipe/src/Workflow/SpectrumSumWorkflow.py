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
        if self.args.get_config('spectrum_sum', 'tool'):
            sum_spectrum_command.extend(["--tool", self.args.get_config('spectrum_sum', 'tool')])

        if self.args.get_config('spectrum_sum', 'method'):
            sum_spectrum_command.extend(["--method", self.args.get_config('spectrum_sum', 'method')])
        
        if self.args.get_config('spectrum_sum', 'block_size'):
            sum_spectrum_command.extend(["--block-size", self.args.get_config('spectrum_sum', 'block_size')])
        
        if self.args.get_config('spectrum_sum', 'start_scan'):
            sum_spectrum_command.extend(["--start-scan", self.args.get_config('spectrum_sum', 'start_scan')])
        
        if self.args.get_config('spectrum_sum', 'end_scan'):
            sum_spectrum_command.extend(["--end-scan", self.args.get_config('spectrum_sum', 'end_scan')])
        
        if self.args.get_config('spectrum_sum', 'ms_level'):
            sum_spectrum_command.extend(["--ms-level", self.args.get_config('spectrum_sum', 'ms_level')])
        
        if self.args.get_config('spectrum_sum', 'rt_tolerance'):
            sum_spectrum_command.extend(["--rt-tolerance", self.args.get_config('spectrum_sum', 'rt_tolerance')])
        
        if self.args.get_config('spectrum_sum', 'mz_tolerance'):
            sum_spectrum_command.extend(["--mz-tolerance", self.args.get_config('spectrum_sum', 'mz_tolerance')])
        
        sum_spectrum_command.extend(["--input", input_file])

        if self.output_dir:
            sum_spectrum_command.extend(["--output-dir", self.output_dir])
        
        return sum_spectrum_command
        
        
        
        
        
