from .MSConvertWorkflow import MSConvertWorkflow
from .TopfdWorkflow import TopfdWorkflow
from .ToppicWorkflow import ToppicWorkflow
from .TopmgWorkflow import TopmgWorkflow
from .PbfgenWorkflow import PbfgenWorkflow
from .PromexWorkflow import PromexWorkflow
from .MSpathfinderWorkflow import MSpathfinderWorkflow
from .PbfgenPromexWorkflow import PbfgenPromexWorkflow
from .ToppicSuiteWorkflow import ToppicSuitWorkflow
from .SpectrumSumWorkflow import SpectrumSumWorkflow
from .InformedProteomicsFullWorkflow import InformedProteomicsFullWorkflow

class WorkflowManager:
    @staticmethod
    def create_workflow(mode, args):
        workflows = {
            'msconvert': MSConvertWorkflow,
            'topfd': TopfdWorkflow,
            'toppic': ToppicWorkflow,
            'topmg': TopmgWorkflow,
            'pbfgen': PbfgenWorkflow,
            'promex': PromexWorkflow,
            'mspathfinder': MSpathfinderWorkflow,
            'Informed Proteomics MS1-Only': PbfgenPromexWorkflow,
            'TopPIC Suite': ToppicSuitWorkflow,
            'sum spectrum': SpectrumSumWorkflow,
            'Informed Proteomics Full': InformedProteomicsFullWorkflow,
            # 可以添加更多模式
        }
        
        if mode not in workflows:
            raise ValueError(f"不支持的模式: {mode}")
            
        return workflows[mode](args) 

if __name__ == '__main__':
    pass
