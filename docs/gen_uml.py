"""Generate UML diagrams (use case, class, sequence) as standalone SVG files."""
import os
import sys
from html import escape

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)

FONT = "Arial, Helvetica, sans-serif"
INK = "#1f2933"
LINE = "#334155"
FILL = "#fffbea"
HEAD = "#fde68a"


def tw(s, size=13, bold=False):
    w = 0.0
    for ch in s:
        if ch in "il.,:;'|!()[]{} ":
            w += 0.30
        elif ch in "mwMW@":
            w += 0.85
        elif ch.isupper():
            w += 0.68
        else:
            w += 0.56
    return w * size * (1.07 if bold else 1.0)


RED = "#c81e1e"


def chg(s):
    """Strings starting with '!' mark something changed from Assignment 7 (VacQ)."""
    if s.startswith("!!"):          # escaped: a literal "!" that is not a red marker
        return (False, s[1:])
    return (True, s[1:]) if s.startswith("!") else (False, s)


def text(x, y, s, size=13, anchor="start", bold=False, italic=False, halo=False, fill=INK):
    changed, s = chg(s)
    if changed:
        fill, bold = RED, True
    attrs = f'x="{x:.1f}" y="{y:.1f}" font-size="{size}" text-anchor="{anchor}" fill="{fill}"'
    if bold:
        attrs += ' font-weight="bold"'
    if italic:
        attrs += ' font-style="italic"'
    out = f"<text {attrs}>{escape(s)}</text>"
    if halo:
        w = tw(s, size, bold) + 6
        x0 = x - 3 if anchor == "start" else (x - w / 2 if anchor == "middle" else x - w + 3)
        out = f'<rect x="{x0:.1f}" y="{y-size:.1f}" width="{w:.1f}" height="{size+5}" fill="#ffffff"/>' + out
    return out


def legend(x, y):
    return []
    return [
        f'<rect x="{x}" y="{y-12}" width="14" height="14" fill="#fee2e2" stroke="{RED}" stroke-width="1.5"/>',
        text(x + 20, y, "Red = changed or new compared with Assignment 7 (VacQ). Hospital → CoworkingSpace, Appointment → Reservation.", size=12, fill="#475569"),
    ]


DEFS = f"""<defs>
<marker id="filled" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="10" markerHeight="10" orient="auto-start-reverse" markerUnits="userSpaceOnUse">
  <path d="M0,0 L10,5 L0,10 z" fill="{LINE}"/></marker>
<marker id="open" viewBox="0 0 12 12" refX="11" refY="6" markerWidth="12" markerHeight="12" orient="auto-start-reverse" markerUnits="userSpaceOnUse">
  <path d="M0,0 L11,6 L0,12" fill="none" stroke="{LINE}" stroke-width="1.4"/></marker>
<marker id="hollow" viewBox="0 0 16 16" refX="15" refY="8" markerWidth="16" markerHeight="16" orient="auto-start-reverse" markerUnits="userSpaceOnUse">
  <path d="M1,1 L15,8 L1,15 z" fill="#ffffff" stroke="{LINE}" stroke-width="1.4"/></marker>
<marker id="filledR" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="10" markerHeight="10" orient="auto-start-reverse" markerUnits="userSpaceOnUse">
  <path d="M0,0 L10,5 L0,10 z" fill="{RED}"/></marker>
<marker id="openR" viewBox="0 0 12 12" refX="11" refY="6" markerWidth="12" markerHeight="12" orient="auto-start-reverse" markerUnits="userSpaceOnUse">
  <path d="M0,0 L11,6 L0,12" fill="none" stroke="{RED}" stroke-width="1.6"/></marker>
</defs>"""


def save(name, w, h, body, title):
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w:.0f}" height="{h:.0f}" '
        f'viewBox="0 0 {w:.0f} {h:.0f}" font-family="{FONT}">\n{DEFS}\n'
        f'<rect width="100%" height="100%" fill="#ffffff"/>\n'
        + text(16, 26, title, size=16, bold=True)
        + "\n"
        + "\n".join(body)
        + "\n</svg>\n"
    )
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(svg)
    print("wrote", name, int(w), "x", int(h))


def actor(x, y, label):
    """Stick figure centred at (x, y) = hip; label below."""
    s = LINE
    return [
        f'<circle cx="{x}" cy="{y-32}" r="10" fill="#ffffff" stroke="{s}" stroke-width="1.6"/>',
        f'<line x1="{x}" y1="{y-22}" x2="{x}" y2="{y+8}" stroke="{s}" stroke-width="1.6"/>',
        f'<line x1="{x-16}" y1="{y-12}" x2="{x+16}" y2="{y-12}" stroke="{s}" stroke-width="1.6"/>',
        f'<line x1="{x}" y1="{y+8}" x2="{x-13}" y2="{y+32}" stroke="{s}" stroke-width="1.6"/>',
        f'<line x1="{x}" y1="{y+8}" x2="{x+13}" y2="{y+32}" stroke="{s}" stroke-width="1.6"/>',
        text(x, y + 52, label, size=13, anchor="middle", bold=True),
    ]


# ---------------------------------------------------------------- use case
def use_case():
    b = []
    sys_x0, sys_x1, sys_y0, sys_y1 = 230, 1010, 56, 740
    b.append(f'<rect x="{sys_x0}" y="{sys_y0}" width="{sys_x1-sys_x0}" height="{sys_y1-sys_y0}" fill="#f8fafc" stroke="{LINE}" stroke-width="1.6"/>')
    b.append(text((sys_x0 + sys_x1) / 2, sys_y0 + 24, "Co-working Space Reservation System", size=15, anchor="middle", bold=True))

    ell = {}

    def uc(key, cx, cy, label):
        changed, label = chg(label)
        lines = label.split("\n")
        rx = max(tw(l, 13, changed) for l in lines) / 2 + 26
        ry = 22 if len(lines) == 1 else 28
        ell[key] = (cx, cy, rx, ry)
        fill, stroke, sw = ("#fee2e2", RED, 2.2) if changed else (FILL, LINE, 1.4)
        b.append(f'<ellipse cx="{cx}" cy="{cy}" rx="{rx:.1f}" ry="{ry}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')
        y0 = cy + 5 - (len(lines) - 1) * 8
        for i, l in enumerate(lines):
            b.append(text(cx, y0 + i * 16, ("!" if changed else "") + l, anchor="middle"))

    L, R = 440, 800
    guest = [("reg", "!Register\n(name, tel, email, password)"), ("login", "Login"),
             ("list", "View co-working space list"), ("detail", "View co-working space detail")]
    user = [("logout", "Logout (now requires login)"), ("me", "View own profile"),
            ("reserve", "Reserve a co-working space\n(max 3 reservations)"),
            ("vown", "View own reservations\n(detail is owner-only)"), ("eown", "Edit own reservation\n(date / space only)"),
            ("down", "Delete own reservation")]
    admin = [("vany", "View any reservation\n(all, or by space)"), ("eany", "Edit any reservation"),
             ("dany", "Delete any reservation"), ("manage", "Create / update / delete\nco-working space"),
             ("nolimit", "Reserve without\n3-reservation limit")]
    for i, (k, t) in enumerate(guest):
        uc(k, L, 118 + i * 64, t)
    for i, (k, t) in enumerate(user):
        uc(k, L, 392 + i * 64, t)
    for i, (k, t) in enumerate(admin):
        uc(k, R, 330 + i * 76, t)

    # «extend» from no-limit to reserve
    cx, cy, rx, ry = ell["nolimit"]
    tx, ty, trx, try_ = ell["reserve"]
    b.append(f'<line x1="{cx-rx:.1f}" y1="{cy:.1f}" x2="{tx+trx:.1f}" y2="{ty:.1f}" stroke="{LINE}" stroke-width="1.3" stroke-dasharray="6 4"/>')
    b.append(arrowhead(cx - rx, cy, tx + trx, ty, "open"))
    b.append(text((cx - rx + tx + trx) / 2, (cy + ty) / 2 - 8, "«extend»", size=12, anchor="middle", italic=True, halo=True))

    gx, gy = 110, 230
    ux, uy = 110, 545
    ax, ay = 1120, 520
    b += actor(gx, gy, "Guest")
    b += actor(ux, uy, "User")
    b += actor(ax, ay, "Admin")

    def assoc(x, y, key, side):
        cx, cy, rx, ry = ell[key]
        ex = cx - rx if side == "L" else cx + rx
        b.append(f'<line x1="{x}" y1="{y}" x2="{ex:.1f}" y2="{cy}" stroke="{LINE}" stroke-width="1.2"/>')

    for k, _ in guest:
        assoc(gx + 22, gy - 12, k, "L")
    for k, _ in user:
        assoc(ux + 22, uy - 12, k, "L")
    for k, _ in admin:
        assoc(ax - 22, ay - 12, k, "R")

    # generalization: User -> Guest, Admin -> User
    b.append(f'<line x1="{ux}" y1="{uy-44}" x2="{gx}" y2="{gy+62}" stroke="{LINE}" stroke-width="1.4"/>')
    b.append(arrowhead(ux, uy - 44, gx, gy + 62, "hollow"))
    b.append(f'<polyline points="{ax},{ay+62} {ax},{sys_y1+30} {ux},{sys_y1+30} {ux},{uy+62}" fill="none" stroke="{LINE}" stroke-width="1.4"/>')
    b.append(arrowhead(ux, sys_y1 + 30, ux, uy + 62, "hollow"))
    b.append(text((ax + ux) / 2, sys_y1 + 24, "Admin inherits every User use case; User inherits Guest browsing", size=12, anchor="middle", italic=True, fill="#475569"))
    b += legend(16, sys_y1 + 64)
    save("00-use-case.svg", 1200, sys_y1 + 80, b, "Use Case Diagram")


# ---------------------------------------------------------------- class boxes
class Box:
    def __init__(self, name, stereo=None, attrs=(), ops=(), abstract=False):
        self.name, self.stereo, self.attrs, self.ops = name, stereo, list(attrs), list(ops)
        lines = [tw(chg(a)[1], 13, chg(a)[0]) for a in self.attrs + self.ops] + [tw(name, 14, True)]
        if stereo:
            lines.append(tw(f"«{stereo}»", 12))
        self.w = max(lines) + 24
        self.hh = 44 if stereo else 30
        self.ah = max(len(self.attrs), 0) * 18 + (10 if self.attrs else 10)
        self.oh = max(len(self.ops), 0) * 18 + (10 if self.ops else 10)
        self.h = self.hh + self.ah + self.oh
        self.x = self.y = 0

    def at(self, x, y):
        self.x, self.y = x, y
        return self

    @property
    def cx(self):
        return self.x + self.w / 2

    @property
    def cy(self):
        return self.y + self.h / 2

    def svg(self):
        x, y, w = self.x, self.y, self.w
        o = [f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{self.h:.1f}" fill="{FILL}" stroke="{LINE}" stroke-width="1.5"/>',
             f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{self.hh:.1f}" fill="{HEAD}" stroke="{LINE}" stroke-width="1.5"/>']
        ty = y + 20
        if self.stereo:
            o.append(text(x + w / 2, ty - 2, f"«{self.stereo}»", size=12, anchor="middle", italic=True))
            ty += 16
        o.append(text(x + w / 2, ty, self.name, size=14, anchor="middle", bold=True))
        y1 = y + self.hh
        o.append(f'<line x1="{x:.1f}" y1="{y1+self.ah:.1f}" x2="{x+w:.1f}" y2="{y1+self.ah:.1f}" stroke="{LINE}" stroke-width="1.2"/>')
        for i, a in enumerate(self.attrs):
            o.append(text(x + 10, y1 + 18 + i * 18, a))
        y2 = y1 + self.ah
        for i, m in enumerate(self.ops):
            o.append(text(x + 10, y2 + 18 + i * 18, m))
        return o


def clip(box, tx, ty):
    """Point where the line from the box centre towards (tx, ty) leaves the box."""
    cx, cy = box.cx, box.cy
    dx, dy = tx - cx, ty - cy
    if dx == 0 and dy == 0:
        return cx, cy
    sx = (box.w / 2) / abs(dx) if dx else 1e9
    sy = (box.h / 2) / abs(dy) if dy else 1e9
    s = min(sx, sy)
    return cx + dx * s, cy + dy * s


def arrowhead(x1, y1, x2, y2, kind="filled", color=LINE):
    """Arrow tip at (x2, y2), pointing along the line from (x1, y1).
    Drawn as plain shapes (not SVG markers) so every renderer orients it the same way."""
    import math
    a = math.atan2(y2 - y1, x2 - x1)
    length, half = {"filled": (10, 5), "open": (11, 6), "hollow": (15, 8)}[kind]
    bx, by = x2 - length * math.cos(a), y2 - length * math.sin(a)
    px, py = -math.sin(a) * half, math.cos(a) * half
    pts = f"{bx+px:.1f},{by+py:.1f} {x2:.1f},{y2:.1f} {bx-px:.1f},{by-py:.1f}"
    if kind == "filled":
        return f'<polygon points="{pts}" fill="{color}"/>'
    if kind == "open":
        return f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="1.5"/>'
    return f'<polygon points="{pts}" fill="#ffffff" stroke="{color}" stroke-width="1.4"/>'


def edge(a, b, kind="assoc", label=None, m1=None, m2=None, label_at=0.5):
    x1, y1 = clip(a, b.cx, b.cy)
    x2, y2 = clip(b, a.cx, a.cy)
    style = f'stroke="{LINE}" stroke-width="1.4"'
    if kind == "dep":
        style += ' stroke-dasharray="7 4"'
    o = [f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" {style}/>']
    if kind in ("dep", "nav"):
        o.append(arrowhead(x1, y1, x2, y2, "open"))
    if label:
        lx, ly = x1 + (x2 - x1) * label_at, y1 + (y2 - y1) * label_at
        o.append(text(lx, ly - 6, label, size=12, anchor="middle", italic=True, halo=True))
    for (px, py, qx, qy, m) in ((x1, y1, x2, y2, m1), (x2, y2, x1, y1, m2)):
        if m:
            dx, dy = qx - px, qy - py
            d = (dx * dx + dy * dy) ** 0.5 or 1
            mx, my = px + dx / d * 22, py + dy / d * 22
            o.append(text(mx, my - 8, m, size=13, anchor="middle", bold=True, halo=True))
    return o


def class_profile():
    app = Box("CoworkingSpaceService", "Application", ["+ baseURL = /api/v1"], [])
    auth = Box("Auth", "Resource", [], [
        "!«POST» +register(name, tel, email, password): token",
        "«POST» +login(email, password): token",
        "«GET» +getMe(): User",
        "«GET» +logout(): void  {login required}",
    ])
    spaces = Box("CoworkingSpaces", "Resource", [], [
        "«GET» +getCoworkingSpaces(): CoworkingSpace[]",
        "«POST» +createCoworkingSpace(): CoworkingSpace  {admin}",
    ])
    space = Box("CoworkingSpace", "Resource", [], [
        "«GET» +getCoworkingSpace(): CoworkingSpace",
        "«PUT» +updateCoworkingSpace(): CoworkingSpace  {admin}",
        "«DELETE» +deleteCoworkingSpace(): void  {admin}",
    ])
    resvs = Box("Reservations", "Resource", [], [
        "«GET» +getReservations(): Reservation[]",
        "«POST» +addReservation(reservationDate): Reservation",
    ])
    resv = Box("Reservation", "Resource", [], [
        "«GET» +getReservation(): Reservation  {owner or admin}",
        "«PUT» +updateReservation(reservationDate, coworkingSpace): Reservation",
        "«DELETE» +deleteReservation(): void",
    ])
    r_user = Box("User", "Representation", [
        "- name : String",
        "- email : String",
        "!- tel : String",
        "- role : String = user",
        "- password : String",
        "- createdAt : Date",
    ], [])
    r_space = Box("CoworkingSpace", "Representation", [
        "- name : String",
        "- address : String",
        "- tel : String  {required}",
        "!- openTime : String  (HH:mm)",
        "!- closeTime : String  (HH:mm)",
    ], [])
    r_resv = Box("Reservation", "Representation", [
        "- reservationDate : Date",
        "- user : User",
        "- coworkingSpace : CoworkingSpace",
        "- createdAt : Date",
    ], [])

    gap = 70
    cols = [[auth, r_user], [spaces, space, r_space], [resvs, resv, r_resv]]
    colw = [max(bx.w for bx in c) for c in cols]
    xs, x = [], 30
    for w in colw:
        xs.append(x)
        x += w + gap
    W = x - gap + 30
    y1 = 200
    y2 = y1 + max(auth.h, spaces.h, resvs.h) + 90
    y3 = y2 + max(space.h, resv.h) + 90
    for ci, (bx, y) in enumerate([(auth, y1), (spaces, y1), (resvs, y1)]):
        bx.at(xs[ci] + (colw[ci] - bx.w) / 2, y)
    for ci, bx in ((1, space), (2, resv)):
        bx.at(xs[ci] + (colw[ci] - bx.w) / 2, y2)
    for ci, bx in ((0, r_user), (1, r_space), (2, r_resv)):
        bx.at(xs[ci] + (colw[ci] - bx.w) / 2, y3)
    app.at((W - app.w) / 2, 50)

    b = []
    for bx in (app, auth, spaces, space, resvs, resv, r_user, r_space, r_resv):
        b += bx.svg()
    b += edge(app, auth, "nav", "/auth")
    b += edge(app, spaces, "nav", "/coworkingspaces")
    b += edge(app, resvs, "nav", "/reservations")
    b += edge(spaces, space, "nav", "/{coworkingSpaceId}")
    b += edge(resvs, resv, "nav", "/{reservationId}")
    b += edge(space, resvs, "nav", "/reservations", label_at=0.55)
    b += edge(auth, r_user, "dep", "«use»", label_at=0.5)
    b += edge(space, r_space, "dep", "«use»")
    b += edge(resv, r_resv, "dep", "«use»")
    b += edge(r_space, r_resv, "assoc", None, "1", "0..*")
    # User 1 -- 0..3 Reservation, routed under the representations
    yb = y3 + max(r_user.h, r_space.h, r_resv.h) + 30
    ux, rx = r_user.cx, r_resv.cx
    b.append(f'<polyline points="{ux},{r_user.y + r_user.h} {ux},{yb} {rx},{yb} {rx},{r_resv.y + r_resv.h}" fill="none" stroke="{LINE}" stroke-width="1.4"/>')
    b.append(text(ux + 8, r_user.y + r_user.h + 18, "1", bold=True))
    b.append(text(rx + 8, r_resv.y + r_resv.h + 18, "0..3", bold=True))
    b.append(text((ux + rx) / 2, yb - 6, "makes", size=12, anchor="middle", italic=True, halo=True))
    b.append(text(r_space.x, r_space.y + r_space.h + 18, "removed: district, province, postalcode, region", size=12, italic=True, fill="#475569"))
    H = yb + 70
    b.append(text(30, H - 36, "0..3 applies to role = user. Admins have no limit. Deleting a CoworkingSpace also deletes its reservations.", size=12, italic=True, fill="#475569"))
    b += legend(30, H - 14)
    save("00-class-diagram.svg", W, H, b, "Class Diagram (UML Profile)")



# ---------------------------------------------------------------- sequence diagrams read from .puml
import glob
import re

COLOR_TAG = re.compile(r"</?color[^>]*>")
ARROW = re.compile(r"^(\w+)\s*(<)?(-{1,2})(?:\[#(\w+)\])?(-?)(>)?\s*(\w+)\s*(\+\+|--)?\s*(?::(.*))?$")
DECL = re.compile(r'^(participant|database|actor)\s+"(.*)"\s+as\s+(\w+)')


def clean(s):
    """Return (is_red, plain text)."""
    red = "<color:red>" in s
    return red, COLOR_TAG.sub("", s).strip()


def mark(red, s):
    if red:
        return "!" + s
    return ("!" + s) if s.startswith("!") else s   # "!!x" = literal "!x", not red


def parse_puml(path):
    parts, title, header, legend_lines = [], "", "", []
    root = []
    stack = [root]          # list of event lists currently being appended to
    frames = []             # open frames: [op, sections]
    in_legend = False
    for raw in open(path, encoding="utf-8"):
        line = raw.strip()
        if in_legend:
            if line == "endlegend":
                in_legend = False
            else:
                legend_lines.append(clean(line))
            continue
        if not line or line.startswith("'") or line.startswith("@") or line.startswith("skinparam") or line.startswith("footer"):
            continue
        if line.startswith("legend"):
            in_legend = True
            continue
        if line.startswith("title "):
            title = line[6:].strip().strip('"')
            continue
        if line.startswith("header "):
            header = line[7:].strip()
            continue
        m = DECL.match(line)
        if m:
            kind, label, pid = m.groups()
            lines = [mark(*clean(l.replace("<<", "«").replace(">>", "»"))) for l in label.split("\\n")]
            parts.append((pid, lines, kind))
            continue
        word = line.split(" ", 1)
        if word[0] in ("alt", "opt"):
            g = clean(word[1] if len(word) > 1 else "")
            fr = [word[0], [(mark(*g), [])]]
            frames.append(fr)
            stack[-1].append(("frame", fr))
            stack.append(fr[1][-1][1])
            continue
        if word[0] == "else":
            g = clean(word[1] if len(word) > 1 else "")
            stack.pop()
            frames[-1][1].append((mark(*g), []))
            stack.append(frames[-1][1][-1][1])
            continue
        if line == "end":
            stack.pop()
            frames.pop()
            continue
        if word[0] in ("activate", "deactivate"):
            stack[-1].append(("act", word[1].strip(), word[0] == "activate"))
            continue
        m = ARROW.match(line)
        if m:
            a, rev, d1, color, d2, head, b, act, label = m.groups()
            red_l, text_l = clean(label or "")
            red = red_l or (color or "").lower() == "red"
            dashed = len(d1) + len(d2) >= 2
            src, dst = (b, a) if rev else (a, b)
            stack[-1].append(("msg", src, dst, mark(red, text_l), red, dashed, act))
            continue
        raise ValueError(f"{path}: cannot parse line: {line}")
    return parts, title, header, legend_lines, root


def walk(events, depth=0):
    for e in events:
        if e[0] == "frame":
            for g, sub in e[1][1]:
                yield ("guard", g, depth)
                yield from walk(sub, depth + 1)
        else:
            yield e


def cylinder(x, y, w, h):
    l, rx = x - w / 2, w / 2
    return [
        f'<path d="M{l:.1f},{y+7} a{rx:.1f},7 0 0,0 {w:.1f},0 v{h-14} a{rx:.1f},7 0 0,1 {-w:.1f},0 z" fill="{HEAD}" stroke="{LINE}" stroke-width="1.5"/>',
        f'<ellipse cx="{x:.1f}" cy="{y+7}" rx="{rx:.1f}" ry="7" fill="{HEAD}" stroke="{LINE}" stroke-width="1.5"/>',
    ]


def render_sequence(path, outdir):
    parts, title, header, legend_lines, events = parse_puml(path)
    idx = {p[0]: i for i, p in enumerate(parts)}
    widths = [max(max(tw(chg(l)[1], 13, True) for l in lines) + 26, 90) for _, lines, _ in parts]

    xs = []
    for i, w in enumerate(widths):
        xs.append(30 + w / 2 if i == 0 else xs[-1] + widths[i - 1] / 2 + 30 + w / 2)

    flat = list(walk(events))
    cons = []
    for e in flat:
        if e[0] != "msg":
            continue
        i, j = idx[e[1]], idx[e[2]]
        need = tw(chg(e[3])[1], 13, e[4]) + (70 if i == j else 40)
        i, j = (i, i + 1) if i == j else sorted((i, j))
        cons.append((i, j, need))
    cons.sort(key=lambda c: c[1] - c[0])
    for i, j, need in cons:
        if j >= len(xs):
            continue
        d = need - (xs[j] - xs[i])
        if d > 0:
            for k in range(j, len(xs)):
                xs[k] += d

    W = xs[-1] + widths[-1] / 2 + 30
    for e in flat:
        if e[0] == "msg" and e[1] == e[2] and idx[e[1]] == len(xs) - 1:
            W = max(W, xs[-1] + tw(chg(e[3])[1], 13, True) + 90)
        if e[0] == "guard":
            W = max(W, 30 + e[2] * 12 + 60 + tw(chg(e[1])[1], 12, True) + 40)
    W = max(W, 30 + tw(title, 16, True) + 40, 30 + tw(header, 11) + 40)
    for red, s in legend_lines:
        W = max(W, tw(s, 12, red) + 70)

    top = 52
    hh = 46
    life_y0 = top + hh
    b_back, b_act, b_front = [], [], []
    stacks = {p[0]: [] for p in parts}
    y = life_y0 + 14

    def right_edge(p):
        n = len(stacks[p])
        return 5 + 5 * (n - 1) if n else 0

    def left_edge(p):
        return 5 if stacks[p] else 0

    def close_bar(p, yend):
        if not stacks[p]:
            return
        lvl = len(stacks[p]) - 1
        y0 = stacks[p].pop()
        x = xs[idx[p]] - 5 + lvl * 5
        b_act.append(f'<rect x="{x:.1f}" y="{y0:.1f}" width="10" height="{max(yend - y0, 8):.1f}" fill="#ffffff" stroke="{LINE}" stroke-width="1.2"/>')

    def run(evs, depth):
        nonlocal y
        for e in evs:
            if e[0] == "frame":
                op, sections = e[1]
                left, right = 12 + depth * 12, W - 12 - depth * 12
                y0 = y
                y += 4
                seps = []
                for si, (guard, sub) in enumerate(sections):
                    if si > 0:
                        seps.append(y)
                        y += 4
                    if guard:
                        gc, gt = chg(guard)
                        gx = left + 56 if si == 0 else left + 10
                        b_front.append(text(gx, y + 15, mark(gc, f"[{gt}]"), size=12, italic=True, halo=True, fill="#7c2d12"))
                    y += 24
                    run(sub, depth + 1)
                    y += 4
                y += 4
                b_back.append(f'<rect x="{left}" y="{y0}" width="{right-left}" height="{y-y0}" fill="none" stroke="#64748b" stroke-width="1.2"/>')
                b_back.append(f'<path d="M{left},{y0} h44 v12 l-8,8 h-36 z" fill="#e2e8f0" stroke="#64748b" stroke-width="1.2"/>')
                b_front.append(text(left + 6, y0 + 15, op, size=12, bold=True))
                for sy in seps:
                    b_back.append(f'<line x1="{left}" y1="{sy}" x2="{right}" y2="{sy}" stroke="#64748b" stroke-width="1.2" stroke-dasharray="6 4"/>')
                y += 10
            elif e[0] == "act":
                _, p, on = e
                if on:
                    stacks[p].append(y)
                else:
                    close_bar(p, y)
            elif e[0] == "msg":
                _, a, c, label, red, dashed, act = e
                col, sfx, sw = (RED, "R", 2.0) if red else (LINE, "", 1.4)
                dash = ' stroke-dasharray="6 4"' if dashed else ""
                tip = "open" if dashed else "filled"
                y += 4
                ay = y + 20
                xa, xc = xs[idx[a]], xs[idx[c]]
                if a == c:
                    x0 = xa + right_edge(a)
                    b_front.append(text(x0 + 6, y + 12, label, size=13, halo=True))
                    if act == "++":
                        stacks[c].append(ay + 16)
                    x1 = xa + right_edge(a)
                    b_front.append(f'<polyline points="{x0:.1f},{ay} {x0+34:.1f},{ay} {x0+34:.1f},{ay+16} {x1:.1f},{ay+16}" fill="none" stroke="{col}" stroke-width="{sw}"{dash}/>')
                    b_front.append(arrowhead(x0 + 34, ay + 16, x1, ay + 16, tip, col))
                    if act == "--":
                        close_bar(a, ay + 16)
                    y += 44
                    continue
                b_front.append(text((xa + xc) / 2, y + 12, label, size=13, anchor="middle", halo=True))
                if act == "++":
                    stacks[c].append(ay)
                going_right = xc > xa
                sx = xa + right_edge(a) if going_right else xa - left_edge(a)
                ex = xc - left_edge(c) if going_right else xc + right_edge(c)
                b_front.append(f'<line x1="{sx:.1f}" y1="{ay}" x2="{ex:.1f}" y2="{ay}" stroke="{col}" stroke-width="{sw}"{dash}/>')
                b_front.append(arrowhead(sx, ay, ex, ay, tip, col))
                if act == "--":
                    close_bar(a, ay)
                y += 30

    run(events, 0)
    y += 6
    for p in stacks:
        while stacks[p]:
            close_bar(p, y)
    y_end = y + 10

    heads = []
    for (pid, lines, kind), x, w in zip(parts, xs, widths):
        b_back.insert(0, f'<line x1="{x:.1f}" y1="{life_y0}" x2="{x:.1f}" y2="{y_end}" stroke="#94a3b8" stroke-width="1.2" stroke-dasharray="5 5"/>')
        if kind == "database":
            heads += cylinder(x, top, w, hh)
        else:
            heads.append(f'<rect x="{x-w/2:.1f}" y="{top}" width="{w:.1f}" height="{hh}" fill="{HEAD}" stroke="{LINE}" stroke-width="1.5"/>')
        ty = top + (hh / 2 + 5) - (len(lines) - 1) * 8 + (4 if kind == "database" else 0)
        for k, l in enumerate(lines):
            italic = l.startswith("«")
            heads.append(text(x, ty + k * 16, l, size=12 if italic else 13, anchor="middle", bold=not italic, italic=italic))

    tail = []
    ly = y_end + 26
    legend_lines = []
    if False:
        lh = len(legend_lines) * 17 + 12
        lw = max(tw(s, 12, r) for r, s in legend_lines) + 24
        tail.append(f'<rect x="16" y="{ly-14}" width="{lw:.1f}" height="{lh}" fill="#fffbea" stroke="#94a3b8"/>')
        for k, (r, s) in enumerate(legend_lines):
            tail.append(text(28, ly + 4 + k * 17, mark(r, s), size=12, fill="#475569"))
        ly += lh + 6
    elif False and any(e[0] == "msg" and e[4] for e in flat) or any(e[0] == "guard" and chg(e[1])[0] for e in flat):
        tail += legend(16, ly)
        ly += 14

    name = os.path.splitext(os.path.basename(path))[0] + ".svg"
    save(name, W, ly + 12, b_back + b_act + heads + b_front + tail, title)


use_case()
class_profile()
for f in sorted(glob.glob(os.path.join(sys.argv[2], "*.puml"))):
    if os.path.basename(f).startswith("00-"):
        continue
    render_sequence(f, OUT)
