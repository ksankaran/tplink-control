# Multi-Device Smart Home Control - Implementation Plan

## Background and Motivation

The current codebase is a simple FastAPI application that controls a single TP-Link Kasa smart plug. The user has requested extending this application to support multiple smart device APIs from various brands:

- **TP-Link Kasa** (already supported)
- **Philips Hue** (smart lights)
- **Wyze** (smart lights)
- **Roku** (smart lights - not media players)
- **Cree** (smart lights)
- **Geeni** (smart lights)
- **Nanoleaf** (smart lights)

The goal is to create a unified interface that can control devices from all these brands through a single web application, while maintaining the simplicity and ease of use of the current implementation.

## Key Challenges and Analysis

### 1. Library Availability and API Support

**Well-Supported Brands:**
- **TP-Link Kasa**: Already integrated via `python-kasa` library
- **Philips Hue**: Well-documented with `phue` (synchronous) and `aiohue` (async) libraries. Requires Hue Bridge IP and API key.
- **Nanoleaf**: Has `nanoleafapi` library. Requires device IP and authentication token.

**Challenging Brands:**
- **Wyze**: No official public API. May require:
  - Reverse engineering of Wyze app protocols
  - Use of unofficial libraries (if available)
  - Potential cloud API integration
- **Roku Smart Lights**: No public API available. Challenges include:
  - No official developer documentation
  - May require reverse engineering
  - Cloud-dependent operation
  - Authentication token requirements
- **Cree Connected**: Limited public API. May use:
  - Tuya protocol (if rebranded)
  - Custom implementation required
- **Geeni**: Uses Tuya protocol. Can leverage:
  - `python-tuya` library
  - `tuyapi` library
  - Requires device ID and local key

### 2. Architectural Challenges

1. **Different Device Types**: Current app controls smart plugs, but extension needs to support smart lights with different capabilities (brightness, color, etc.)
2. **Authentication Methods**: Each brand uses different authentication:
   - TP-Link: IP-based, no auth needed
   - Hue: Bridge IP + API key
   - Nanoleaf: IP + auth token
   - Tuya-based (Geeni/Cree): Device ID + local key
   - Wyze/Roku: Unknown/cloud-based
3. **Network Protocols**: Mix of local network APIs and cloud APIs
4. **Device Discovery**: Each brand has different discovery mechanisms
5. **Capability Differences**: Some devices support brightness/color, others are simple on/off

### 3. Design Considerations

- **Backward Compatibility**: Must maintain existing TP-Link functionality
- **Configuration Management**: Need flexible config system for multiple devices
- **Error Handling**: Robust error handling for different failure modes
- **Extensibility**: Easy to add new device types in the future
- **Simplicity**: Keep the simple, single-page UI while supporting multiple devices

## High-level Task Breakdown

### Phase 1: Architecture Refactoring
**Goal**: Create abstract device interface and refactor existing TP-Link code to use it.

#### Task 1.1: Create Abstract Device Interface
- **Description**: Define a base class/interface that all device adapters will implement
- **Success Criteria**:
  - Abstract base class created with methods: `turn_on()`, `turn_off()`, `is_on()`, `get_status()`
  - Optional methods for advanced features: `set_brightness()`, `set_color()`
  - All methods are async
  - Type hints included
  - Documentation strings added
- **Files**: `devices/base.py`

#### Task 1.2: Create TP-Link Adapter
- **Description**: Refactor existing TP-Link code into an adapter class implementing the base interface
- **Success Criteria**:
  - TP-Link adapter class created inheriting from base interface
  - All existing functionality preserved
  - Adapter can be instantiated with device IP
  - All methods properly implemented
  - Unit tests pass
- **Files**: `devices/tplink.py`

#### Task 1.3: Create Device Registry/Manager
- **Description**: Create a system to manage multiple devices with configuration
- **Success Criteria**:
  - Device registry class created
  - Can register devices with name, type, and config
  - Can retrieve devices by name
  - Can list all registered devices
  - Configuration stored in JSON or environment variables
- **Files**: `devices/registry.py`, `config.py`

#### Task 1.4: Refactor Main Application
- **Description**: Update `app.py` to use the new device architecture
- **Success Criteria**:
  - Application uses device registry
  - Existing UI still works with TP-Link devices
  - Device selection mechanism added (dropdown or device parameter)
  - All existing tests pass
  - No breaking changes to existing functionality
- **Files**: `app.py`

### Phase 2: Well-Supported Device Integrations
**Goal**: Add support for brands with well-documented APIs and libraries.

#### Task 2.1: Research and Install Dependencies
- **Description**: Research and add required Python libraries for Hue, Nanoleaf, and Tuya
- **Success Criteria**:
  - Libraries identified and documented
  - `requirements.txt` updated with:
    - `aiohue` or `phue` for Hue
    - `nanoleafapi` for Nanoleaf
    - `python-tuya` or `tuyapi` for Geeni/Cree
  - Libraries installed and importable
  - Version compatibility verified
- **Files**: `requirements.txt`

#### Task 2.2: Implement Philips Hue Adapter
- **Description**: Create adapter for Philips Hue lights
- **Success Criteria**:
  - Hue adapter class created
  - Can connect to Hue Bridge with IP and API key
  - Can control individual lights or groups
  - Supports on/off, brightness, and color (if applicable)
  - Error handling for connection failures
  - Unit tests created and passing
- **Files**: `devices/hue.py`, `tests/test_hue.py`

#### Task 2.3: Implement Nanoleaf Adapter
- **Description**: Create adapter for Nanoleaf devices
- **Success Criteria**:
  - Nanoleaf adapter class created
  - Can authenticate with device using IP and token
  - Can control on/off state
  - Supports brightness and color control
  - Error handling implemented
  - Unit tests created and passing
- **Files**: `devices/nanoleaf.py`, `tests/test_nanoleaf.py`

#### Task 2.4: Implement Geeni Adapter (Tuya Protocol)
- **Description**: Create adapter for Geeni devices using Tuya protocol
- **Success Criteria**:
  - Geeni adapter class created using Tuya library
  - Can connect with device ID and local key
  - Can control on/off state
  - Supports brightness if device supports it
  - Error handling for authentication failures
  - Unit tests created and passing
- **Files**: `devices/geeni.py`, `tests/test_geeni.py`

#### Task 2.5: Implement Cree Adapter
- **Description**: Create adapter for Cree Connected devices
- **Success Criteria**:
  - Research Cree API/protocol (may be Tuya-based)
  - Cree adapter class created
  - Can control devices (method depends on research)
  - Error handling implemented
  - Unit tests created and passing
- **Files**: `devices/cree.py`, `tests/test_cree.py`

### Phase 3: Challenging Device Integrations
**Goal**: Add support for brands with limited or no public APIs.

#### Task 3.1: Research Wyze API/Protocol
- **Description**: Investigate available methods to control Wyze devices
- **Success Criteria**:
  - Research completed and documented
  - Options identified (unofficial libraries, reverse engineering, cloud API)
  - Decision made on approach
  - Implementation plan created
- **Files**: Documentation in scratchpad

#### Task 3.2: Implement Wyze Adapter
- **Description**: Create adapter for Wyze devices based on research
- **Success Criteria**:
  - Wyze adapter class created
  - Can control Wyze smart lights
  - Authentication/connection method implemented
  - Error handling for failures
  - Unit tests created (may use mocks if cloud-dependent)
- **Files**: `devices/wyze.py`, `tests/test_wyze.py`

#### Task 3.3: Research Roku Smart Lights API/Protocol
- **Description**: Investigate methods to control Roku smart lights
- **Success Criteria**:
  - Research completed and documented
  - Options identified (reverse engineering, cloud API, indirect methods)
  - Challenges and limitations documented
  - Decision made on feasibility and approach
- **Files**: Documentation in scratchpad

#### Task 3.4: Implement Roku Adapter (if feasible)
- **Description**: Create adapter for Roku smart lights if viable approach found
- **Success Criteria**:
  - Roku adapter class created (if feasible)
  - Can control Roku smart lights
  - Authentication method implemented
  - Error handling for failures
  - Limitations documented
  - Unit tests created
- **Files**: `devices/roku.py`, `tests/test_roku.py`
- **Note**: This task may be marked as blocked if no viable approach is found

### Phase 4: UI Enhancement
**Goal**: Update the web interface to support multiple devices.

#### Task 4.1: Add Device Selection UI
- **Description**: Update HTML to allow users to select which device to control
- **Success Criteria**:
  - Device dropdown/selector added to UI
  - Selected device persists during session
  - UI updates to show selected device name
  - Works with all device types
- **Files**: `app.py` (HTML template)

#### Task 4.2: Add Device Configuration UI (Optional)
- **Description**: Create interface for adding/configuring devices
- **Success Criteria**:
  - Configuration page/form created
  - Can add new devices with required credentials
  - Can edit existing device configurations
  - Can remove devices
  - Configuration persisted (JSON file or database)
- **Files**: `app.py`, `config.py`
- **Note**: May be deferred if using environment variables for config

### Phase 5: Testing and Documentation
**Goal**: Ensure reliability and usability.

#### Task 5.1: Integration Testing
- **Description**: Test the complete system with real or mocked devices
- **Success Criteria**:
  - Integration tests created for each device type
  - Tests verify end-to-end functionality
  - All tests pass
  - Error scenarios tested
- **Files**: `tests/test_integration.py`

#### Task 5.2: Update Documentation
- **Description**: Update README and create setup guides for each device type
- **Success Criteria**:
  - README updated with multi-device instructions
  - Setup guide for each device type created
  - Configuration examples provided
  - Known limitations documented
- **Files**: `README.md`, `docs/` (if created)

#### Task 5.3: Error Handling Enhancement
- **Description**: Add comprehensive error handling throughout the application
- **Success Criteria**:
  - All device adapters have proper error handling
  - User-friendly error messages in UI
  - Logging added for debugging
  - Graceful degradation when devices unavailable
- **Files**: All device adapter files, `app.py`

## Project Status Board

### Phase 1: Architecture Refactoring
- [x] Task 1.1: Create Abstract Device Interface
- [x] Task 1.2: Create TP-Link Adapter
- [x] Task 1.3: Create Device Registry/Manager
- [x] Task 1.4: Refactor Main Application

### Phase 2: Well-Supported Device Integrations
- [x] Task 2.1: Research and Install Dependencies
- [x] Task 2.2: Implement Philips Hue Adapter
- [x] Task 2.3: Implement Nanoleaf Adapter
- [x] Task 2.4: Implement Geeni Adapter (Tuya Protocol)
- [x] Task 2.5: Implement Cree Adapter

### Phase 3: Challenging Device Integrations
- [ ] Task 3.1: Research Wyze API/Protocol
- [ ] Task 3.2: Implement Wyze Adapter
- [ ] Task 3.3: Research Roku Smart Lights API/Protocol
- [ ] Task 3.4: Implement Roku Adapter (if feasible)

### Phase 4: UI Enhancement
- [ ] Task 4.1: Add Device Selection UI
- [ ] Task 4.2: Add Device Configuration UI (Optional)

### Phase 5: Testing and Documentation
- [ ] Task 5.1: Integration Testing
- [ ] Task 5.2: Update Documentation
- [ ] Task 5.3: Error Handling Enhancement

## Current Status / Progress Tracking

**Current Phase**: Phase 2 Complete - Ready for Testing
**Last Updated**: Phase 2 implementation completed

**Notes**:
- Phase 1 implementation completed successfully
- Phase 2 implementation completed successfully
- All well-supported device integrations completed:
  - Dependencies installed: `aiohue==4.8.0`, `nanoleafapi==2.1.2`, `tinytuya==1.17.4`
  - Philips Hue adapter created in `devices/hue.py` (supports lights and groups)
  - Nanoleaf adapter created in `devices/nanoleaf.py`
  - Geeni adapter created in `devices/geeni.py` (Tuya protocol)
  - Cree adapter created in `devices/cree.py` (Tuya protocol)
- Application updated to support all new device types in configuration
- All adapters implement the SmartDevice interface correctly
- All imports verified and working
- Ready for user testing before proceeding to Phase 3

## Executor's Feedback or Assistance Requests

**Phase 1 Completion Report:**

All Phase 1 tasks have been completed successfully:

1. **Abstract Device Interface** (`devices/base.py`):
   - Created `SmartDevice` abstract base class
   - Defined required methods: `turn_on()`, `turn_off()`, `is_on()`, `get_status()`
   - Added optional methods: `set_brightness()`, `set_color()`
   - Created custom exceptions: `DeviceError`, `DeviceConnectionError`
   - All methods are async with proper type hints and documentation

2. **TP-Link Adapter** (`devices/tplink.py`):
   - Created `TPLinkDevice` class implementing `SmartDevice` interface
   - Maintains all existing functionality from original code
   - Added proper error handling and connection management
   - Supports device IP configuration

3. **Device Registry** (`devices/registry.py`):
   - Created `DeviceRegistry` class for managing multiple devices
   - Supports device registration, retrieval, and listing
   - Provides methods for device management

4. **Configuration Management** (`config.py`):
   - Created configuration loading system
   - Supports both JSON file (`.devices.json`) and environment variables
   - Maintains backward compatibility with existing `.env` setup

5. **Main Application Refactoring** (`app.py`):
   - Refactored to use new device architecture
   - Maintains backward compatibility with existing setup
   - Added device parameter support (defaults to "default" device)
   - Enhanced error handling with user-friendly messages
   - All existing functionality preserved

**Documentation Updated:**
- README.md updated to reflect new architecture and multi-device support
- AGENT.md updated with detailed architecture documentation
- Both files now document the device adapter pattern and configuration options

**Phase 2 Completion Report:**

All Phase 2 tasks have been completed successfully:

1. **Dependencies Installed** (`requirements.txt`):
   - `aiohue==4.8.0` for Philips Hue support
   - `nanoleafapi==2.1.2` for Nanoleaf support
   - `tinytuya==1.17.4` for Geeni and Cree (Tuya protocol) support

2. **Philips Hue Adapter** (`devices/hue.py`):
   - Supports individual lights and light groups
   - Requires bridge IP and API key
   - Supports brightness and color control
   - Proper error handling for connection and authentication failures

3. **Nanoleaf Adapter** (`devices/nanoleaf.py`):
   - Supports Nanoleaf Light Panels, Canvas, and Shapes
   - Requires device IP and authentication token
   - Supports brightness and color control
   - Handles connection errors gracefully

4. **Geeni Adapter** (`devices/geeni.py`):
   - Uses Tuya protocol via tinytuya library
   - Requires device ID, IP, and local key
   - Supports brightness and color control
   - Handles Tuya DPS (Data Points) for status

5. **Cree Adapter** (`devices/cree.py`):
   - Uses Tuya protocol via tinytuya library (similar to Geeni)
   - Requires device ID, IP, and local key
   - Supports brightness and color control
   - Handles Tuya DPS (Data Points) for status

6. **Application Updates** (`app.py`):
   - Updated to support all new device types in configuration
   - Device initialization supports all adapter types
   - Configuration system ready for multi-device setups

**Testing Required:**
- User should test that existing TP-Link device still works
- Test each new device type with appropriate configuration
- Verify that the web interface displays correctly for all device types
- Test toggle functionality for each device type
- Verify error messages appear correctly when devices are unavailable

**Next Steps:**
- Awaiting user confirmation that Phase 2 is working correctly
- Once confirmed, proceed to Phase 3: Challenging Device Integrations (Wyze and Roku)

## Lessons

*This section will be updated with lessons learned during implementation.*

**User Specified Lessons**:
- Include info useful for debugging in the program output
- Read the file before you try to edit it
- If there are vulnerabilities that appear in the terminal, run npm audit before proceeding
- Always ask before using the -force git command

