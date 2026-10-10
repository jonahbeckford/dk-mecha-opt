# Mecha DK design notes

The working files behind the Mecha DK 1.0 UI design. The design itself is a private artifact at
https://claude.ai/artifact/6uEnii5TQfwRvXp4Zk8qLY, a canvas of boards. This folder is what a later session
needs to change it.

- `canvas/project/` holds every board (`*.dc.html`) and the canvas layout (`canvas.json`), as last published.
- `gen/` holds the Python scripts that generated or edited the boards. Several derive one board from
  another: `tplform.py` and `describe.py` build the template and the description boards from
  `PIProject.dc.html`, so run them again after changing it. `stages.py` builds the stage boards.
- `check/` holds the render checks. `conv.py` turns a board into plain HTML, `w.js` lists anything wider than
  a 390 px phone screen, and `d.js` takes a full-page screenshot. Run the scripts with Playwright, for example
  `NODE_PATH=$(npm root -g) node check/w.js $PWD/out.html`.
- `dk0-learn-serves-the-mecha-dk-gui.md` is the plan of engine requests, R1 to R33. The copy that dk-engine-opt
  cycles read is on branch `engine-opt/mecha-dk-design-requests` of jonahbeckford/dk-engine-opt.
- `docs/MECHA-DK.md` drafts the security sections of `MECHA-DK.md`, a sibling of `DK0-REFERENCE.md` in
  `dksdk-coder/ext/dk/docs/`.

To publish a changed board, read the published copy first, then publish with the artifact URL, `root` set to
this folder's `canvas`, and the board under `files` as `project/<name>.dc.html`.
