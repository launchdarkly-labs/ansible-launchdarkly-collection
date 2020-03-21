package launchdarkly_base

has_tag(resource, tag) {
	contains(resource.tags, tag)
}

has_variation(resource, variation) {
    #some i
    resource.variations[_].value = variation
    #contains(resource.variations.value, variation)
}

name_endswith(resource, match) {
    endswith(resource.name, match)
}

name_startswith(resource, match) {
    startswith(resource.name, match)
}

contains(arr, elem) {
  arr[_] = elem
}
