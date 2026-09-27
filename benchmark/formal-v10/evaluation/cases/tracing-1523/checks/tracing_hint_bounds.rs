#![cfg(feature = "registry")]
use tracing::{Event, Subscriber};
use tracing_subscriber::{filter::LevelFilter, layer::Context, prelude::*, Layer};

struct Capture;
impl<S: Subscriber> Layer<S> for Capture {
    fn on_event(&self, _: &Event<'_>, _: Context<'_, S>) {}
}

#[test]
fn global_filter_does_not_add_a_consumer() {
    let subscriber = tracing_subscriber::registry()
        .with(Capture.with_filter(LevelFilter::INFO))
        .with(LevelFilter::TRACE);
    let hint = subscriber.max_level_hint();
    println!("PROBE_RESULT {{\"check\":\"global_filter_does_not_add_a_consumer\",\"hint\":\"{:?}\",\"passed\":{}}}", hint, hint == Some(LevelFilter::INFO));
}
