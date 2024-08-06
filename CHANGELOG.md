# Changelog
Changelog for dupicolib

## [0.3.1] - 2024-08-06
### Changed
- Reinitialize connection to the board (via DTR) only after the first failed connection attempt

## [0.3.0] - 2024-08-04
### Changed
- Make use of the binary protocol only
- Use DTR when retrying the connection to the board

### Removed
- Removed support for text based protocol

## [0.2.0] - 2024-07-29

### Added
- Support for multiple pin maps depending on model type
- Logging support during board connection
- Add code to parse and check fw firmware version
- Add support multiple command classes depending on hardware version and firmware

## [0.1.0] - 2024-07-26

- Initial release
