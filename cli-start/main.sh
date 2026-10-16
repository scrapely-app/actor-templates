#!/bin/bash
set -ex

# Parse input values
input="$(scrapely actor get-input)"
name="$(jq -r .name <<< "$input")"

# Construct an output object and push it to the dataset (Actor results)
echo '{}' |
    jq ".name = \"$name\"" |
    jq ".greeting = \"Hello $name!\"" |
    scrapely actor push-data
