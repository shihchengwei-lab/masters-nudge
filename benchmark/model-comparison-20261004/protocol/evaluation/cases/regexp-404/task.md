`regexp/no-dupe-disjunctions` should "de-sugar" character classes
**Description**
While writing some regexes, I noticed the `regexp/no-dupe-disjunctions` didn't say anything about a regex of this from:

```js
/a+|[abc]/
```

The `a` in `[abc]` is clearly useless but didn't get reported. This is because `regexp/no-dupe-disjunctions` looks at the `[abc]` as a whole and only detects the overlap between `a+` and `[abc]`. It doesn't understand that the overlap is really subset (with `a` in `[abc]`) and therefor you get this report with `report: "all"` even though the problem is trivial.

---

Some test cases:

```js
// bad
var foo = /a+|[abc]/; // remove `a` in `[abc]`
var foo = /a+|a|b|c/; // remove `a` (this currently works)
var foo = /a+|[a-f]/; // change `a-f` to `b-f`

var foo = /a|[ab]a/; // remove `a` in `[ab]`
var foo = /a|aa|bb/; // remove `aa` (this currently works)

// ok
var foo = /c+|[a-f]/;
```

## Public acceptance behavior

Extend no-dupe-disjunctions to recognize redundant nested alternatives and individual elements of non-negated character classes, including removable range endpoints. Preserve the distinction between strict-subset redundancy and prefix coverage under JavaScript's ordered matching. Keep useful range interiors, such as /c+|[a-f]/. Handle nested groups and preserve existing capturing-group warnings and existing rule options. Diagnostic location identifies the removable nested element.

New diagnostics use these templates, following the rule's existing quoting/character descriptions:
- Strict subset: `Unexpected useless element. All paths of <alternative> that go through <element> are a strict subset of <covered alternatives>. This element can be removed.`
- Prefix coverage: `Unexpected useless element. All paths of <alternative> that go through <element> are already covered by <covered alternatives>. This element can be removed.`
- When that element contains capturing groups, append the existing warning: ` Careful! This alternative contains capturing groups which might be difficult to remove.`

Public rule behavior, message text and locations are part of the contract; internal algorithms and helper names are not prescribed.
