import os
import time

import libsbml


# Validation
class validateSBML:
    def __init__(self, ucheck, silent):
        # the sbml reader
        self.reader = libsbml.SBMLReader()

        # variable set by the class
        self.ucheck = ucheck
        self.silent = silent

        # variables passed as arguments
        self.file = None

        # variables calculated
        self.numinvalid = 0
        self.time_read = 0.0

        # variables used in validation
        self.skipCC = False
        self.timeCC = 0.0
        self._numReadErr = 0
        self._numReadWarn = 0
        self._errMsgRead = ""
        self._numCCErr = 0
        self._numCCWarn = 0
        self._errMsgCC = ""

    def validate_file(self, file):
        """
        Function to validate an sbml file
        :param file: the file name to validate
        :return: none
        """
        if not os.path.exists(file):
            if not self.silent:
                print("[Error] %s : No such file." % file)
            self.numinvalid += 1
            return

        self.file = file
        start = time.time()
        sbml_document = libsbml.readSBML(file)
        stop = time.time()
        self.time_read = (stop - start) * 1000

        return self.validate_sbml_document(sbml_document)

    def print_results(self):
        """
        Function to print the results of validation
        :return:
        """
        if not self.silent:
            print("                 filename : %s" % self.file)
            print("         file size (byte) : %d" % (os.path.getsize(self.file)))
            print("           read time (ms) : %f" % self.time_read)

            if not self.skipCC:
                print("        c-check time (ms) : %f" % self.timeCC)
            else:
                print("        c-check time (ms) : skipped")

            print("      validation error(s) : %d" % (self._numReadErr + self._numCCErr))
            if not self.skipCC:
                print("    (consistency error(s)): %d" % self._numCCErr)
            else:
                print("    (consistency error(s)): skipped")

            print("    validation warning(s) : %d" % (self._numReadWarn + self._numCCWarn))
            if not self.skipCC:
                print("  (consistency warning(s)): %d" % self._numCCWarn)
            else:
                print("  (consistency warning(s)): skipped")

            if self._errMsgRead or self._errMsgCC:
                print()
                print("===== validation error/warning messages =====\n")
                if self._errMsgRead:
                    print(self._errMsgRead)
                if self._errMsgCC:
                    print("*** consistency check ***\n")
                    print(self._errMsgCC)

    def validate_model(self, document):
        return self.validate_sbml_document(document)

    def validate_sbml_document(self, sbml_document):
        errors = sbml_document.getNumErrors()

        seriousErrors = False

        if errors > 0:
            for i in range(errors):
                severity = sbml_document.getError(i).getSeverity()
                if (severity == libsbml.LIBSBML_SEV_ERROR) or (
                        severity == libsbml.LIBSBML_SEV_FATAL
                ):
                    seriousErrors = True
                    self._numReadErr += 1
                else:
                    self._numReadWarn += 1

                self._errMsgRead = sbml_document.getErrorLog().toString()

        # If serious errors are encountered while reading an SBML document, it
        # does not make sense to go on and do full consistency checking because
        # the model may be nonsense in the first place.

        if seriousErrors:
            self.skipCC = True
            self._errMsgRead += "Further consistency checking and validation aborted."
            self.numinvalid += 1
        else:
            sbml_document.setConsistencyChecks(
                libsbml.LIBSBML_CAT_UNITS_CONSISTENCY, self.ucheck
            )
            start = time.time()
            failures = sbml_document.checkConsistency()
            stop = time.time()
            self.timeCC = (stop - start) * 1000

            if failures > 0:
                isinvalid = False
                for i in range(failures):
                    severity = sbml_document.getError(i).getSeverity()
                    if (severity == libsbml.LIBSBML_SEV_ERROR) or (
                            severity == libsbml.LIBSBML_SEV_FATAL
                    ):
                        self._numCCErr += 1
                        isinvalid = True
                    else:
                        self._numCCWarn += 1

                if isinvalid:
                    self.numinvalid += 1

                self._errMsgCC = sbml_document.getErrorLog().toString()

        return self._numCCErr + self._numCCWarn + self._numReadErr + self._numReadWarn

