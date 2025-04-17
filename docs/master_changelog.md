# Master Changelog - Madness Interactive

## Overview
This document provides a comprehensive changelog across all projects in the Madness Interactive ecosystem for the past 3 days (April 15-17, 2025). For more detailed information on specific projects, see the individual project changelog files.

## Project Ecosystem Overview
The Madness Interactive ecosystem consists of the following projects organized by category:

### Core Projects
- **madness_interactive** - Main umbrella project repository
- **regressiontestkit** - Testing framework for regression testing
- **Swarmonomicon** - Agent-based system with AI capabilities 
- **Omnispindle** - Todo and task management system (formerly factmcp-todo-server)
- **.hammerspoon** - Lua-based automation for macOS

### RegressionTestKit Ecosystem
- **OculusTestKit** - Test toolkit for Oculus devices
- **phoenix** - Testing framework component
- **rust_ingest** - Data ingestion in Rust
- **rtk-docs-host** - Documentation hosting for RTK
- **gateway_metrics** - Metrics collection for gateways
- **http-dump-server** - Server for HTTP request analysis
- **teltonika_wrapper** - Wrapper for Teltonika devices
- **ohmura-firmware** - Firmware for Ohmura devices
- **saws** - Tool for AWS management

### Projects by Language

#### Python Projects
- **Omnispindle** - Todo and task management system
- **mcp-personal-jira** - Personal Jira integration
- **mqtt-get-var** - MQTT variable retrieval
- **dvtTestKit** - Testing toolkit for DVT
- **EventGhost-py** - Python implementation of EventGhost

#### Rust Projects
- **Tinker** - Rust tinkering project
- **EventGhost-Rust** - Rust implementation of EventGhost

#### Mobile Projects
- **Cogwyrm** - Mobile application

#### Lua Projects
- **hammerspoon-proj** - Hammerspoon configuration and extensions

#### PowerShell Projects
- **WinSystemSnapshot** - System snapshot tool for Windows

#### OS Projects
- **DisplayPhotoTime** - Photo timing display for Windows

#### Tasker Projects
- **Verbatex** - Tasker automation project
- **RunedManifold** - Tasker automation project
- **PhilosophersAmpoule** - Tasker automation project
- **Ludomancery** - Tasker automation project
- **Fragmentarium** - Tasker automation project
- **EntropyVector** - Tasker automation project
- **ContextOfficium** - Tasker automation project
- **AnathemaHexVault** - Tasker automation project

## Main Repository Activity
- Updates to submodules (59e9596, fb83a7b)
- Fixed merge issues (be8446c)
- Created .cursorindexingignore file (c1b14b9)
- Finalized project renaming from factmcp-todo-server to omnispindle (866e11b)
- Added comprehensive changelogs for all projects

## Cursor ChatHistory Updates
Recent chat logs have been added for:
- Project designations in todo server
- Hammerspoon DragonGrid feature development
- DVTTestKit logkit refactoring
- Omnispindle error fixing and improvements
- Swarmonomicon architecture documentation

## Project-Specific Updates

### Omnispindle (formerly factmcp-todo-server)
- **Project Structure**: Renamed project and fixed import structures
- **Database**: Added project field integration to MongoDB collections
- **API**: Updated endpoints for project-based filtering
- **Integration**: Enhanced MQTT integration and improved GitHub Desktop project selection
- **Code Quality**: Fixed Python import errors and improved code organization

### Swarmonomicon
- **Documentation**: Updated Architecture.md with current system structure
- **Project Integration**: Added project database field integration
- **AI Features**: Implemented GPT-4 batch processing with request pooling
- **Agent System**: Improved agent interactivity and communication
- **Tools**: Enhanced git assistant and todo tool integration

### Hammerspoon
- **DragonGrid**: Implemented advanced window management with custom keybindings
- **UI**: Customized log messages with hyperlinks to source code
- **Project Management**: Added GitHub Desktop project selection configuration
- **Technical**: Refactored hotkey management and enhanced multi-monitor support

### RegressionTestKit
- Updated Makefile for fleet command capitalization
- Added database record modification instructions
- Improved handling of ping results in BalenaOS
- Added function for retrieving gateway data

### DVTTestKit
- Converted jenkins handler
- Created logkit.py file
- Refactored code structure for better maintainability

## Cross-Project Integration
- Enhanced project field support across multiple tools
- Improved GitHub Desktop integration with project selection
- Better MQTT communication between components
- Standardized logging and error handling approaches

## Upcoming Development Focus
- Enhanced AI assistant integration for todo suggestions
- Improved scheduling and project management
- LangGraph integration for improved workflows
- Enhanced log message formatting with clickable source links
- Additional window management patterns for Hammerspoon
