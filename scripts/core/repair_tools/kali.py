from core.input_parser import add_repair_tool
from core.repair_tools.prophet import Prophet


class Kali(Prophet):
    """Kali"""

    def __init__(self, **kwargs):
        super(Kali, self).__init__(name="Kali", **kwargs)


def kali_args(input_parser):
    input_parser.add_argument('--version', action='version', version='Prophet/Kali')


parser = add_repair_tool("Kali", Kali, 'Repair the challenge with Kali')
kali_args(parser)
