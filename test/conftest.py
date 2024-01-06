import pytest

from src.neurord_sbml.convert import convert


class Arguments:
    """
    Class to mimic the command line arguments.
    """
    def __init__(self):
        self.reactions_file = ""
        self.initial_conditions_file = ""
        self.display_only = True
        self.validate = False


@pytest.fixture(scope="session")
def model():
    """
    Create an instance of SBML model.

    :return: SBML model
    """
    arguments = Arguments()
    arguments.reactions_file = './resources/Reactions.xml'
    arguments.initial_conditions_file = './resources/IC.xml'
    arguments.display_only = True
    arguments.validate = False
    converter = convert(arguments)
    model = converter.do_conversion()
    return model
