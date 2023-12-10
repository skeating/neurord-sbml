import pytest

from src.neurord_sbml.convert import convert


class Arguments:
    def __init__(self):
        self.reactions_file = ""


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
    arguments.testing = True
    converter = convert(arguments)
    model = converter.do_conversion()
    return model
