from xml.etree import ElementTree as ET

import libsbml
import simplesbml


# the class that does the conversion
class convert:
    def __init__(self, arguments):
        self.rx = ET.parse(arguments.reactions_file)
        self.ic = ET.parse(arguments.initial_conditions_file)
        self.root = self.rx.getroot()
        self.ic_root = self.ic.getroot()

        # variables that will be needed
        self.is_conc = True
        self.size_micron_cubed = 0.5  # presumably this is the size of the compartment
        self.micron_cube_to_litre = 1e-15 # conversion to litres
        self.comp = 'compartment'

        # variables that will be populated
        self.model = None
        self.units = {}
        self.species = {}
        self.conc_dict = {}

    def do_conversion(self):
        self.convert_to_nanomoles()
        self.create_model()
        self.add_unit_definitions()
        self.add_species_parameters_reactions()
        return self.model

    def add_species_parameters_reactions(self):        
        reaction_num = 0
        for i, child in enumerate(self.root):
            #     print(i)
            if child.tag == "Specie":
                self.add_species(child)
            elif child.tag == "Reaction":
                reaction_num = self.add_parameters_and_reactions(child, reaction_num)
#                print(i)
 #               print(child)
            else:
                print('Encountered a problem')

    def add_species(self, child):
        if not child.attrib["id"][0].isdigit():
            specie = child.attrib["id"]
        else:
            specie = "_" + child.attrib["id"]
            
        if self.is_conc:
            spec_name = "[{}]".format(specie)
        else:
            spec_name = specie
        self.model.addSpecies(spec_name, self.conc_dict[child.attrib["name"]], comp=self.comp)

        self.species.update({child.attrib["id"]: specie})

    def add_parameters_and_reactions(self, child, reaction_num):
        reaction_num += 1
        reactants, products = [], []
        local_params = {}
        rorder, porder = {}, {}
        kin_law = ""
        for reactant in child:
            if reactant.tag == "Reactant":
                reac_id = self.species[reactant.attrib["specieID"]]
                reactants.append(reac_id)
                if "power" in reactant.attrib:
                    rorder[reac_id] = reactant.attrib["power"]
                else:
                    rorder[reac_id] = "1"
            elif reactant.tag == "Product":
                reac_id = self.species[reactant.attrib["specieID"]]
                products.append(reac_id)
                if "power" in reactant.attrib:
                    porder[reac_id] = reactant.attrib["power"]
                else:
                    porder[reac_id] = "1"
            elif reactant.tag == "forwardRate":
                # local_params.update({'kon':float(reactant.text)})
                reac_ord = [
                    r + "^" + rorder[r] if rorder[r] != "1" else r
                    for r in reactants
                ]

                total_rord = sum(int(rorder[r]) for r in rorder.keys()) - 1

                # print(reac_ord)

                kin_law = "{}*(kon_{}*{} )".format(
                    self.comp, reaction_num, "*".join(reac_ord)
                )  #'comp*(kon*E*S-koff*ES)'

                self.model.addParameter(
                    "kon_{}".format(reaction_num),
                    float(reactant.text),
                    units=self.units[total_rord].id,
                )

            elif reactant.tag == "reverseRate":
                # local_params.update({'koff':float(reactant.text)})
                prod_ord = [
                    r + "^" + porder[r] if r in porder[r] != "1" else r
                    for r in products
                ]

                total_pord = sum(int(porder[r]) for r in porder.keys()) - 1
                # print(prod_ord)
                kin_law = "{}*(kon_{}*{} - koff_{}*{})".format(
                    self.comp, reaction_num, "*".join(reac_ord), reaction_num, "*".join(prod_ord)
                )  #'comp*(kon*E*S-koff*ES)'

                self.model.addParameter(
                    "koff_{}".format(reaction_num),
                    float(reactant.text),
                    units=self.units[total_pord].id,
                )

        self.model.addReaction(
            reactants,
            products,
            kin_law,
            local_params=local_params,
            rxn_id="r{}".format(reaction_num),
        )
        return reaction_num

    def convert_to_nanomoles(self):
        ## Concentration in nanomolar
        for child in self.ic_root:
            if child.tag == "ConcentrationSet":
                for child2 in child:
                    self.conc_dict[child2.attrib["specieID"]] = float(
                        child2.attrib["value"]
                    )  # Nanomolarity to Molarity

    def create_model(self):
        # Create SBML model from the NeuroRD model
        self.model = simplesbml.SbmlModel(sub_units="nM", time_units="ms", extent_units="nM")

        # simplesbml creates a default compartment
        # rather than add a new one; let's adapt that one for our use case
        size = self.size_micron_cubed * self.micron_cube_to_litre  
        compartment = self.model.model.compartments[0]
        compartment.id = self.comp
        compartment.size = size

    def add_unit_definitions(self):
        """
        Function to add the required unit definitions to the model.
        """
        ## ms
        ms = self.model.model.createUnitDefinition()
        ms.setId("ms")
        unit = ms.createUnit()
        unit.setKind(libsbml.UNIT_KIND_SECOND)
        unit.setScale(-3)
        unit.setExponent(1)
        unit.setMultiplier(1)

        ## nM
        nM = self.model.model.createUnitDefinition()
        nM.setId("nM")
        unit = nM.createUnit()
        unit.setKind(libsbml.UNIT_KIND_MOLE)
        unit.setScale(-9)
        unit.setExponent(1)
        unit.setMultiplier(1)

        ## ms^{-1}
        per_ms = self.model.model.createUnitDefinition()
        per_ms.setId("per_ms")
        unit = per_ms.createUnit()
        unit.setKind(libsbml.UNIT_KIND_SECOND)
        unit.setScale(-3)
        unit.setExponent(-1)
        unit.setMultiplier(1)

        ## l nM^{-1} ms^{-1}
        l_per_nM_per_ms = self.model.model.createUnitDefinition()
        l_per_nM_per_ms.setId("l_per_nM_per_ms")
        unit = l_per_nM_per_ms.createUnit()
        unit.setKind(libsbml.UNIT_KIND_LITRE)
        unit.setScale(0)
        unit.setExponent(1)
        unit.setMultiplier(1)

        unit = l_per_nM_per_ms.createUnit()
        unit.setKind(libsbml.UNIT_KIND_MOLE)
        unit.setScale(-9)
        unit.setExponent(-1)
        unit.setMultiplier(1)

        unit = l_per_nM_per_ms.createUnit()
        unit.setKind(libsbml.UNIT_KIND_SECOND)
        unit.setScale(-3)
        unit.setExponent(-1)
        unit.setMultiplier(1)

        ## nM^{-2} ms^{-1}
        per_nM2_per_ms = self.model.model.createUnitDefinition()
        per_nM2_per_ms.setId("per_nM2_per_ms")
        unit = per_nM2_per_ms.createUnit()
        unit.setKind(libsbml.UNIT_KIND_MOLE)
        unit.setScale(-9)
        unit.setExponent(-2)
        unit.setMultiplier(1)

        unit = per_nM2_per_ms.createUnit()
        unit.setKind(libsbml.UNIT_KIND_SECOND)
        unit.setScale(-3)
        unit.setExponent(-1)
        unit.setMultiplier(1)

        ## nM^{-3} ms^{-1}
        per_nM3_per_ms = self.model.model.createUnitDefinition()
        per_nM3_per_ms.setId("per_nM3_per_ms")
        unit = per_nM3_per_ms.createUnit()
        unit.setKind(libsbml.UNIT_KIND_MOLE)
        unit.setScale(-9)
        unit.setExponent(-3)
        unit.setMultiplier(1)

        unit = per_nM3_per_ms.createUnit()
        unit.setKind(libsbml.UNIT_KIND_SECOND)
        unit.setScale(-3)
        unit.setExponent(-1)
        unit.setMultiplier(1)

        ## nM^{-4} ms^{-1}
        per_nM4_per_ms = self.model.model.createUnitDefinition()
        per_nM4_per_ms.setId("per_nM4_per_ms")
        unit = per_nM4_per_ms.createUnit()
        unit.setKind(libsbml.UNIT_KIND_MOLE)
        unit.setScale(-9)
        unit.setExponent(-3)
        unit.setMultiplier(1)

        unit = per_nM4_per_ms.createUnit()
        unit.setKind(libsbml.UNIT_KIND_SECOND)
        unit.setScale(-3)
        unit.setExponent(-1)
        unit.setMultiplier(1)

        self.units = {
            0: per_ms,
            1: l_per_nM_per_ms,
            2: per_nM2_per_ms,
            3: per_nM3_per_ms,
            4: per_nM4_per_ms,
        }
