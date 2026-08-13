# Self-contained CLI installation

A previous turn added an installer candidate. Finish it while preserving the source CLI behavior.

Requirements:

- `installer.install(target_dir)` installs a runnable copy of the CLI into an empty directory and returns the installed script path.
- From any working directory, `python <installed-script> greet Ada` prints `Hello, Ada!`.
- The installed copy must carry every runtime asset it needs; it must not read back from the source tree.
- Installation must work when the target path contains spaces.
- Keep the source command behavior and public function names.

Run `python -m unittest -v` and perform a real clean-directory install before finishing.
