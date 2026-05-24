# Guarded Machine Update Flow

Date captured: 2026-05-24

This note preserves the update-flow plan so a computer restart or chat reset does not lose the thread.

## Goal

Set up a local update workflow for this machine where package updates are reviewed before they are applied. The agent should follow along, collect enough context to spot known-dangerous packages or suspicious upgrade patterns, and avoid turning routine maintenance into a blind bulk update.

The target package/update surfaces identified on this machine are:

| Surface | Current local signal |
| --- | --- |
| Homebrew | `brew` at `/opt/homebrew/bin/brew`, Homebrew `5.1.13` |
| Node/npm | `node`/`npm` via `nvm`, Node `v20.19.5`, npm `10.8.2` |
| pnpm | `pnpm` `10.15.1` |
| Yarn | `yarn` `1.22.22` |
| Bun | `bun` `1.2.22` |
| Python tooling | `uv` `0.9.18`, Python `3.13.3` |
| Rust tooling | `cargo` `1.87.0`, `rustup` `1.28.2`, active `rustc 1.87.0` |
| RubyGems | system `gem` `3.0.3.1` |
| macOS updates | `softwareupdate` available |
| Mac App Store | `mas` was not found during the inventory |

No updates were applied during the inventory.

## Recommended Flow

Use a semi-automated, agent-reviewed workflow.

1. Run a preflight command that gathers update candidates and security context without upgrading anything.
2. Have an agent review the generated report.
3. Approve a specific batch.
4. Apply updates in stages.
5. Verify the machine and key projects still work.
6. Commit the report and any changed machine manifests.

This is the recommended balance: automation does the boring collection and comparison, while humans/agents still gate risky changes before they touch the machine.

## Proposed Commands

The eventual local command shape should be:

```bash
machine-update preflight
machine-update review-report
machine-update apply --brew
machine-update apply --npm-globals
machine-update apply --language-tools
machine-update apply --os
machine-update verify
```

`preflight` should be dry-run/read-only except for refreshing package-manager metadata where needed.

`apply` should never upgrade every surface at once. It should upgrade one group, then run verification before continuing.

## Preflight Should Collect

Homebrew:

```bash
brew doctor
brew outdated --json=v2
brew leaves
brew tap
brew bundle dump --global --force --describe
```

Notes:

- Homebrew `Brewfile` is useful as a machine snapshot.
- `brew bundle check` can tell whether a `Brewfile` is satisfied.
- `brew bundle` can install or upgrade packages from a `Brewfile`.
- Homebrew is rolling release and does not provide a lockfile like `package-lock.json`.
- `HOMEBREW_BUNDLE_NO_UPGRADE=1` or `brew bundle --no-upgrade` can prevent implicit upgrades while checking/installing declared packages.

Node and JavaScript:

```bash
npm outdated -g --json
npm audit --json
npm audit signatures
pnpm outdated -g
yarn global outdated
bun pm ls -g
corepack --version
```

Notes:

- `npm audit` reports known vulnerabilities from npm advisory data and exits non-zero when vulnerabilities are found.
- `npm audit signatures` verifies registry signatures and provenance attestations where supported.
- npm audit is useful but not complete; malicious packages may not be known to advisory systems yet.
- For project dependencies, prefer reviewing lockfile diffs and running package-manager-native install commands such as `npm ci`, `pnpm install --frozen-lockfile`, or equivalent.

Cross-ecosystem vulnerability scanning:

```bash
osv-scanner scan source --lockfile=/path/to/package-lock.json
osv-scanner scan source --lockfile=/path/to/pnpm-lock.yaml
osv-scanner scan source --lockfile=/path/to/Cargo.lock
```

Notes:

- OSV-Scanner can scan lockfiles and SBOMs for known vulnerabilities.
- It should be part of the report, not the only gate.

Python:

```bash
uv tool list
uv self version
python3 --version
```

Rust:

```bash
rustup check
cargo install --list
cargo --version
rustc --version
```

macOS:

```bash
softwareupdate --list
```

Optional if installed later:

```bash
mas outdated
```

## Agent Review Checklist

For each proposed update batch, the agent should check:

- Is this a major version change?
- Is this package in a known vulnerability or malware advisory?
- Has the version been yanked, deprecated, unpublished, or quickly replaced?
- Is it extremely new? Consider a 24-72 hour delay for non-urgent updates.
- Did maintainership, repository, package name, or provenance change?
- Does the package add or change install scripts?
- Does the dependency tree change much more than expected?
- Are there new transitive dependencies with low reputation or suspicious names?
- Does the changelog mention breaking changes, migrations, auth, crypto, networking, filesystem access, or telemetry?
- Are there project tests or smoke checks that should run immediately after this update?

## Hold Rules

Default holds:

- Hold major upgrades unless explicitly approved.
- Hold new package additions until reviewed.
- Hold packages with new install scripts.
- Hold versions published in the last 24 hours unless the update fixes an active security issue.
- Hold packages flagged by OSV, npm audit, GitHub advisories, Homebrew issue/changelog review, or the package manager itself.
- Hold cask updates for critical daily apps if there are known compatibility reports.

Allowed fast lane:

- Security patches with clear advisories and low breaking-change risk.
- Patch-level updates for well-known tools with clean vulnerability/provenance checks.
- OS security updates, after checking whether a restart is required and saving active work.

## Apply Stages

Suggested order:

1. Save manifests and reports.
2. Update Homebrew formulae, not casks.
3. Verify shell, git, language runtimes, and core CLI tools.
4. Update language global tools such as npm/pnpm/bun/uv/cargo tools.
5. Verify project boot/tests for active Madness Interactive projects.
6. Update Homebrew casks and GUI apps.
7. Apply macOS updates.
8. Restart if needed.
9. Run final verification.

## Verification Ideas

Machine checks:

```bash
brew doctor
node --version
npm --version
pnpm --version
yarn --version
bun --version
uv --version
python3 --version
cargo --version
rustup check
git --version
```

Project checks should be scoped to active work. For Madness Interactive, check any currently active project before broad testing. Good candidates:

- Inventorium app/server smoke check.
- Omnispindle MCP tool smoke check.
- Any project that depends on upgraded Node, Python, Rust, or system packages.

## Report Format

Store reports under a future directory such as:

```text
docs/machine-updates/YYYY-MM-DD-preflight.md
```

Each report should include:

- Date/time and machine identity.
- Package manager versions.
- Outdated package list.
- Security scan results.
- Agent risk notes.
- Approved update batch.
- Commands run.
- Verification results.
- Rollback notes.

## Implementation Plan

1. Create a small script directory, probably `scripts/machine-update/`.
2. Add a `preflight` script that writes Markdown and JSON artifacts.
3. Add a config file for hold rules and high-value packages.
4. Add optional `apply` commands that require explicit flags.
5. Add a report template under `docs/machine-updates/`.
6. Use git commits as checkpoints after docs/script changes and after completed update reports.
7. Push when ready, following the repo's `push-to-deploy` habit.

## Useful Sources

- Homebrew Bundle and Brewfile docs: https://docs.brew.sh/Brew-Bundle-and-Brewfile
- npm audit docs: https://docs.npmjs.com/cli/v8/commands/npm-audit/
- npm package provenance/signature docs: https://docs.npmjs.com/viewing-package-provenance/
- OSV-Scanner source and lockfile scanning docs: https://google.github.io/osv-scanner/usage/scan-source
- Renovate Dependency Dashboard docs: https://docs.renovatebot.com/key-concepts/dashboard/
- Renovate malicious package detection note: https://docs.renovatebot.com/configuration-options/#osvvulnerabilityalerts

## Resume Notes

The next practical step is to implement `machine-update preflight` as a read-only script and generate the first report before running any more upgrades.

Avoid applying package updates from an agent session unless the user explicitly approves the exact update batch.
