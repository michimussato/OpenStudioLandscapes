#!/usr/bin/env bash

# THIS IS A CONCEPT
# Todo:
#  - [ ] Python implementation

# Be sure to be on the feature branch (not main)
# Example
# ISSUE="https://github.com/michimussato/OpenStudioLandscapes/issues/34" bash ./utils/create_batch_pr.sh


if [ -z ${ISSUE+x} ];
  then
    echo "Var ISSUE is not set"
    exit 1
fi


declare -a PULL_REQUESTS


CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
# --template vs --body-file
# https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/creating-a-pull-request-template-for-your-repository
# TEMPLATE="/home/michael/git/repos/OpenStudioLandscapes/media/git/pr_template.md"
#BODY_FILE="/home/michael/git/repos/OpenStudioLandscapes/media/git/pr_template.md"
#BODY_STRING=$(cat "${BODY_FILE}")
SUBSTITUTE_FROM="[]"
SUBSTITUTE_TO=""


# Checkboxes:
# https://gist.github.com/TheMatt2/1360af52468714370c753cfa2fe50783
# https://stackoverflow.com/a/60687493/2207196
# https://www.toptal.com/designers/htmlarrows/symbols/
# Box:      &#x2610;
# Checked:  &#x2611;
# Crossed:  &#x2612;


## Open web
#gh PR create \
#    --head="${CURRENT_BRANCH}" \
#    --base="main" \
#    --title="${CURRENT_BRANCH//${SUBSTITUTE_FROM}/${SUBSTITUTE_TO}}" \
#    --assignee="@me" \
#    --web \
#    --body="${BODY_STRING}" \
##    --body-file="${BODY_FILE}" \
##    --template="${TEMPLATE}" \


pushd () {
    command pushd "$@" > /dev/null || exit 1
}

popd () {
    command popd > /dev/null || exit 1
}


function create_pr() {
  # Returns:
  #   Web URL of the created PR
  working_directory="${1}"
  body_string="${2}"
#  args="${*}"
  # or pure CLI
  # formatting:
  #  https://cli.github.com/manual/gh_help_formatting
  pushd "${working_directory}" || exit 1
  RESULT=$(gh pr create \
      --head="${CURRENT_BRANCH}" \
      --base="main" \
      --title="${CURRENT_BRANCH//${SUBSTITUTE_FROM}/${SUBSTITUTE_TO}}" \
      --assignee="@me" \
      --draft \
      --body="${body_string}" \
      --dry-run \
#      ${args}
#      --body-file="${BODY_FILE}" \
  #    --template="${TEMPLATE}" \
  )

  popd || exit 1

  echo "${RESULT}"
}


function iterate_features() {
  pushd ~/git/repos/OpenStudioLandscapes || exit 1
  for d in ./.features/*
  do
    echo "pwd = $(pwd)"
    result="$(create_pr "${d}" "Links ${ISSUE}")"
    echo "result = ${result}"
    PULL_REQUESTS+=("${result}")
  done
  popd || exit 1

#  for PR in "${PULL_REQUESTS[@]}"
#  do
#    echo "${PR}"
#  done
#  popd || exit 1
##  return "${PULL_REQUESTS[@]}"
}


iterate_features
#pull_requests=$(iterate_features)

md=$(echo -e "Implements [${ISSUE}](${ISSUE})")
md+="\n\n"
md+="---\n"
md+="\n"
md+="Current Work in Progress:\n"
md+="\n"
#  md+="| Repository | PR Created | PR Status | Link |\n"
md+="| PR Created | Link |\n"
md+="| ---------- | ---- |\n"

for PR in "${PULL_REQUESTS[@]}"
do
#  echo "PR = ${PR}"
  md+="| &#x2611; | ${PR} |\n"
done

result_main="$(create_pr "$(pwd)" "${md}")"

echo "${result_main}"

unset ISSUE
