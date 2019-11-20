# To update docs to point to a new api_client_python version, copy current to old. Update current.
# Run "make update_api_version_docs"
current_api_doc_version := 2.0.24
old_api_doc_version := 2.0.21
.PHONY: update_api_version_docs
update_api_version_docs:
	find . -name "*.py" -type f -print0 | xargs -0 sed -i 's/$(old_api_doc_version)/$(current_api_doc_version)/g'
