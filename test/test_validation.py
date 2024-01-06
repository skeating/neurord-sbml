from src.neurord_sbml.validateSBML import validateSBML

import libsbml


def test_basic_sbml():
    """
    Function to test the validation of a basic SBML file.
    """
    validator = validateSBML(True, True)
    file_name = 'resources/basicSBML.xml'
    errors = validator.validate_file(file_name)
    assert (errors == 0)


def test_sbml_document():
    """
    Function to test the validation of an SBML document as read by libsbml.
    """
    validator = validateSBML(True, True)
    file_name = 'resources/basicSBML.xml'
    document = libsbml.readSBML(file_name)
    errors = validator.validate_sbml_document(document)
    assert (errors == 0)


def test_basic_model(model):
    """
    Function to test the validation of an SBML model created by conversion from neuroRD.

    Note this function does not test unit validation.
    """
    validator = validateSBML(False, True)
    sbml_model = libsbml.readSBMLFromString(model.toSBML())
    errors = validator.validate_model(sbml_model)
    assert (errors == 0)


def test_basic_model_with_units(model):
    """
    Function to test the validation of an SBML model created by conversion from neuroRD.

    Note this function does test unit validation.
    """
    validator = validateSBML(True, False-)
    sbml_model = libsbml.readSBMLFromString(model.toSBML())
    errors = validator.validate_model(sbml_model)
    assert (errors == 0)
