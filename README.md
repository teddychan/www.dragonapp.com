# ClipMenu 2

A modern macOS clipboard-history menu-bar app, written in Swift 6. It lives in
`app/` as a SwiftPM executable that runs as a menu-bar agent (no Dock icon).

## Features
- Clipboard history shown in a menu popped at the cursor or from the menu bar.
- Text snippets organized in folders.
- JavaScript text "Actions" (case, trim, HTML, Base64, hashing, Japanese
  conversions, and more).
- Image thumbnails in the menu, numbered items, and tooltips.
- Global hotkeys (Carbon) and paste synthesis into the frontmost app
  (requires Accessibility permission).
- Settings window (General / Menu / Type / Action / Shortcuts), persisted via
  `UserDefaults`; history and snippets stored via SwiftData.

## Requirements
- Current macOS and a Swift 6 toolchain (Xcode or the Command Line Tools).


## License
MIT — see [LICENSE](LICENSE).

## Credits
Based on the original [ClipMenu](https://github.com/naotaka/ClipMenu) by
Naotaka Morimoto, used under the MIT License.
