#![cfg(feature = "registry")]
use std::sync::{Arc, Mutex, atomic::{AtomicUsize, Ordering}};
use tracing::{Event, Subscriber};
use tracing_subscriber::{filter, layer::Context, prelude::*, registry::LookupSpan, Layer};

struct Noop;
impl<S: Subscriber> Layer<S> for Noop {}

#[test]
fn all_observers_reject_under_global_filter() {
    let count = AtomicUsize::new(0);
    let subscriber = tracing_subscriber::registry()
        .with(Noop.with_filter(filter::filter_fn(|_| false)))
        .with(filter::LevelFilter::TRACE);
    let mut span_disabled = false;
    tracing::subscriber::with_default(subscriber, || {
        tracing::info!(value = { count.fetch_add(1, Ordering::SeqCst); 1 });
        let span = tracing::info_span!("rejected", value = { count.fetch_add(1, Ordering::SeqCst); 1 });
        span_disabled = span.is_disabled();
    });
    let evaluations = count.load(Ordering::SeqCst);
    println!("PROBE_RESULT {{\"check\":\"all_observers_reject_under_global_filter\",\"field_evaluations\":{},\"span_disabled\":{},\"passed\":{}}}",
        evaluations, span_disabled, evaluations == 0 && span_disabled);
}

#[derive(Clone, Default)]
struct Current(Arc<Mutex<Vec<(String, String)>>>);
impl<S> Layer<S> for Current where S: Subscriber + for<'a> LookupSpan<'a> {
    fn on_event(&self, _: &Event<'_>, cx: Context<'_, S>) {
        let current = cx.current_span().metadata().map(|m| m.name().to_owned()).unwrap_or_default();
        let lookup = cx.lookup_current().map(|s| s.name().to_owned()).unwrap_or_default();
        self.0.lock().unwrap().push((current, lookup));
    }
}

#[test]
fn current_view_retains_visible_entered_root() {
    let seen = Current::default();
    let subscriber = tracing_subscriber::registry()
        .with(seen.clone().with_filter(filter::filter_fn(|m| m.name() != "hidden")))
        .with(Noop);
    tracing::subscriber::with_default(subscriber, || {
        let _visible = tracing::info_span!("visible").entered();
        let _hidden = tracing::info_span!(parent: None, "hidden").entered();
        tracing::info!("check current view");
    });
    let values = seen.0.lock().unwrap();
    let expected = vec![("visible".to_owned(), "visible".to_owned())];
    println!("PROBE_RESULT {{\"check\":\"current_view_retains_visible_entered_root\",\"observations\":{:?},\"passed\":{}}}",
        values.iter().map(|(a,b)| vec![a,b]).collect::<Vec<_>>(), *values == expected);
}


#[derive(Clone, Default)]
struct EventCount(Arc<AtomicUsize>);
impl<S: Subscriber> Layer<S> for EventCount {
    fn on_event(&self, _: &Event<'_>, _: Context<'_, S>) {
        self.0.fetch_add(1, Ordering::SeqCst);
    }
}

#[test]
fn shared_arc_keeps_filter_rejection() {
    let count = EventCount::default();
    let layer = Arc::new(count.clone().with_filter(filter::LevelFilter::OFF));
    let _retained = layer.clone();
    let subscriber = tracing_subscriber::registry().with(layer).with(Noop);
    tracing::subscriber::with_default(subscriber, || tracing::info!("must be rejected"));
    let events = count.0.load(Ordering::SeqCst);
    println!("PROBE_RESULT {{\"check\":\"shared_arc_keeps_filter_rejection\",\"events\":{},\"passed\":{}}}", events, events == 0);
}

#[derive(Clone, Default)]
struct EnterCount(Arc<AtomicUsize>);
impl<S: Subscriber> Layer<S> for EnterCount {
    fn on_enter(&self, _: &tracing::span::Id, _: Context<'_, S>) {
        self.0.fetch_add(1, Ordering::SeqCst);
    }
}

#[test]
fn same_filter_reload_keeps_existing_span_hidden() {
    let count = EnterCount::default();
    let (layer, handle) = tracing_subscriber::reload::Layer::new(count.clone().with_filter(filter::LevelFilter::OFF));
    let subscriber = tracing_subscriber::registry().with(layer).with(Noop);
    tracing::subscriber::with_default(subscriber, || {
        let span = tracing::info_span!("already_hidden");
        handle.reload(count.clone().with_filter(filter::LevelFilter::OFF)).unwrap();
        let _entered = span.enter();
    });
    let enters = count.0.load(Ordering::SeqCst);
    println!("PROBE_RESULT {{\"check\":\"same_filter_reload_keeps_existing_span_hidden\",\"enters\":{},\"passed\":{}}}", enters, enters == 0);
}

#[test]
fn boxed_reload_preserves_existing_filter_support() {
    let initial = Box::new(Noop.with_filter(filter::LevelFilter::INFO));
    let (layer, handle) = tracing_subscriber::reload::Layer::new(initial);
    let subscriber = tracing_subscriber::registry().with(layer);
    let result = std::panic::catch_unwind(std::panic::AssertUnwindSafe(|| {
        tracing::subscriber::with_default(subscriber, || {
            handle.reload(Box::new(Noop.with_filter(filter::LevelFilter::INFO)))
        })
    }));
    let panicked = result.is_err();
    let passed = matches!(result, Ok(Ok(())));
    println!("PROBE_RESULT {{\"check\":\"boxed_reload_preserves_existing_filter_support\",\"panicked\":{},\"passed\":{}}}", panicked, passed);
}
