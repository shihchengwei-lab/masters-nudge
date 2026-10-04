#![cfg(feature = "registry")]
use std::sync::{Arc, atomic::{AtomicUsize, Ordering}};
use tracing::{Event, Metadata, Subscriber};
use tracing_core::subscriber::Interest;
use tracing_subscriber::{filter::{dynamic_filter_fn, filter_fn, LevelFilter}, layer::Context, prelude::*, Layer};

#[derive(Clone, Default)]
struct Seen(Arc<AtomicUsize>);
impl<S: Subscriber> Layer<S> for Seen {
    fn on_event(&self, _: &Event<'_>, _: Context<'_, S>) { self.0.fetch_add(1, Ordering::SeqCst); }
}
#[test]
fn field_nested_event_preserves_outer_decision() {
    let seen = Seen::default();
    let sub = tracing_subscriber::registry().with(seen.clone().with_filter(dynamic_filter_fn(|m, _| m.target() == "outer")));
    tracing::subscriber::with_default(sub, || {
        tracing::info!(target: "outer", value = { tracing::info!(target: "inner", "rejected"); 1 });
    });
    let events = seen.0.load(Ordering::SeqCst);
    println!("PROBE_RESULT {{\"check\":\"field_nested_event_preserves_outer_decision\",\"events\":{},\"passed\":{}}}", events, events == 1);
}
#[test]
fn pure_global_filter_does_not_enable_rejected_items() {
    let evaluations = AtomicUsize::new(0);
    let sub = tracing_subscriber::registry().with(Seen::default().with_filter(dynamic_filter_fn(|_, _| false))).with(LevelFilter::TRACE);
    let disabled = tracing::subscriber::with_default(sub, || {
        tracing::info!(value = evaluations.fetch_add(1, Ordering::SeqCst));
        tracing::info_span!("rejected_span").is_disabled()
    });
    let fields = evaluations.load(Ordering::SeqCst);
    println!("PROBE_RESULT {{\"check\":\"pure_global_filter_does_not_enable_rejected_items\",\"fields\":{},\"span_disabled\":{},\"passed\":{}}}", fields, disabled, fields == 0 && disabled);
}
struct Veto;
impl<S: Subscriber> Layer<S> for Veto {
    fn enabled(&self, _: &Metadata<'_>, _: Context<'_, S>) -> bool { false }
    fn register_callsite(&self, _: &'static Metadata<'static>) -> Interest { Interest::sometimes() }
}
#[test]
fn wrapped_custom_global_veto_rejects_every_consumer() {
    let seen = Seen::default();
    let sub = tracing_subscriber::registry().with(seen.clone()).with(Veto.with_filter(filter_fn(|_| true)));
    tracing::subscriber::with_default(sub, || tracing::info!("must not arrive"));
    let events = seen.0.load(Ordering::SeqCst);
    println!("PROBE_RESULT {{\"check\":\"wrapped_custom_global_veto_rejects_every_consumer\",\"events\":{},\"passed\":{}}}", events, events == 0);
}

#[test]
fn context_enabled_is_an_independent_query() {
    let outer = Seen::default();
    let sub = tracing_subscriber::registry()
        .with(Seen::default().with_filter(dynamic_filter_fn(|_, _| false)))
        .with(outer.clone().with_filter(dynamic_filter_fn(|m, cx| cx.enabled(m))));
    let disabled = tracing::subscriber::with_default(sub, || {
        tracing::info!("must be rejected by queried inner subscriber");
        tracing::info_span!("queried_inner_rejects").is_disabled()
    });
    let events = outer.0.load(Ordering::SeqCst);
    println!("PROBE_RESULT {{\"check\":\"context_enabled_is_an_independent_query\",\"events\":{},\"span_disabled\":{},\"passed\":{}}}", events, disabled, events == 0 && disabled);
}
