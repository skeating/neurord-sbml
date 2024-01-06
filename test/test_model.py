
def test_model_units(model):
    assert (model.model.time_units == "ms")
    assert (model.model.substance_units == "nM")
    assert (model.model.extent_units == "nM")


def test_model_elements(model):
    assert (model.model.num_unit_definitions == 8)
    assert (model.model.num_compartments == 1)
    assert (model.model.num_species == 4)
    assert (model.model.num_reactions == 2)
    assert (model.model.num_parameters == 4)


def test_compartment(model):
    compartment = model.model.compartments[0]
    assert (compartment.id == "compartment")
    assert (compartment.size == 5e-16)
    assert (compartment.spatial_dimensions == 3)
    assert compartment.constant
    assert (compartment.units == "litre")


def test_unit_definitions(model):
    assert (model.model.num_unit_definitions == 8)


def test_species1(model):
    species = model.model.species[0]
    assert (species.id == "Ca")
    assert not species.boundary_condition
    assert not species.constant
    assert not species.has_only_substance_units
    assert (species.units == "nM")
    assert (species.initial_concentration == 0)


def test_species2(model):
    species = model.model.species[1]
    assert (species.id == "CaOut")
    assert not species.boundary_condition
    assert not species.constant
    assert not species.has_only_substance_units
    assert (species.units == "nM")
    assert (species.initial_concentration == 1900000)


def test_reaction1(model):
    reaction = model.model.reactions[0]
    assert (reaction.id == "r1")
    assert (reaction.num_reactants == 2)
    assert (reaction.num_products == 1)


def test_reaction2(model):
    reaction = model.model.reactions[1]
    assert (reaction.id == "r2")
    assert (reaction.num_reactants == 1)
    assert (reaction.num_products == 2)


def test_parameter1(model):
    parameter = model.model.parameters[0]
    assert (parameter.id == "kon_1")
    assert (parameter.value == 0.5e-4)
    assert not parameter.constant
    assert (parameter.units == "l_per_nM_per_ms")


def test_parameter2(model):
    parameter = model.model.parameters[1]
    assert (parameter.id == "koff_1")
    assert (parameter.value == 0.007)
    assert not parameter.constant
    assert (parameter.units == "per_ms")


def test_parameter3(model):
    parameter = model.model.parameters[2]
    assert (parameter.id == "kon_2")
    assert (parameter.value == 0.0035)
    assert not parameter.constant
    assert (parameter.units == "per_ms")


def test_parameter4(model):
    parameter = model.model.parameters[3]
    assert (parameter.id == "koff_2")
    assert (parameter.value == 0.0)
    assert not parameter.constant
    assert (parameter.units == "l_per_nM_per_ms")
    