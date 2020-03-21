package launchdarkly
import data.launchdarkly_base
# Resource map to LaunchDarkly Ansible modules

deny[msg] {
	count(input.tags) < 1
	msg := "Need at least one tag"
}

deny[msg] {
	not launchdarkly_base.name_startswith(input, "test")
	msg := "Flag names should start with test"
}
