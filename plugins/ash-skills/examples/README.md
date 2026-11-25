# Examples

Optional, macOS-specific. No skill depends on these: `standup --after` creates a missing note itself.

## Daily standup note

`create-standup-note.sh` creates the day's standup note (`YYYY/MM - Month/MM-DD-YY.md` inside the folder) from the standup template on weekdays. It does nothing at weekends and never overwrites an existing note.

```sh
./create-standup-note.sh "<vault>/10 - Meetings/Standup" "<vault>/00 - System/Templates/Standup Template.md"
```

Arguments can also come from `STANDUP_FOLDER` and `STANDUP_TEMPLATE`. An optional third argument (or `STANDUP_DATE`, `YYYY-MM-DD`) sets the date.

### Run it every weekday morning (launchd)

1. Copy `com.example.standup-note.plist` to `~/Library/LaunchAgents/` and replace the `/path/to/...` values with absolute paths.
2. Load it: `launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.example.standup-note.plist`
3. Remove it: `launchctl bootout gui/$(id -u)/com.example.standup-note`

It runs daily at 08:00; the script skips weekends. If the Mac was asleep at 08:00, launchd runs it on wake.
