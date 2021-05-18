from core.input_parser import add_repair_tool
from core.repair_tools.prophet import Prophet


class SPR(Prophet):
    """SPR"""

    def __init__(self, **kwargs):
        super(SPR, self).__init__(name="SPR", **kwargs)


def spr_args(input_parser):
    input_parser.add_argument('--version', action='version', version='Prophet/SPR')


parser = add_repair_tool("SPR", SPR, 'Repair the challenge with SPR')
spr_args(parser)
