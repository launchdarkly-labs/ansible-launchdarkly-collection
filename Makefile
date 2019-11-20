# To update docs to point to a new api_client_python version, copy current to old. Update current.
# Run "make update_api_version_docs"
current_api_doc_version := 2.0.24
old_api_doc_version := 2.0.21


current_galaxy_version := 0.1.14
old_galaxy_version := 0.1.12


.PHONY: update_api_version_docs
update_api_version_docs:
	find . -name "*.py" -type f -print0 | xargs -0 sed -i 's/$(old_api_doc_version)/$(current_api_doc_version)/g'

.PHONY: build_docs
build_docs:
	bash scripts/sphinx-gh-pages.sh

.PHONY: update_galaxy_version
update_galaxy_version:
	sed -i 's/version: $(old_galaxy_version)/version: $(current_galaxy_version)/g' galaxy.yml
	sed -i 's/$(old_galaxy_version)/$(current_galaxy_version)/g' docs/source/conf.py
