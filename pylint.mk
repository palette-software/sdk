PYLINT_DISABLED_WARNINGS := star-args,locally-disabled,locally-enabled,too-few-public-methods
PYLINT_GOOD_NAMES := "_,ex"
PYLINT_OPTS := -rn -d $(PYLINT_DISABLED_WARNINGS) --good-names=$(PYLINT_GOOD_NAMES)
PYLINT := pylint $(PYLINT_OPTS)
