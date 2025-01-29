# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-01-29

### Added
- macOS menu bar interface
- Clipboard history with support for text and images
- Cmd+Shift+V keyboard shortcut to display history
- Context-aware popup window that appears at cursor position
- Real-time clipboard history updates
- System menu with quit option
- macOS permissions handling (Accessibility and Input Monitoring)

### Changed
- Migration to AppKit-based architecture
- Improved keyboard event handling

### Technical
- PyObjC for native macOS integration
- Clipboard monitoring implementation using NSTimer
- Keyboard event handling using pynput
- Modular code structure for better maintainability
