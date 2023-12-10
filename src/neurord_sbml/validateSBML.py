import os
import time

import libsbml


# Validation
class validateSBML:
    def __init__(self, ucheck, silent):
        self.reader = libsbml.SBMLReader()
        self.ucheck = ucheck
        self.silent = silent
        self.numinvalid = 0

    def validate(self, file):
        if not os.path.exists(file):
            if not self.silent:
                print("[Error] %s : No such file." % file)
            self.numinvalid += 1
            return

        start = time.time()
        sbmlDoc = libsbml.readSBML(file)
        stop = time.time()
        timeRead = (stop - start) * 1000
        errors = sbmlDoc.getNumErrors()

        seriousErrors = False

        numReadErr = 0
        numReadWarn = 0
        errMsgRead = ""

        if errors > 0:
            for i in range(errors):
                severity = sbmlDoc.getError(i).getSeverity()
                if (severity == libsbml.LIBSBML_SEV_ERROR) or (
                        severity == libsbml.LIBSBML_SEV_FATAL
                ):
                    seriousErrors = True
                    numReadErr += 1
                else:
                    numReadWarn += 1

                errMsgRead = sbmlDoc.getErrorLog().toString()

        # If serious errors are encountered while reading an SBML document, it
        # does not make sense to go on and do full consistency checking because
        # the model may be nonsense in the first place.

        numCCErr = 0
        numCCWarn = 0
        errMsgCC = ""
        skipCC = False
        timeCC = 0.0

        if seriousErrors:
            skipCC = True
            errMsgRead += "Further consistency checking and validation aborted."
            self.numinvalid += 1
        else:
            sbmlDoc.setConsistencyChecks(
                libsbml.LIBSBML_CAT_UNITS_CONSISTENCY, self.ucheck
            )
            start = time.time()
            failures = sbmlDoc.checkConsistency()
            stop = time.time()
            timeCC = (stop - start) * 1000

            if failures > 0:
                isinvalid = False
                for i in range(failures):
                    severity = sbmlDoc.getError(i).getSeverity()
                    if (severity == libsbml.LIBSBML_SEV_ERROR) or (
                            severity == libsbml.LIBSBML_SEV_FATAL
                    ):
                        numCCErr += 1
                        isinvalid = True
                    else:
                        numCCWarn += 1

                if isinvalid:
                    self.numinvalid += 1

                errMsgCC = sbmlDoc.getErrorLog().toString()

        # print results
        #
        if not self.silent:
            print("                 filename : %s" % file)
            print("         file size (byte) : %d" % (os.path.getsize(file)))
            print("           read time (ms) : %f" % timeRead)

            if not skipCC:
                print("        c-check time (ms) : %f" % timeCC)
            else:
                print("        c-check time (ms) : skipped")

            print("      validation error(s) : %d" % (numReadErr + numCCErr))
            if not skipCC:
                print("    (consistency error(s)): %d" % numCCErr)
            else:
                print("    (consistency error(s)): skipped")

            print("    validation warning(s) : %d" % (numReadWarn + numCCWarn))
            if not skipCC:
                print("  (consistency warning(s)): %d" % numCCWarn)
            else:
                print("  (consistency warning(s)): skipped")

            if errMsgRead or errMsgCC:
                print()
                print("===== validation error/warning messages =====\n")
                if errMsgRead:
                    print(errMsgRead)
                if errMsgCC:
                    print("*** consistency check ***\n")
                    print(errMsgCC)
        return numCCErr + numCCWarn + numReadErr + numReadWarn
