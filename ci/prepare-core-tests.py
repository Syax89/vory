"""Prepare existing app regression tests to run against VoryCore only.
Fork-only verification: the full app requires a newer SDK than this runner.
"""
from pathlib import Path

root = Path(__file__).resolve().parents[1]
package = root / 'Packages/VoryCore'
tests = package / 'Tests/VoryCoreTests'
tests.mkdir(parents=True, exist_ok=True)
away = (root / 'VoryTests/AwayRefreshTests.swift').read_text()
(tests / 'AwayRefreshTests.swift').write_text(away.replace('@testable import Vory\n', ''))
registry = (root / 'VoryTests/HermesRemoteTests.swift').read_text()
registry = registry.split('// MARK: Chat registry', 1)[1].split('// MARK: Log grouping', 1)[0]
registry = registry[registry.index('@MainActor'):]
(tests / 'ChatRegistryTests.swift').write_text('import Foundation\nimport Testing\n@testable import VoryCore\n\n' + registry)
manifest = package / 'Package.swift'
source = manifest.read_text()
anchor = '        .target(name: "VoryCore", path: "Sources/VoryCore", swiftSettings: [.swiftLanguageMode(.v6)]),'
assert source.count(anchor) == 1
manifest.write_text(source.replace(anchor, anchor + '\n        .testTarget(name: "VoryCoreTests", dependencies: ["VoryCore"], swiftSettings: [.swiftLanguageMode(.v6)]),'))
print('Prepared unmodified regression test bodies against the complete production VoryCore target')
