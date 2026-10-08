//! The command line of `ebi prob trac` is public: these tests pin it as it is.
use std::process::{Command, Output};

fn run(trace: &[&str]) -> Output {
    Command::new(env!("CARGO_BIN_EXE_ebi"))
        .args(["prob", "trac", "testfiles/aa-ab-ba.slang"])
        .args(trace)
        .output()
        .unwrap()
}

fn stdout_of(trace: &[&str]) -> String {
    let output = run(trace);
    assert!(
        output.status.success(),
        "{}",
        String::from_utf8_lossy(&output.stderr)
    );
    String::from_utf8(output.stdout).unwrap()
}

#[test]
fn trace_is_given_as_separate_arguments() {
    assert_eq!(stdout_of(&["b", "a"]), "Approximately 0.6\n3/5\n\n");
}

#[test]
fn trace_that_is_not_in_the_language_has_probability_zero() {
    assert_eq!(stdout_of(&["b", "b"]), "Approximately 0\n0\n\n");
}

#[test]
fn trace_with_an_unknown_activity_has_probability_zero() {
    assert_eq!(stdout_of(&["a", "unknown"]), "Approximately 0\n0\n\n");
}

#[test]
fn a_missing_trace_is_a_usage_error() {
    assert!(!run(&[]).status.success());
}
