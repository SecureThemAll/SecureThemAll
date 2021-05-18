from core.input_parser import add_repair_tool
from core.repair_tools.sosrepair import SOSRepair


class SearchRepair(SOSRepair):
    """SearchRepair"""

    def __init__(self, **kwargs):
        super(SearchRepair, self).__init__(name="SearchRepair", **kwargs)


def search_repair_args(input_parser):
    input_parser.add_argument('--version', action='version', version='SOSRepair/SearchRepair ae6550e')


parser = add_repair_tool("SearchRepair", SearchRepair, 'Repair the challenge with SearchRepair')
search_repair_args(parser)

