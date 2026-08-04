# Khalorg

[Click here for the GitHub page.](https://github.com/BartSte/khalorg)

<img src="./demo/logo.jpg" width=50%>

## Demo

The demo below demonstrates the following features using the neovim plugin
called [nvim-khalorg](https://github.com/BartSte/nvim-khalorg):

- `khalorg new`: convert an org agenda item into a `khal` agenda item.
- `khalorg list`: convert a `khal` agenda item into an org agenda item.
- `khalorg edit`: edit an existing `khal` agenda item with org mode.
- `khalorg delete`: delete an existing `khal` item.

![neovim-plugin](https://github.com/BartSte/khalorg/blob/main/demo/neovim-plugin.gif?raw=true)

## Contents

<!--toc:start-->

- [Demo](#demo)
- [Contents](#contents)
- [Introduction](#introduction)
  - [Definitions](#definitions)
  - [Motivation](#motivation)
  - [Features](#features)
- [Installation](#installation)
  - [PyPi](#pypi)
  - [From source](#from-source)
  - [For development](#for-development)
- [Usage](#usage)
  - [List: from khal to org](#list-from-khal-to-org)
    - [Custom output format](#custom-output-format)
    - [Recurring events from khal](#recurring-events-from-khal)
  - [Sync: bidirectional](#sync-bidirectional)
    - [Sync options](#sync-options)
  - [New: from org to khal](#new-from-org-to-khal)
    - [Creating recurring events](#creating-recurring-events)
    - [Attendees](#attendees)
  - [Edit: from org to khal](#edit-from-org-to-khal)
  - [Delete: from org to khal](#delete-from-org-to-khal)
    - [Deleting recurring events](#deleting-recurring-events)
- [Neovim plugin](#neovim-plugin)
- [Workflow for Office 365](#workflow-for-office-365)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)
- [Improvements:](#improvements)

<!--toc:end-->

## Introduction

`khalorg` is an interface between Org mode and Khal cli calendar.

### Definitions

- [CalDav](https://en.wikipedia.org/wiki/CalDAV): internet standard for client access to calendars
- [Davmail](https://davmail.sourceforge.net/e): CalDav exchange gateway
- [khal](https://github.com/pimutils/khal): command line calendar app
- [khalel](https://gitlab.com/hperrey/khalel): interface between emacs and khal
- [nvim-orgmode](https://github.com/nvim-orgmode/orgmode): org mode for neovim
- [org](https://orgmode.org): plain text system for keeping notes, agendas and more
- [vdirsyncer](https://github.com/pimutils/vdirsyncer): synchronizes calendars and addressbooks between servers and the local file system

### Motivation

I use org mode to manage my agenda and my notes. However, in a professional
setting, you are often required to use proprietary software for your agenda,
like Office 365. Luckily, programs exist that can synchronize agendas from
different sources, by implementing the CalDav standard. Personally, I like to
use `vdirsyncer` with `khal` to synchronize my agendas. To bridge the gap
between `khal` and `org mode`, only 1 program exists called: `khalel`. However,
this program is designed for `emacs`. Since there are also org mode users
outside of `emacs` (e.g. `neovim`), `khalorg` aims to be a general interface
between `vdirsyncer`/`khal` and `org mode`.

Based on the above, the following workflow is desired:

```example
┌──────┐
│CalDav│
└┬─────┘
┌▽─────────┐
│vdirsyncer│
└┬─────────┘
┌▽───┐
│khal│
└┬───┘
┌▽───────┐
│khalorg │
└┬───────┘
┌▽───────┐
│org mode│
└────────┘
```

### Features

- [x] Can be used by org mode for emacs, vim and neovim.
- [x] Vdirsyncer calendars can be manipulated by using the cli of `khal`
      as the interface.
- [x] `khalorg new`: convert an org agenda item into a `khal` agenda
      item.
- [x] `khalorg list`: convert a `khal` agenda item into an org agenda
      item.
- [x] `khalorg edit`: edit an existing `khal` agenda item with org mode.
- [x] `khalorg delete`: delete an existing `khal` item.
- [x] `khalorg sync`: synchronize events between a `khal` calendar and an org
      file.
- [x] Recurring items are supported by providing an org repeater in the
      time stamp (e.g., `+1w`). The following is supported:
  - `khalorg new` supports `+1d`, `+1w`, `+1m`, and `+1y`.
  - `khalorg new` and `khalorg edit --edit-dates` support one timestamp per
    org agenda item.
  - `khalorg list` concatenates timestamps that cannot be describes by
    an org repeater, resulting in an org agenda item with multiple
    timestamps.
  - Supports an `until` date for recurring items. The until date can be
    supplied through an org property `UNTIL`.
- [x] Has unittests
- [x] Includes an Office 365 workflow with a bash script
- [x] Semantic versioning
- [x] Gifs with demos
- [x] Neovim plugin
- [x] Is available on PyPI

## Installation

For safety, always make a back-up of your calendar before installing software
that is new to you.

Make sure your `khal` date format is compatible with org, otherwise it
will not work. When running `khal printformats` you should get:

```example
longdatetimeformat: 2013-12-21 Sat 21:45
datetimeformat: 2013-12-21 Sat 21:45
longdateformat: 2013-12-21 Sat
dateformat: 2013-12-21 Sat
timeformat: 21:45
```

If not, you can try setting the snippet below in your khal configuration, which uses python's [`time.strftime` format](https://docs.python.org/3/library/time.html#time.strftime).

```ini
[locale]
longdatetimeformat=%Y-%m-%d %a %H:%M
datetimeformat=%Y-%m-%d %a %H:%M
longdateformat=%Y-%m-%d %a
dateformat=%Y-%m-%d %a
timeformat=%H:%M
```

### PyPi

Install by running the following command:

```bash
pip install khalorg
```

### From source

Set your current working directory to the root directory, i.e, the
directory containing the `pyproject.toml` file. Next, run:

```bash
pip install .
```

After this, the executable `khalorg` will be available.

### For development

If you want to develop the code, debug it, and test it, run:

```bash
uv sync
```

## Usage

Use `khalorg --help` to get information about the cli of `khalorg`. The
following section discuss the `khalorg` commands that are available.

### List: from khal to org

![khalorg list demo](https://github.com/BartSte/khalorg/blob/main/demo/list.gif?raw=true)

Agenda items from `khal` can be converted to org items using the
`khalorg list` command. For examples:

```bash
khalorg list my_calendar today 90d > my_calendar.org
```

Here, the `khal` agenda items of the calendar `my_calendar` are
converted to org format and written to a file called `my_calendar.org`.
The range is specified from `today` till `90d` (90 days) in the future.
For more information about the allowed date formats, check the
`khal list` command, which is used for this functionality. It is assumed
that the `khal` calendar called `my_calendar` exists. Make sure
`my_calendar` is a calendar that exists on your local file system.

#### Custom output format

If `khalorg list --format` is not defined, the default template from
[`src/khalorg/static/khalorg_format.txt`](./src/khalorg/static/khalorg_format.txt)
is used. Pass a custom template with `--format`, or save one at
`$HOME/.config/khalorg/khalorg_format.txt` to use it by default.

```org
* {title}
  {timestamps}
  :PROPERTIES:
  :ATTENDEES: {attendees}
  :CALENDAR: {calendar}
  :CATEGORIES: {categories}
  :LOCATION: {location}
  :ORGANIZER: {organizer}
  :STATUS: {status}
  :UID: {uid}
  :URL: {url}
  :UNTIL: {until_rrule}
  :END:
  {description}
```

The following keys are supported:

- `{attendees}`: a comma separated list of email addresses of attendees
- `{calendar}`: the name of the khal calendar
- `{categories}`: the categories property of the item
- `{description}`: the description of the item
- `{location}`: the location of the item
- `{organizer}`: the email of the organizer
- `{status}`: the status of the item, e.g., TENTATIVE or ACCEPTED
- `{timestamps}`: the timestamp of the item
- `{title}`: the summary of the item
- `{uid}`: the UID of the item
- `{until_rrule}`: the until value from the RRULE
- `{url}`: the url property

The following keys are supported but are typically reserved for internal use
and are therefore less informative:

- `{until}`: the until property value. Is empty when using `khalorg list`.
- `{rrule}`: the ICal RRULE of the item.

#### Recurring events from khal

The `khalorg list` command relies on the `khal list` command. Using this
command the `RRULE` of each item is retrieved to create the correct org
repeater. Only simple org repeaters are supported that have the
following form: `+[number][h,d,w,m,y]`. Complex `RRULEs` are described by
concatenating the corresponding timestamps within one agenda item,
resulting in a list of items. For example, the agenda item below
represents a weekly recurring event where the first meeting was moved to
another date, resulting in a timestamp without a repeater, and one with
a repeater.

```org
* Meeting
  <2023-01-05 Thu 01:00-02:00>
  <2023-01-08 Sun 01:00-02:00 +1w>
  :PROPERTIES:
  :UID: 123
  :LOCATION: Somewhere
  :ORGANIZER: Someone (someone@outlook.com)
  :ATTENDEES: test@test.com, test2@test.com
  :URL: www.test.com
  :END:
  Hello,

  Lets have a meeting.

  Regards,


  Someone
```

### Sync: bidirectional

`khalorg sync` synchronizes new and changed events between a `khal` calendar
and an org file:

```bash
khalorg sync my_calendar my_calendar.org
```

Events are matched by UID. The default range is from `today` through `90d`.
Sync state is stored in
`$HOME/.local/share/khalorg/<calendar>.org`; keep this file between runs so
that changes and conflicts can be detected. If the org file does not exist,
it is created from the selected `khal` calendar.

When an event changed in both sources since the previous sync, `khal` wins by
default. Deletions are not propagated unless `--delete-on-sync` is passed.

#### Sync options

- `--start` and `--stop` set the synchronized date range.
- `--conflict-resolution khal|org` selects which source wins a conflict.
- `--edit-dates` allows org changes to update event dates and recurrence.
- `--delete-on-sync` propagates deletions between both sources. Back up both
  sources and test with `--dry-run` before enabling it.
- `--dry-run` logs planned actions without changing either source or the sync
  state.
- `--state-dir` changes where synchronization state is stored.
- `--filetags TAG` adds a file tag to generated org files and can be repeated.
- `--format` uses the same output templates as `khalorg list`.

### New: from org to khal

![khalorg new demo](https://github.com/BartSte/khalorg/blob/main/demo/new.gif?raw=true)

An org agenda item can be converted to a new `khal` agenda item by
feeding the org item through stdin to `khalorg new` and specifying the
khal calendar name as a positional argument. For example, the consider
the org item below, which is saved as `meeting.org`.

```org
* Meeting
  <2023-01-01 Sun 01:00-02:00 +1w>
  :PROPERTIES:
  :UID: 123
  :LOCATION: Somewhere
  :ORGANIZER: Someone (someone@outlook.com)
  :ATTENDEES: test@test.com, test2@test.com
  :URL: www.test.com
  :END:
  Hello,

  Lets have a meeting.

  Regards,


  Someone
```

This item can be converted to the `khal` calendar called
"my<sub>calendar</sub>" as follows:

```bash
cat meeting.org | khalorg new my_calendar
```

It is assumed that the `khal` calendar called "my<sub>calendar</sub>"
exists. Make sure "my<sub>calendar</sub>" is a calendar that exists on
your local file system.

#### Creating recurring events

Only one timestamp per org item is supported. `khalorg new` accepts the
repeaters `+1d`, `+1w`, `+1m`, and `+1y`. These events repeat forever unless
you specify an end date using the `UNTIL` property in the org file.

Personally, when I need to create a complex repeat pattern (or when I
need outlook specific items like a Teams invite), I create the event in
outlook first. Next, I use `khalorg edit` to change the fields that need
editing (e.g., the description).

#### Attendees

Optionally, attendees can be added to the `ATTENDEES` property field.
The attendees will be added to the `Attendees` field of `khal`. Once you
synchronize `khal` with a server (e.g., outlook) an invitation will be
send to the attendees.

### Edit: from org to khal

![khalorg edit demo](https://github.com/BartSte/khalorg/blob/main/demo/edit.gif?raw=true)

Existing `khal` events can be updated by feeding an org file with the
corresponding UID through stdin to the `khalorg edit` command. For
example, the org agenda item of <span class="spurious-link"
target="New">_New_</span> can be altered and used as an input for
`khalorg edit`, as long as the UID remains untouched.

```org
* Edited meeting
  <2023-01-01 Sun 01:00-02:00 +1w>
  :PROPERTIES:
  :UID: 123
  :ORGANIZER: Someone (someone@outlook.com)
  :ATTENDEES: other@test.com
  :END:
  Hello,

  I edited the meeting by removing the location and url. I also changed the
  title and the attendees field.

  Regards,


  Someone
```

Next, run the following command:

```bash
cat meeting.org | khalorg edit my_calendar
```

When using `khalorg edit` please consider the following:

- Editing an existing event is different from creating a new one as the
  original `icalendar` file is retained. Only parts of it are altered.
  This is convenient when the icalendar file contains information that
  cannot be generated by `khalorg`. For example, a Microsoft Team
  meeting.
- Only the PROTO event is edited, i.e., the whole series is altered not
  only the occurrence.
- `khalorg edit` will only update the dates and recurrence if the
  `--edit-dates` flag is passed. This avoids editing the start-stop date
  when editing an event that contains multiple timestamps (which are not
  supported).

### Delete: from org to khal

![khalorg deleted demo](https://github.com/BartSte/khalorg/blob/main/demo/delete.gif?raw=true)

An event can be deleted from a khal calendar by feeding an org file to the
`khalorg delete` command through stdin. The org file must contain an agenda
item with a non-empty UID property. For example, the khal event that was
created using the <span class="spurious-link" target="New">_New_</span> command
above can be removed by feeding the same file to `khalorg delete`:

```bash
cat meeting.org | khalorg delete my_calendar
```

#### Deleting recurring events

When deleting recurring items the whole series will be removed. Removing
occurrences is not supported.

## Neovim plugin

The neovim plugin can be found here:
[nvim-khalorg](https://github.com/BartSte/nvim-khalorg). Check out the demo at
the top of the [page](#demo).

## Workflow for Office 365

The diagram below illustrates the workflow than can be achieved when using
`khalorg`. The folder `extras`, on the
[GitHub](https://github.com/BartSte/khalorg) page, contains a `bash` script
called `calsync`, that synchronizes `vdirsyncer` calendars and exports them as
an org file using the `khalorg list` command. Davmail is used as the CalDav
server in this specific example.

```example
┌──────────┐
│Office 365│
└┬─────────┘
┌▽──────┐
│Davmail│
└┬──────┘
┌▽─────────┐
│vdirsyncer│
└┬─────────┘
┌▽───┐
│khal│
└┬───┘
┌▽───────┐
│khalorg │
└┬───────┘
┌▽───────┐
│org mode│
└────────┘
```

## Troubleshooting

If you encounter any issues, please report them on the issue tracker at:
[khalorg issues](https://github.com/BartSte/khalorg/issues)

## Contributing

Contributions are welcome! Please see [CONTRIBUTING](./CONTRIBUTING.md) for
more information.

## License

Distributed under the [MIT License](./LICENSE).

## Improvements:

- [ ] Timezones are not yet supported, so `khalorg` will only work when
      you agenda remain in the timezone that you specified within your
      `khal` config.
- [ ] Running khal commands directly from a script in not
      straightforward. Therefore, khal is executed as a subprocess, by using
      its command line interface.
- [ ] `khalorg new` and `khalorg edit` only support one timestamp per item.
      However, it is desired that all timestamps within 1 org agenda item,
      end up in 1 khal event, as is the case for the `orgagenda`. To achieve
      this the following could be build:
  - [ ] When multiple timestamps without an org repeater are provided,
        find the `RRULE` that describes them. Also, set the `UNTIL` date to
        the last date. If no `RRULE` can be found, raise an error. Another
        option could be to use the `RDATE` option of ICal.
  - [ ] When multiple timestamps with an org repeater are presented, try
        to find the `RRULE` that describes them.
