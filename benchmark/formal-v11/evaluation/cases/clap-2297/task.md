# Preserve occurrence groups and consistently apply self-overrides

Add support for retrieving values grouped by each occurrence of an argument, and fix inconsistent self-override behavior in the command-line parser.

Required public behavior:
- `ArgMatches::grouped_values_of(name)` returns `None` when absent, otherwise an iterator whose items collect the UTF-8 string values belonging to one occurrence. Preserve occurrence order and value order. Expose the iterator type as `clap::GroupedValues`.
- Repeated long options, `--option=value`, short options and `-o=value` must create separate occurrence groups. Splitting a delimited value produces values in the same occurrence group.
- A positional argument accepting multiple values has one group containing all its values. A trailing positional after `--` follows the same rule. Values for different positional arguments remain separate.
- Existing flattened `values_of` and other value lookup behavior continues to work.
- For a value-taking argument with `.overrides_with(its_own_name)`, each new occurrence replaces the previous occurrence's whole value set. For example, `--input a b --input c d` returns `c,d`; `--input a b c --input d` returns `d`. This also applies with `min_values(0)`.
- `AppSettings::AllArgsOverrideSelf` handles repeated short flags consistently whether repeated inside a cluster or in separate tokens. With flags `p` and `z`, all of `-pz -p`, `-pzp`, `-zpp`, `-pp -z`, `-p -p -z`, `-p -pz`, and `-ppz` must parse successfully.
- Preserve existing argument validation, required/conflict rules, occurrences, defaults, and non-overriding parsing behavior. Internal representation and helper names are implementation choices.
