# Using the integrated workbench

## Install and start

Use the supplied wheel, rather than assuming that this experimental release exists on
any package registry:

```sh
python -m pip install ./cmba_core-0.1.0a3-py3-none-any.whl
cmba-workbench
```

The pure library needs no third-party runtime package. The GUI needs Tk and a graphical
session. Signing-dependent examples need genuine cryptography 46.x. Native DKN needs
the preserved DKN wheel and its own genuine dependencies:

```sh
python -m pip install ./baseline/dkn/dkn_core-0.2.0rc5-py3-none-any.whl
```

A declared Python 3.12+ target is not evidence of execution on every version or OS.
Consult the release receipt. Use importlib.metadata.version('cmba-core') for distribution
version. The frozen cmba_core.__version__ field remains historical I1 source metadata.
The separate cmba-workbench-i1 command preserves the older inspector; installing K does
not rewrite any saved binding, namespace, vault, receipt or policy.

## A first workflow

Start on Object inspector. The initial canonical-JSON transformation is PUBLIC example
data. Its commitments are checked, but no reader policy is selected. Pressing Assess
at this point refuses with CMBA_READER_CONTEXT_REQUIRED.

Go to Context & assessments. The document's context is displayed for inspection, but
is not active. Select “Use document context — DEMO ONLY” for a demonstration. For real
work, import or edit reader-owned context and explicitly apply it. Context source
selection is not proof that the source is trustworthy: independently recognize the
intended root, signer roles, policy, evidence and time inputs.

Press Assess. The fixed evaluator runs in a single read-only worker. The table displays
every reported predicate, including missing or contradictory checks. The full result
retains authorization=EXTERNAL_DECISION_REQUIRED. Process success or a matching result
is not permission to execute, publish or save.

Each assessment adds a replayable receipt packet to the in-memory history. Change the
time in a consent example to 201 and apply the new context. Its approval may no longer
match, while its binding root remains unchanged. Select the two history entries and
choose Explain difference. Both receipts are replayed before their changed input hashes
are listed. This identifies changed inputs; it does not infer causality from hash differences.

## Pages and controls

| Page | Use |
|---|---|
| Object inspector | Read exact root, profile, committed dimensions, supplied values and typed relations. |
| Applications & capabilities | Inspect 71 recovered records, reference-only dispositions, and fixed installed capabilities. |
| Author a binding | Use a public template or current record; edit JSON data and bind a new draft. No Python is needed. |
| Context & assessments | Select reader context explicitly, evaluate, and inspect individual outcomes. |
| Relationships & compare | Compare exact bindings/contexts; inspect incoming/outgoing local edges; explicitly follow local targets. |
| Receipt history | Replay entries, compare two evaluations, and inspect full packet inputs. |
| Disclosure preview | Create a salted tree or load openings; select labels and verify the exact public view. |
| Design & realization | Assess finite combinations and their missing obligations; compare declarations without claiming equivalence. |
| Native DKN reader | Read an explicitly selected existing index/vault with supported native methods. No path is taken from a binding. |
| Local workspace & export | Choose a directory, preview exact output, approve a single create-only write, or cancel. |

Ctrl+O opens data, Ctrl+E assesses, Ctrl+S selects export, and Escape cancels pending work.
Controls are keyboard-focusable. Text panes scroll in both directions. Oversized display
previews show an explicit truncation marker; the export and verification bytes are not
taken from that clipped rendering. Accessibility on additional operating systems and
screen readers remains target-host work, not established by one Tk smoke test.

## Authoring

Select a profile and choose Public template, or copy the selected record. Edit the record
and explicit options: now, parameters, and typed relations. Bind draft makes a NEW object
in memory. It does not preserve old authority/evidence snapshots or silently carry approvals
onto changed data. It does not sign. A malformed semantic record can be structurally bound
but will be refused or contradicted by the selected evaluator; a binding is not validation.

Generic descriptions use a noncritical metadata dimension. The finite profile designer
produces data-only blueprints, not new executable plugins. Unknown input cannot import
code or register a handler. Sensitive historical domain catalogue entries remain descriptive.

## Disclosure

Create tree from entries generates fresh random salts through an explicit action. Until
saved, the private tree exists only in memory. Select public labels and enter the expected
root. A newly constructed or document-supplied root is not independently authenticated.
Preview validates all supplied openings before selecting the requested view.

Export kind disclosure serializes ONLY that verified selected view. It does not attach
the private opening set or the authoring editor. The view still discloses its root, total
leaf count, selected labels/values/salts and proof paths. It is not encryption, unlinkability,
erasure, a guarantee against dictionary attacks on badly chosen salts, or proof that the
original data collection was complete.

## Saving and reopening

Select an existing operator-owned output directory. Nothing is created merely by selecting
it. Choose a kind and a new .json basename. Prepare preview shows the exact payload and
its hash, size, target, input-state commitment and expiry. Review, approve & create file
then asks a separate host confirmation. Cancel leaves no output. Existing files are never
overwritten: use a new name. Filesystems without the required exclusive hard-link operation
refuse rather than fall back to overwriting or partial direct writes.

Bundles retain their ORIGINAL document context. They do not replace it with the reader's
selected context. A receipt packet carries the actual context used for its assessment.
A workspace snapshot carries all admitted documents and history, but no adopted trust state.
Restoring one selects neither a binding nor its reader context. Imported historical results
are labeled IMPORTED_NOT_REPLAYED, even if their stored status says MATCH.

Bundles, receipt packets and workspace snapshots can contain private information. There is
no secret scrubber or encryption. Do not treat an export label as a privacy guarantee.
Only the selected disclosure-view operation excludes its private source by construction.
Handoffs contain references only; creating one does not send it to DKN, CCP, UCM, P/PPI or
a Courthouse. Missing material must be retrieved and evaluated through a separately accepted path.

## Responsiveness and cancellation

Longer checks run in one bounded read-only worker. Cancel discards the result and invalidates
a pending export. It does not forcibly terminate a Python thread. No second worker starts
until the first exits. A timeout has the same honest distinction: the UI stops accepting the
result, but does not claim an OS-enforced CPU quota or sandbox. Every live result is tied to
its selected document generation and context; a changed selection cannot receive an old result.
