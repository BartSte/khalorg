# Changelog - Khalorg
This document describes the changes that were made to the software for each
version. The changes are described concisely, to make it comprehensible for the
user. A change is always categorized based on the following types:
- Bug: a fault in the software is fixed.
- Feature: a functionality is added to the program.
- Improvement: a functionality in the software is improved.
- Task: a change is made to the repository that has no effect on the source
code.

# 0.0.0

## Feature
- `khalorg new` is added. It converts an org agenda item into a `khal` agenda
item.
- `khalorg list` is added. It converts a `khal` agenda item into an org agenda
item.
- `khalorg edit` is added. It edits an existing `khal` agenda item with org
mode.
- `khalorg delete` is added. It deletes an existing `khal` item.
- Recurring items are supported by providing an org repeater in the
time stamp (e.g., `+1w`). The following is supported:
  - the follow org repeaters: `+{integer}{d,w,m,y}`
  - `khalorg new` and `khalorg edit --edit-dates` support 1 time stamp
  per org agenda item.
  - `khalorg list` concatenates timestamps that cannot be describes by
  an org repeater, resulting in an org agenda item with multiple
  timestamps.
  - Supports an `until` date for recurring items. The until date can be
  supplied through an org property `UNTIL`.

## Task
- An Office 365 workflow with a [bash script](./extras/calsync) is added which
synchronizes all ~vdirsyncer~ calendars and exports them to org with ~khalorg~.
Davmail is used as the CalDav server. 
