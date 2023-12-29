from src.neurord_sbml.validateSBML import validateSBML

import libsbml


def test_basic_sbml():
    validator = validateSBML(True, True)
    file_name = 'resources/basicSBML.xml'
    errors = validator.validate_file(file_name)
    assert (errors == 0)


def test_sbml_document():
    validator = validateSBML(True, True)
    file_name = 'resources/basicSBML.xml'
    document = libsbml.readSBML(file_name)
    errors = validator.validate_sbml_document(document)
    assert (errors == 0)


def test_basic_model(model):
    validator = validateSBML(False, True)
    sbml_model = libsbml.readSBMLFromString(model.toSBML())
    errors = validator.validate_model(sbml_model)
    assert (errors == 0)


