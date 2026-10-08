use crate::ebi_framework::ebi_command::EbiCommand;

pub const PYTHON_PACKAGE: &str = "ebi-pm";

/// Python function names of commands that are deliberately not exposed yet, until they are tested from Python.
pub const NOT_IN_PYTHON: &[&str] = &[
    "analyse_directly_follows_edge_difference_no_frequencies",
    "analyse_non_stochastic_empty_traces",
    "conformance_non_stochastic_fitting_traces",
    "discover_non_stochastic_inductive_miner",
    "discover_non_stochastic_inductive_miner_infrequent",
    "discover_non_stochastic_split_miner",
    "reduce_labelled_petri_net",
    "reduce_process_tree",
    "test_permutation_test_log_model",
];

pub fn pm4py_function_name(path: &[&EbiCommand]) -> String {
    let raw_name = EbiCommand::path_to_string(path);
    raw_name
        .strip_prefix("Ebi ")
        .unwrap_or(&raw_name)
        .to_lowercase()
        .chars()
        .map(|c| if c == ' ' || c == '-' { '_' } else { c })
        .collect()
}

pub fn path_is_in_python(path: &[&EbiCommand]) -> bool {
    path.last().is_some_and(|command| command.is_in_python())
        && !NOT_IN_PYTHON.contains(&pm4py_function_name(path).as_str())
}

#[cfg(test)]
mod tests {
    use super::{NOT_IN_PYTHON, pm4py_function_name};
    use crate::ebi_framework::ebi_command::EBI_COMMANDS;

    #[test]
    fn every_withheld_name_is_a_command_that_would_otherwise_be_in_python() {
        let candidates: Vec<String> = EBI_COMMANDS
            .get_command_paths()
            .iter()
            .filter(|path| path.last().unwrap().is_in_python())
            .map(|path| pm4py_function_name(path))
            .collect();
        for name in NOT_IN_PYTHON {
            assert!(
                candidates.contains(&name.to_string()),
                "{name} is not a command that would otherwise be in Python"
            );
        }
    }
}
