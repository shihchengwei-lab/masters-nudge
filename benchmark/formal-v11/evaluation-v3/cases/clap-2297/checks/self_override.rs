
use clap::{App, Arg};

#[test]
fn explicit_self_override_replaces_repeatable_option() {
    let m = App::new("app")
        .arg(Arg::new("input").long("input").takes_value(true)
            .multiple_values(true).multiple_occurrences(true).overrides_with("input"))
        .get_matches_from(vec!["app", "--input", "a", "b", "--input", "c", "d"]);
    assert_eq!(m.values_of("input").unwrap().collect::<Vec<_>>(), vec!["c", "d"]);
    let groups: Vec<Vec<_>> = m.grouped_values_of("input").unwrap()
        .map(|group| group.into_iter().collect()).collect();
    assert_eq!(groups, vec![vec!["c", "d"]]);
}

#[test]
fn empty_occurrence_replaces_repeatable_option_values() {
    let m = App::new("app")
        .arg(Arg::new("input").long("input").takes_value(true)
            .multiple_values(true).multiple_occurrences(true).min_values(0).overrides_with("input"))
        .get_matches_from(vec!["app", "--input", "a", "b", "--input"]);
    assert_eq!(m.values_of("input").unwrap().collect::<Vec<_>>(), Vec::<&str>::new());
    let groups: Vec<Vec<_>> = m.grouped_values_of("input").unwrap()
        .map(|group| group.into_iter().collect()).collect();
    assert_eq!(groups, vec![Vec::<&str>::new()]);
}
