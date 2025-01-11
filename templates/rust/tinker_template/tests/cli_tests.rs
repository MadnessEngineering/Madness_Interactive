use assert_cmd::Command;

#[test]
fn test_help_command() {
    let mut cmd = Command::cargo_bin("tinker").unwrap();
    cmd.arg("--help")
        .assert()
        .success()
        .stdout(predicates::str::contains("A craftsperson's browser"));
}

#[test]
fn test_version_command() {
    let mut cmd = Command::cargo_bin("tinker").unwrap();
    cmd.arg("--version")
        .assert()
        .success()
        .stdout(predicates::str::contains(env!("CARGO_PKG_VERSION")));
}

// TODO: Add tests for the --headless, --url, --tabs, --record, --record-path, --replay, and --replay-speed options
