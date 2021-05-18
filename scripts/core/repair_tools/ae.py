from core.input_parser import add_repair_tool
from core.repair_tools.genprog import GenProg


class AE(GenProg):
    """GenProg"""

    def __init__(self, **kwargs):
        super(AE, self).__init__(name="AE", **kwargs)


def ae_args(input_parser):
    input_parser.add_argument('--version', action='version', version='GenProg/AE e720256')


parser = add_repair_tool("AE", AE, 'Repair the challenge with AE')
ae_args(parser)

