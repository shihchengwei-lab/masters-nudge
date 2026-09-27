# Independent filters for tracing subscriber layers

## Motivation

Currently, filtering with `Layer`s is always _global_. If a `Layer`
performs filtering, it will disable a span or event for _all_ layers
that compose the current subscriber. In some cases, however, it is often
desirable for individual layers to see different spans or events than
the rest of the `Layer` stack.

Issues in other projects, such as tokio-rs/console#64 and
tokio-rs/console#76, linkerd/linkerd2-proxy#601,
influxdata/influxdb_iox#1012 and influxdata/influxdb_iox#1681,
jackwaudby/spaghetti#86, etc; as well as `tracing` feature requests like
#302, #597, and #1348, all indicate that there is significant demand for
the ability to add filters to individual `Layer`s.

Unfortunately, doing this nicely is somewhat complicated. Although a
naive implementation that simply skips events/spans in `Layer::on_event`
and `Layer::new_span` based on some filter is relatively simple, this
wouldn't really be an ideal solution, for a number of reasons. A proper
per-layer filtering implementation would satisfy the following
_desiderata_:

* If a per-layer filter disables a span, it shouldn't be present _for
  the layer that filter is attached to_ when iterating over span
  contexts (such as `Context::event_scope`, `SpanRef::scope`, etc), or
  when looking up a span's parents.
* When _all_ per-layer filters disable a span or event, it should be
  completely disabled, rather than simply skipped by those particular
  layers. This means that per-layer filters should participate in
  `enabled`, as well as being able to skip spans and events in
  `new_span` and `on_event`.
* Per-layer filters shouldn't interfere with non-filtered `Layer`s.
  If a subscriber contains layers without any filters, as well as
  layers with per-layer filters, the non-filtered `Layer`s should
  behave exactly as they would without any per-layer filters present.
* Similarly, per-layer filters shouldn't interfere with global
  filtering. If a `Layer` in a stack is performing global filtering
  (e.g. the current filtering behavior), per-layer filters should also
  be effected by the global filter.
* Per-layer filters _should_ be able to participate in `Interest`
  caching, _but only when doing so doesn't interfere with
  non-per-layer-filtered layers_.
* Per-layer filters should be _tree-shaped_. If a `Subscriber` consists
  of multiple layers that have been `Layered` together to form new
  `Layer`s, and some of the `Layered` layers have per-layer filters,
  those per-layer filters should effect all layers in that subtree.
  Similarly, if `Layer`s in a per-layer filtered subtree have their
  _own_ per-layer filters, those layers should be effected by the union
  of their own filters and any per-layer filters that wrap them at
  higher levels in the tree.

Meeting all these requirements means that implementing per-layer
filtering correctly is somewhat more complex than simply skipping
events and spans in a `Layer`'s `on_event` and `new_span` callbacks.


## Required public API and behavior

Enable the per-layer filtering API under the `registry` feature. Preserve existing unfiltered/global Layer behavior and the current public subscriber APIs.

- Expose `tracing_subscriber::layer::Filter<S>`, with `enabled(&self, metadata: &Metadata<'_>, context: &Context<'_, S>) -> bool`, `callsite_enabled(&self, metadata: &'static Metadata<'static>) -> Interest` and `max_level_hint(&self) -> Option<LevelFilter>`. The latter two have conservative defaults (`Interest::sometimes()` and `None`).
- `Layer::with_filter(self, filter)` returns `filter::Filtered<Self, F, S>` for a `Filter<S>`. `LevelFilter` itself implements the per-layer filter trait.
- Expose `filter::FilterFn<F = fn(&Metadata<'_>) -> bool>`, `FilterFn::new`, and `filter::filter_fn` for metadata-only predicates. Such static predicates can yield always/never callsite interests.
- Expose `filter::DynFilterFn<S, F = fn(&Metadata<'_>, &Context<'_, S>) -> bool, R = fn(&'static Metadata<'static>) -> Interest>`, `DynFilterFn::new`, and `filter::dynamic_filter_fn` for context-sensitive predicates. A dynamic predicate must be reevaluated for each event/span unless an explicit callsite filter establishes a stable result; do not cache a decision made with an empty context as its runtime result.
- Both function-filter types provide `with_max_level_hint(impl Into<LevelFilter>)`; the dynamic type also provides `with_callsite_filter` accepting a static-metadata predicate returning `Interest`.
- Every filtered layer receives only the spans and events its filter enables. Its span callbacks, current-span lookup, explicit span lookup, event/span scope, and parent traversal must consistently see that filtered view. Rejected ancestors must not hide accepted ancestors further up the chain.
- Nested filters apply to the entire wrapped subtree. A nested layer sees an item only when every enclosing filter and its own filter allows it. Sibling layers retain independent views. Span references returned from a filtered context retain that view during subsequent parent/scope traversal.
- A globally filtered-out item remains disabled everywhere. A per-layer rejection must never suppress a sibling that wants the item, including an unfiltered sibling. When all consumers reject an item, the subscriber should disable it entirely.
- Callsite interest caching must preserve these rules for mixed filtered/unfiltered stacks, multiple static filters that disagree, context-sensitive filters, and nested subtrees. Repeated emissions from the same callsite must remain correct.
- `max_level_hint()` must describe the combined subscriber's actual possible verbosity. Independent branches combine by the most verbose permitted branch; an unhinted/unfiltered branch yields `None` unless an enclosing global/subtree filter bounds it. Nested filters restrict their subtree. Hints must not disable an unfiltered sibling.
- Existing layering, downcasting, boxed layers, reload behavior, span closing and cleanup must keep working. Internal file layout, helper names and representation are implementation choices; no debug log file is required.
