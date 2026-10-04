use clap::{App, Arg};
#[test]
fn diagnostic_preserve_occurrences() {
 for (kind,self_override,multi) in [("non_overriding_control",false,false),("self_override_single_value",true,false),("self_override_multi_values",true,true)] {
  let mut arg=Arg::new("input").long("input").multiple_occurrences(true).multiple_values(multi).takes_value(true);
  if self_override {arg=arg.overrides_with("input");}
  let tokens=if multi {vec!["app","--input","a","b","--input","c","d"]} else {vec!["app","--input","a","--input","c"]};
  let matches=App::new("app").arg(arg).get_matches_from(tokens);
  let values:Vec<_>=matches.values_of("input").unwrap().collect();
  println!("PROBE_RESULT {{\"case\":\"{}\",\"occurrences\":{},\"values\":{:?}}}",kind,matches.occurrences_of("input"),values);
 }
}
