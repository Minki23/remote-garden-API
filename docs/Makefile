SOURCEDIR = source

BUILDDIR = _build

help:
	@echo "Please use 'make <target>' where <target> is one of"
	@echo "  html      to build the HTML documentation"
	@echo "  latexpdf  to build LaTeX PDF documentation"

html:
	sphinx-build -b html $(SOURCEDIR) $(BUILDDIR)/html

latexpdf:
	sphinx-build -b latex $(SOURCEDIR) $(BUILDDIR)/latex
	cd $(BUILDDIR)/latex && make
