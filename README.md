# Tado Hijack for Home Assistant

[![semantic-release: conventional commits](https://img.shields.io/badge/semantic--release-conventionalcommits-e10079?logo=semantic-release)](https://github.com/semantic-release/semantic-release)
[![GitHub release (latest by date)](https://img.shields.io/github/v/release/banter240/tado_hijack)](https://github.com/banter240/tado_hijack/releases/latest)
[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
![GitHub all releases](https://img.shields.io/github/downloads/banter240/tado_hijack/total)
![GitHub](https://img.shields.io/github/license/banter240/tado_hijack)
![GitHub issues by-label](https://img.shields.io/github/issues/banter240/tado_hijack/bug?color=red)

An ultra-efficient, minimalist Home Assistant integration to monitor and control Tado heating systems. Designed for maximum API economy and real-time precision.

---

> 🏴‍☠️ **Why "Hijack"?**
> 1. **Header Hijack**: We use advanced monkey-patching to intercept Tado API headers in real-time, tracking your remaining API calls with zero additional network overhead.
> 2. **Feature Hijack**: HomeKit is great, but its standard integration is blind to Tado's most critical features. This integration "hijacks" Tado's 100-calls-per-day limit to pull exactly what is missing from HomeKit: **Battery health, Home/Away presence logic, and the full HVAC Auto control.** We bridge the gap where the official HomeKit support ends.

---

**Table of Contents**

- [About This Integration](#about-this-integration)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Supported Entities](#supported-entities)
- [Services](#services)
- [Troubleshooting](#troubleshooting)
- [Disclaimer](#disclaimer)
- [License](#license)

## About This Integration

Tado Hijack is an ultra-efficient, minimalist Home Assistant integration designed to monitor and control Tado heating systems. It "hijacks" Tado's restrictive API limits to provide critical features often missing from standard HomeKit setups—such as battery health, advanced presence logic, and full HVAC Auto control—all while reducing API traffic by up to 90%. It fills the gap left by official integrations by providing deep access to Tado-specific data.

## Features

- **Extreme API Economy**:
  - **The 2-Call Guarantee**: Every action (e.g., setting a zone to Auto) consumes exactly 2 API calls: 1 for the command and 1 for a targeted confirmation refresh.
  - **Dual-Track Polling**: Presence and HVAC states are checked frequently (Fast Track), while battery states and metadata are checked once a day (Slow Track).
- **High-Performance Architecture**:
  - **Sequential Background Worker**: All API commands are queued and processed one by one to prevent server flooding and ensure rock-solid stability.
  - **Intelligent Batching**: Rapid sequential changes (e.g., turning off multiple rooms) are collected and processed in a single batch with a unified confirmation refresh.
  - **Universal Debouncing**: A 5-second grace period on all UI toggles prevents accidental spamming of the Tado servers.
- **Real-Time Header Hijack**:
  - Captures `RateLimit-Policy` and `RateLimit` headers passively from every outgoing request.
  - API call statistics update immediately in Home Assistant without costing an extra call.
- **Optimistic UI Feedback**: Immediate visual response in the Home Assistant UI while the background worker handles the actual communication.
- **Robustness**:
  - Monkey-patches `tadoasync` to fix common deserialization errors (`nextTimeBlock: null`).
  - Native support for token rotation and automatic re-authentication.

## Prerequisites

- A Tado account with at least one Home and one Zone configured.
- Home Assistant version 2024.6.0 or newer.

## Installation

### Via HACS (Recommended)

1. Open **HACS** in Home Assistant.
2. Click on **Integrations**.
3. Click the three dots in the top right and select **Custom repositories**.
4. Add `https://github.com/banter240/tado_hijack` with category **Integration**.
5. Search for **"Tado Hijack"** and click **Download**.
6. **Restart Home Assistant**.

## Configuration

### Initial Setup

1. Go to **Settings** -> **Devices & Services**.
2. Click **+ ADD INTEGRATION** and search for **"Tado Hijack"**.
3. Follow the OAuth link to authorize the integration.
4. Configure your polling intervals:
   - **Fast Polling (default 1h)**: For presence and heating status.
   - **Slow Polling (default 24h)**: For battery states and device info.

## Supported Entities

- **Home Device**:
  - `switch.away_mode`: Toggle between Home and Away.
  - `sensor.api_daily_limit`: Your current Tado API quota.
  - `sensor.api_calls_remaining`: Real-time remaining calls for the day.
- **Zone Devices**:
  - `switch.auto_mode`: Toggle between HVAC Auto and Manual Overlay (Protection).
  - `binary_sensor.battery_state`: Binary sensor for device battery health.

## Services

### `tado_hijack.manual_poll`
Force an immediate update of all data, including slow-track metadata and batteries.

### `tado_hijack.resume_all_schedules`
Resets all zones in the house to their HVAC Auto in a single batch operation.

## Troubleshooting

- **Logs**: To enable debug logging, add the following to your `configuration.yaml`:
  ```yaml
  logger:
    default: info
    logs:
      custom_components.tado_hijack: debug
  ```

## Disclaimer

This is an unofficial integration and is not affiliated with or endorsed by Tado GmbH. Use at your own risk.

## License

This project is licensed under the GNU General Public License v3.0.
