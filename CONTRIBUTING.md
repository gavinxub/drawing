How to contribute to Drawing

- [If you find a bug](#bug-report)
- [If you want a new feature](#feature-request)
- [If you want to translate the app](#translating)
- [If you want to fix a bug or to add a new feature](#contribute-to-the-code)

----

# Bug report

Usability and design issues concerning existing features are bugs.

- If you can, try to **check if it hasn't already been fixed but not released**.
- Report it with informations required by the adequate issue template.

----

# Feature request

Usability and design issues concerning existing features are **not** new features.

- If you can, try to **check if it hasn't already been added but not released**.
- Report it with informations required by the adequate issue template.
- In the report, explain what it does, not how it does it.
- Is it…
	- a general feature?
	- a new standalone tool?
	- a new option for an existing tool?

----

# Translating

### If the translation doesn't exist at all

- Fork the repo and clone your fork on your disk.
- **Add your language to `po/LINGUAS`.**
- Build the app once, and then run `ninja -C _build drawing-update-po` at the root of the project. It will produce a `.po` file for your language in the `po` directory.
- Use a text editor or [an adequate app](https://flathub.org/apps/details/org.gnome.Gtranslator) to translate the strings of this `.po` file. Do not translate the app id (`com.github.maoschanz.drawing`).
- (optional) if you want to test your translation:
	- GNOME Builder isn't able to run a translated version of the app so export it as a `.flatpak` file.
	- Install it with `flatpak install path/to/that/file`.
- Run `git add . && git commit && git push`
- Submit a "pull request"/"merge request"

### If the translation exists but is incomplete

- Fork the repo and clone your fork on your disk.
- Find file corresponding to you language in the the `po` directory
- Use a text editor or [an adequate app](https://flathub.org/apps/details/org.gnome.Gtranslator) to translate the strings of this `.po` file. Do not translate the app id (`com.github.maoschanz.drawing`).
- If you want to test your translation:
	- GNOME Builder isn't able to run a translated version of the app so export it as a `.flatpak` file.
	- Install it with `flatpak install path/to/that/file`.
- Run `git add . && git commit && git push`
- Submit a "pull request"/"merge request"

----

# Contribute to the code

- The issue has to be reported first
- Easy issues are tagged "**good first issue**"
- Tell on the issue that you'll try to fix it

**If you find some bullshit in the code, or don't understand it, feel free to
ask me about it.**

### Syntax

- Use tabs in `.py` files.
- Use 2 spaces in `.ui` or `.xml` files.
- Try to not write lines longer than 80 characters.
- In the python code, use double quotes for strings the user might see, and
single quotes otherwise (paths, constants, enumerations, dict keys, …)
- Good comments explain *why* the code does what it does. If a comment explains
*what* it does, the comment is useless, or the code is bad.

I like `GAction`s and i've added wrapper methods for using them, try to use that
instead of directly connecting buttons/menu-items to a method.

### UI design

Concerning UI design, try to respect [GNOME Human Interface Guidelines](https://developer.gnome.org/hig/stable/)
as much as possible, while making your feature available from the menubar. The
menubar is hidden in most cases, but it should contains as many `GAction`s as
possible for testing purposes (and also because searchable menus still exist).
If you're contributing to an alternative layout ("elementary OS", "Cinnamon", or
any other), just be sure to not hurt the UX with the GNOME layout (since it's
the one used on smartphone, be careful it has to stay very resizable).

### Explanation of the code

The `data` directory contains data useless to the execution (app icons, desktop
launcher, settings schemas, appdata, …).

According to some people, it should contain the UI resources, but i don't care:
resources used by the app (`.ui` files, in-app icons, …) are in `src`, along
with the python code.

In my opinion, the complexity of the code comes mainly from 2 points:

- tools are window-wide, while the operations they produce, which are stored in
the history, are image-wide.
- the interactions with the selection are ridiculously complex and numerous
_(defining, explicit applying, explicit canceling, import, clipboard methods,
use by other tools (cancelled or confirmed), deletion, implicit applying,
implicit canceling, …)_ which can easily create small bugs.


##### The application itself

`main.py` defines the application, which has:

- implementations of CLI handling methods
- some `GioAction`s
- a preferences window (`preferences.py`)
- a menubar (hidden with most layouts)
- an appmenu (for GNOME Shell ≤ 3.30)
- dialogs (about, shortcuts)
- several **windows**

`window.py` defines a GtkApplicationWindow:

- some `GioAction`s
- a "properties" dialog (`properties.py`). It depends on the window despite
showing image-wide infos.
- a window's decorations can change quite a lot, which is mostly handled by
`deco_manager.py`. Three classes are defined in this file:
	- `DrDecoManagerMenubar` just hides or shows the menubar. Most of its
	methods are empty.
	- `DrDecoManagerToolbar` loads a toolbar from an UI file. This class extends
	`DrDecoManagerMenubar`, and will manage a small "hamburger menu" at the end
	of the toolbar if the menubar is hidden.
	- `DrDecoManagerHeaderbar` loads a headerbar from an UI file. This class
	extends `DrDecoManagerMenubar` but the menubar will always stay hidden.
	It handles how widgets are shown or hidden depending on the size of the
	window, and will display various menus depending on the visibility of the
	buttons, to ensure all features are always available.
- a window has several **tools**
- a window has several **images**
- `minimap.py` for the minimap, which shows a thumbnail of the currently opened image.
- each window has an **options_manager** (`options_manager.py`). It will display
the correct bottom bar (= the one required by the current **tool**) and manage
tools' options. All bottom options bars can be found in the sub-directories of
`src/optionsbars/`, and are specialized from `src/optionsbars/abstract_optionsbar.py`

`image.py` defines an image, which contains:

- an "undo" history and a "redo" history
- a selection, managed by `selection_manager.py`
- a `GdkPixbuf.Pixbuf` (as an attribute), named `main_pixbuf`, which corresponds
to the current state of the edited image.

##### The tools

The tools are managed by a bunch of files in the `src/tools` directory.

>The relationship between the window and the tools is a
**[State](https://en.wikipedia.org/wiki/State_pattern)** design pattern.

The active tool's methods are called from the window's (or the current image's)
code regardless of what tool is active. To achieve that, all tools inherit from
**abstract** classes defining common methods.

First of all, `src/tools/abstract_tool.py` defines how the tool will be added in
the UI, provides several wrappers to add options, to access the pixbufs, to add
an operation to the edition history, etc. Other common features, when they don't
depend on the image or the tool at all (such as blurring, computing some paths,
displaying an overlay on the image (for the selection for example)), may be
provided by one of the `src/tools/utilities_*.py` files.

Then, an other layer of abstract classes is used, depending on the subcategory a
tool is in:

- the classic tools, draw on the main pixbuf using **`cairo`**
- the selection tools translates the user's input into operations using the
image's **selection_manager**. These operations are quite complex, and are
almost entirely managed in `abstract_select.py`.
- the "canvas tools" (scale/crop/rotate/filters/…) can be applied to the
selection pixbuf or the main pixbuf, and will use the image's `temp_pixbuf`
attribute to store a preview of their changes. These tools have to be
explicitely applied by the user.

### UML diagrams

TODO

<!-- ![UML diagrams](docs/uml.png) -->

----

