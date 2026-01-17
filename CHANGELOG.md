# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-01-17

### Added

- Initial release of Tado Hijack integration
- **API Quota Monitoring**: Real-time tracking of Tado API rate limits via passive header interception
- **Presence Control**: Home/Away switch with intelligent debouncing
- **Zone Auto Mode**: Per-zone switches to toggle between smart schedule and manual override
- **Battery Monitoring**: Binary sensors for device battery health
- **Dual-Track Polling**: Configurable fast (hourly) and slow (daily) polling intervals
- **Sequential API Worker**: Background queue prevents API flooding
- **Monkey-patching**: Fixes `nextTimeBlock: null` deserialization bug in tadoasync library
- **Services**: `manual_poll` and `resume_all_schedules` for automation integration
- **Translations**: English and German language support
- **OAuth Device Flow**: Secure authentication without storing credentials
