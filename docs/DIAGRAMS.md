# UML Diagrams (PlantUML)

The diagrams are written in PlantUML, in the same style as the VacQ sample. Paste a `.puml` file into
https://www.plantuml.com/plantuml or open it with the VS Code PlantUML extension, then export PNG/SVG for the slides.

Ready-made images are in `img/` (PNG at 2x for slides, SVG sharp at any zoom). They are drawn by `gen_uml.py`, which reads the
sequence `.puml` files directly, so edit the `.puml` and redraw with:

```
python docs/gen_uml.py docs/img docs/puml
```

`gen_uml.py` writes SVG only. To refresh the PNGs, convert them with e.g. `magick -density 192 file.svg file.png`.
The use case and class images are laid out by hand inside `gen_uml.py` (functions `use_case` and `class_profile`).

**Red** marks what changed from Assignment 7 (VacQ). Hospital -> CoworkingSpace and Appointment -> Reservation are renames, so they are not marked.

| File | Diagram | Changed from VacQ? | Image |
|---|---|---|---|
| `puml/00-use-case.puml` | Use case diagram | Register (tel), Logout, View own, Edit own | [PNG](img/00-use-case.png) · [SVG](img/00-use-case.svg) |
| `puml/00-class-diagram.puml` | Class diagram (UML Profile: Application / Resource / Representation) | tel, openTime/closeTime, logout, get/update reservation | [PNG](img/00-class-diagram.png) · [SVG](img/00-class-diagram.svg) |
| `puml/01-auth-register.puml` | Auth (POST register) | **Yes**: tel | [PNG](img/01-auth-register.png) · [SVG](img/01-auth-register.svg) |
| `puml/02-auth-login.puml` | Auth (POST login) | **Yes**: tel in response | [PNG](img/02-auth-login.png) · [SVG](img/02-auth-login.svg) |
| `puml/03-auth-logout.puml` | Auth (GET logout) | **Yes**: now requires login | [PNG](img/03-auth-logout.png) · [SVG](img/03-auth-logout.svg) |
| `puml/04-auth-me.puml` | Auth (GET me) | No | [PNG](img/04-auth-me.png) · [SVG](img/04-auth-me.svg) |
| `puml/05-middleware-protect-authorize.puml` | protect + authorize | No | [PNG](img/05-middleware-protect-authorize.png) · [SVG](img/05-middleware-protect-authorize.svg) |
| `puml/06-coworkingspace-get-all.puml` | Manage Co-working Space (GET all) | No | [PNG](img/06-coworkingspace-get-all.png) · [SVG](img/06-coworkingspace-get-all.svg) |
| `puml/07-coworkingspace-get-one.puml` | Manage Co-working Space (GET one) | No | [PNG](img/07-coworkingspace-get-one.png) · [SVG](img/07-coworkingspace-get-one.svg) |
| `puml/08-coworkingspace-create.puml` | Manage Co-working Space (POST) | No | [PNG](img/08-coworkingspace-create.png) · [SVG](img/08-coworkingspace-create.svg) |
| `puml/09-coworkingspace-update.puml` | Manage Co-working Space (PUT) | No | [PNG](img/09-coworkingspace-update.png) · [SVG](img/09-coworkingspace-update.svg) |
| `puml/10-coworkingspace-delete.puml` | Manage Co-working Space (DELETE, cascade) | No | [PNG](img/10-coworkingspace-delete.png) · [SVG](img/10-coworkingspace-delete.svg) |
| `puml/11-reservation-get-all.puml` | Manage Reservation (GET all) | No | [PNG](img/11-reservation-get-all.png) · [SVG](img/11-reservation-get-all.svg) |
| `puml/12-reservation-get-one.puml` | Manage Reservation (GET one) | **Yes**: owner or admin only | [PNG](img/12-reservation-get-one.png) · [SVG](img/12-reservation-get-one.svg) |
| `puml/13-reservation-create.puml` | Manage Reservation (POST) | No | [PNG](img/13-reservation-create.png) · [SVG](img/13-reservation-create.svg) |
| `puml/14-reservation-update.puml` | Manage Reservation (PUT) | **Yes**: only date / space editable, new space must exist | [PNG](img/14-reservation-update.png) · [SVG](img/14-reservation-update.svg) |
| `puml/15-reservation-delete.puml` | Manage Reservation (DELETE) | No | [PNG](img/15-reservation-delete.png) · [SVG](img/15-reservation-delete.svg) |

The full code-change list is in [CHANGES_FROM_ASSIGNMENT7.md](CHANGES_FROM_ASSIGNMENT7.md).
