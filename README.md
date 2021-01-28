# Juju Junebug

This a draft of a bug reporting tool for Juju

The eventual goal is to develop metrics to measure out general code
quality, and our responsiveness to the community and to internal
Canonical teams.

For now, it fetches some bugs, and captures stats to a simple .csv file.

Known issues with the draft:

1. The mechanism for determining bug age is sketchy. We need to figure
   out a better way of handling old bugs that were recently re-opened,
   or bumped in priority.

2. The stats captured are probably incomplete. We need to find the
   right balance between capturing historical data that will not
   necessarily persist in launchpad (e.g., the number of bugs in new
   state, day by day), and replicating the launchpad db locally.
3. The tool makes no attempt to de-depulicate multiple runs on the
   same day when printing reports (or unit is days, so we don't need
   to resolve to finer incrememnts).

## Usage

Check out this repo and run the following to fetch reports:

```
make report
```

Currently, you must be on an Ubuntu Desktop system for the above to
work, as we rely on launchpadlib being installed globally.

To play around and test things out, run:

```
make test
```

This will run a lighter weight script. You can affect its output by
hacking on fetch.test_report for now. (TODO: move testing stuff into a
nice module.)
