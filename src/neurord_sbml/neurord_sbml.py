import argparse
import sys

from src.neurord_sbml.validateSBML import validateSBML
from src.neurord_sbml.convert import convert


def main(args):
    converter = convert(args)
    model = converter.do_conversion()

    # serialization
    if args.display_only:
        print(model.toSBML())
    else:
        with open(args.output_file, "w") as f:
            f.write(model.toSBML())

    if args.validate:
        if args.unit_validation:
            enableUnitCCheck = True
        else:
            enableUnitCCheck = False

        validator = validateSBML(enableUnitCCheck, silent=False)

        fnum = 0

        validator.validate_file(args.output_file)
        numinvalid = validator.numinvalid

        print(
            "---------------------------------------------------------------------------"
        )
        print(
            "Validated %d files, %d valid files, %d invalid files"
            % (fnum, fnum - numinvalid, numinvalid)
        )
        if not enableUnitCCheck:
            print("(Unit consistency checks skipped)")

        if numinvalid > 0:
            sys.exit(1)


def get_parser():
    ### Command line input parsing here. ###########
    parser = argparse.ArgumentParser(
        prog="python " + sys.argv[0],
        description="Combines NeuroRD files and units into an SBML file",
    )

    neurord_group = parser.add_argument_group("neuroRD files")
    neurord_group.add_argument(
        "-r", "--reactions-file", help="NeuroRD file with reactions.", default=""
    )
    neurord_group.add_argument(
        "-ic",
        "--initial-conditions-file",
        help="NeuroRD file with initial conditions for the model",
        default="",
    )

    sbml_group = parser.add_argument_group("Output")
    sbml_group.add_argument(
        "-d",
        "--display-only",
        help="Use to display SBML only",
        default=False,
        action="store_true",
    )
    sbml_group.add_argument(
        "-v",
        "--validate",
        help="Validate SBML file",
        default=False,
        action="store_true",
    )
    sbml_group.add_argument(
        "-u",
        "--unit-validation",
        help="Validate units",
        default=False,
        action="store_true",
    )
    sbml_group.add_argument(
        "-o", "--output-file", type=str, help="SBML file to output model"
    )

    return parser


if __name__ == "__main__":
    parser = get_parser()
    args = parser.parse_args()

    # if args.signature_file:
    #    with open (args.signature_file, 'r') as f:
    #        args.signatures.extend(f.read().splitlines())

    # if not args.cspace_files and not args.signatures:
    #    parser.error ('Either --files or --signatures is required.')
    main(args)
