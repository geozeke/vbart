#!/bin/sh
set -eu

usage() {
  echo "Usage: $0 <tag> <output-file>"
  echo "  Example: $0 v0.3.0 .release-notes.md"
  echo "  Example: $0 v0.4.0-beta.1 .release-notes.md"
  exit 1
}

if [ "$#" -ne 2 ]; then
  usage
fi

tag="$1"
output_file="$2"

case "$tag" in
  v*) version="${tag#v}" ;;
  *)
    echo "Error: tag must start with 'v' followed by a version." >&2
    exit 1
    ;;
esac

if [ -z "$version" ]; then
  echo "Error: tag must start with 'v' followed by a version." >&2
  exit 1
fi

script_dir="$(cd "$(dirname "$0")" && pwd)"
project_root="$(dirname "$script_dir")"
changelog="$project_root/CHANGELOG.md"
major="${version%%.*}"
minor_patch="${version#*.}"
minor="${minor_patch%%.*}"
archive_changelog="$project_root/changelogs/v$major.$minor.x.md"

if [ ! -f "$changelog" ]; then
  echo "Error: CHANGELOG.md not found." >&2
  exit 1
fi

tmp_file="$(mktemp)"
cleanup() {
  rm -f "$tmp_file"
}
trap cleanup EXIT

extract_notes() {
  input_file="$1"

  awk -v version="$version" '
  BEGIN {
    in_section = 0
    found = 0
  }

  /^## / {
    if (in_section) {
      exit
    }
    if ($0 ~ "^## v?" version "([[:space:]]|$)") {
      in_section = 1
      found = 1
    }
  }

  in_section {
    print
  }

  END {
    if (!found) {
      exit 2
    }
  }
  ' "$input_file"
}

extract_notes "$changelog" > "$tmp_file" || {
  status=$?
  if [ "$status" -ne 2 ]; then
    exit "$status"
  fi
  if [ -f "$archive_changelog" ]; then
    extract_notes "$archive_changelog" > "$tmp_file" || {
      archive_status=$?
      if [ "$archive_status" -eq 2 ]; then
        echo "Error: release notes for '$tag' not found in CHANGELOG.md or $archive_changelog." >&2
      fi
      exit "$archive_status"
    }
  else
    echo "Error: release notes for '$tag' not found in CHANGELOG.md or $archive_changelog." >&2
    exit "$status"
  fi
}

if [ ! -s "$tmp_file" ]; then
  echo "Error: release notes for '$tag' are empty." >&2
  exit 1
fi

mkdir -p "$(dirname "$output_file")"
mv "$tmp_file" "$output_file"
trap - EXIT
