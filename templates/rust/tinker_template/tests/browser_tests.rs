use assert_cmd::Command;
use std::time::Duration;
use predicates::prelude::*;
use std::fs;

#[test]
fn test_browser_headless_startup() {
    let mut cmd = Command::cargo_bin("tinker").unwrap();
    let assert = cmd
        .arg("--headless")
        .timeout(Duration::from_secs(5))
        .assert();

    assert
        .success()
        .stdout(predicate::str::contains("Starting Tinker Workshop"));
}

#[test]
fn test_browser_with_url() {
    let mut cmd = Command::cargo_bin("tinker").unwrap();
    let assert = cmd
        .args(["--headless", "--url", "https://github.com/DanEdens/Tinker"])
        .timeout(Duration::from_secs(5))
        .assert();

    assert
        .success()
        .stdout(predicate::str::contains("Navigating to: https://github.com/DanEdens/Tinker"));
}

#[test]
fn test_browser_with_multiple_tabs() {
    let mut cmd = Command::cargo_bin("tinker").unwrap();
    let assert = cmd
        .args(["--headless", "--tabs", "3"])
        .timeout(Duration::from_secs(5))
        .assert();

    assert
        .success()
        .stdout(predicate::str::contains("Created new tab"));
}

#[test]
fn test_browser_recording() {
    let record_path = "test_recording.json";

    // Clean up any existing recording
    let _ = fs::remove_file(record_path);

    let mut cmd = Command::cargo_bin("tinker").unwrap();
    let assert = cmd
        .args([
            "--headless",
            "--record",
            "--record-path",
            record_path,
            "--url",
            "https://github.com/DanEdens/Tinker"
        ])
        .timeout(Duration::from_secs(5))
        .assert();

    assert
        .success()
        .stdout(predicate::str::contains("Recording will be saved to"));

    // Verify the recording file was created
    assert!(fs::metadata(record_path).is_ok());

    // Clean up
    let _ = fs::remove_file(record_path);
}

#[test]
fn test_browser_replay() {
    let record_path = "test_replay.json";

    // First create a recording
    let mut cmd = Command::cargo_bin("tinker").unwrap();
    let assert = cmd
        .args([
            "--headless",
            "--record",
            "--record-path",
            record_path,
            "--url",
            "https://github.com/DanEdens/Tinker"
        ])
        .timeout(Duration::from_secs(5))
        .assert();

    assert.success();

    // Then replay it
    let mut cmd = Command::cargo_bin("tinker").unwrap();
    let assert = cmd
        .args([
            "--headless",
            "--replay",
            record_path,
            "--replay-speed",
            "2.0"
        ])
        .timeout(Duration::from_secs(5))
        .assert();

    assert
        .success()
        .stdout(predicate::str::contains("Replaying events"));

    // Clean up
    let _ = fs::remove_file(record_path);
}

#[test]
fn test_browser_record_without_path() {
    let mut cmd = Command::cargo_bin("tinker").unwrap();
    let assert = cmd
        .args(["--headless", "--record"])
        .timeout(Duration::from_secs(5))
        .assert();

    assert
        .failure()
        .stderr(predicate::str::contains("--record-path is required"));
}
