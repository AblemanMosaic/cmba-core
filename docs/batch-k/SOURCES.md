# Sources and interpretation boundaries

The user-selected program is docs/PROGRAM-I-L.md and the frozen J handoff in history/j1.
The recovered CMBA transcript and seven-document assessment remain exact source material under
sources/. Their descriptions motivate workbench capabilities; they do not certify implementation.
The native DKN baseline is pinned by its exact source/wheel hashes under baseline/dkn.

External primary references checked during construction:

* Python documentation, tkinter threading model: event handlers should remain responsive and
  long-running work should not monopolize the Tk event loop. The implementation keeps rendering
  and confirmation on the main thread, with one fixed-handler worker.
  https://docs.python.org/3/library/tkinter.html#threading-model
* Python documentation, os.open, os.link, os.fsync, dir_fd support and platform differences.
  These describe primitives, not proof of our host algorithm or every filesystem's behavior.
  https://docs.python.org/3/library/os.html

The actual executed Python/OS/Tk versions are recorded in replay receipts. The web documentation's
current version is not substituted for runtime evidence. No external source establishes complete
sandboxing, hostile-host custody, physical power-loss safety or production security of this code.
