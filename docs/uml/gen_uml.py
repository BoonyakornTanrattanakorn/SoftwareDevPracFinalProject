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
    user = [("logout", "!Logout (now requires login)"), ("me", "View own profile"),
            ("reserve", "!Reserve a co-working space\n(date required, max 3)"),
            ("vown", "!View own reservations\n(detail is owner-only)"), ("eown", "!Edit own reservation\n(date / space only)"),
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
    b.append(f'<line x1="{cx-rx:.1f}" y1="{cy:.1f}" x2="{tx+trx:.1f}" y2="{ty:.1f}" stroke="{LINE}" stroke-width="1.3" stroke-dasharray="6 4" marker-end="url(#open)"/>')
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
    b.append(f'<line x1="{ux}" y1="{uy-44}" x2="{gx}" y2="{gy+62}" stroke="{LINE}" stroke-width="1.4" marker-end="url(#hollow)"/>')
    b.append(f'<polyline points="{ax},{ay+62} {ax},{sys_y1+30} {ux},{sys_y1+30} {ux},{uy+62}" fill="none" stroke="{LINE}" stroke-width="1.4" marker-end="url(#hollow)"/>')
    b.append(text((ax + ux) / 2, sys_y1 + 24, "Admin inherits every User use case; User inherits Guest browsing", size=12, anchor="middle", italic=True, fill="#475569"))
    b += legend(16, sys_y1 + 64)
    save("01-use-case.svg", 1200, sys_y1 + 80, b, "Use Case Diagram")


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


def edge(a, b, kind="assoc", label=None, m1=None, m2=None, label_at=0.5):
    x1, y1 = clip(a, b.cx, b.cy)
    x2, y2 = clip(b, a.cx, a.cy)
    style = f'stroke="{LINE}" stroke-width="1.4"'
    if kind == "dep":
        style += ' stroke-dasharray="7 4" marker-end="url(#open)"'
    elif kind == "nav":
        style += ' marker-end="url(#open)"'
    o = [f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" {style}/>']
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
        "!«GET» +logout(): void  {login required}",
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
        "!«POST» +addReservation(reservationDate): Reservation",
    ])
    resv = Box("Reservation", "Resource", [], [
        "!«GET» +getReservation(): Reservation  {owner or admin}",
        "!«PUT» +updateReservation(reservationDate, coworkingSpace): Reservation",
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
        "!- tel : String  {now required}",
        "!- openTime : String  (HH:mm)",
        "!- closeTime : String  (HH:mm)",
    ], [])
    r_resv = Box("Reservation", "Representation", [
        "!- reservationDate : Date",
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
    save("02-class-diagram-uml-profile.svg", W, H, b, "Class Diagram (UML Profile)")

# ---------------------------------------------------------------- sequence
def flatten(events):
    for e in events:
        if e[0] in ("m", "r", "s"):
            yield e
        elif e[0] == "alt":
            for _, sub in e[1]:
                yield from flatten(sub)
        elif e[0] == "opt":
            yield from flatten(e[2])


def guards(events, depth=0):
    for e in events:
        if e[0] == "alt":
            for g, sub in e[1]:
                yield g, depth
                yield from guards(sub, depth + 1)
        elif e[0] == "opt":
            yield e[1], depth
            yield from guards(e[2], depth + 1)


def sequence(fname, title, parts, events):
    ids = [p[0] for p in parts]
    idx = {p: i for i, p in enumerate(ids)}
    widths = []
    for pid, label, kind in parts:
        widths.append(max(tw(label, 13, True) + 24, 90) if kind != "actor" else max(tw(label, 13, True) + 10, 60))
    xs = []
    x = 40
    for i, w in enumerate(widths):
        x = x + w / 2 if i == 0 else xs[-1] + widths[i - 1] / 2 + 40 + w / 2
        xs.append(x)

    cons = []
    for e in flatten(events):
        if e[0] == "s":
            i = idx[e[1]]
            cons.append((i, i + 1, tw(chg(e[2])[1], 13, True) + 70))
        else:
            i, j = sorted((idx[e[1]], idx[e[2]]))
            cons.append((i, j, tw(chg(e[3])[1], 13, True) + 36))
    cons.sort(key=lambda c: c[1] - c[0])
    for i, j, need in cons:
        if j >= len(xs):
            continue
        d = need - (xs[j] - xs[i])
        if d > 0:
            for k in range(j, len(xs)):
                xs[k] += d
    W = xs[-1] + widths[-1] / 2 + 40
    for e in flatten(events):
        if e[0] == "s" and idx[e[1]] == len(xs) - 1:
            W = max(W, xs[-1] + tw(chg(e[2])[1], 13, True) + 80)
    for g, depth in guards(events):
        W = max(W, 20 + depth * 12 + 60 + tw(f"[{g}]", 12, True) + 40)
    W = max(W, 760)

    top = 60
    life_y0 = 134
    b_front, b_back = [], []
    y = life_y0 + 16

    def frame(op, sections, depth):
        nonlocal y
        left = 14 + depth * 12
        right = W - 14 - depth * 12
        y0 = y
        y += 4
        seps = []
        for si, (guard, sub) in enumerate(sections):
            if si > 0:
                seps.append(y)
                y += 4
            gx = left + 56 if si == 0 else left + 10
            gc, gtxt = chg(guard)
            b_front.append(text(gx, y + 15, ("!" if gc else "") + f"[{gtxt}]", size=12, italic=True, halo=True, fill="#7c2d12"))
            y += 26
            run(sub, depth + 1)
            y += 4
        y += 4
        b_back.append(f'<rect x="{left}" y="{y0}" width="{right-left}" height="{y-y0}" fill="none" stroke="#64748b" stroke-width="1.2"/>')
        b_back.append(f'<path d="M{left},{y0} h44 v12 l-8,8 h-36 z" fill="#e2e8f0" stroke="#64748b" stroke-width="1.2"/>')
        b_front.append(text(left + 6, y0 + 15, op, size=12, bold=True))
        for sy in seps:
            b_back.append(f'<line x1="{left}" y1="{sy}" x2="{right}" y2="{sy}" stroke="#64748b" stroke-width="1.2" stroke-dasharray="6 4"/>')
        y += 10

    def run(evs, depth):
        nonlocal y
        for e in evs:
            k = e[0]
            if k in ("m", "r"):
                a, c, label = xs[idx[e[1]]], xs[idx[e[2]]], e[3]
                y += 4
                b_front.append(text((a + c) / 2, y + 12, label, size=13, anchor="middle", halo=True))
                ay = y + 20
                col, sfx, sw = (RED, "R", 2.0) if chg(label)[0] else (LINE, "", 1.4)
                if k == "m":
                    b_front.append(f'<line x1="{a}" y1="{ay}" x2="{c}" y2="{ay}" stroke="{col}" stroke-width="{sw}" marker-end="url(#filled{sfx})"/>')
                else:
                    b_front.append(f'<line x1="{a}" y1="{ay}" x2="{c}" y2="{ay}" stroke="{col}" stroke-width="{sw}" stroke-dasharray="6 4" marker-end="url(#open{sfx})"/>')
                y += 30
            elif k == "s":
                a = xs[idx[e[1]]]
                y += 4
                b_front.append(text(a + 10, y + 12, e[2], size=13, halo=True))
                ay = y + 20
                col, sfx, sw = (RED, "R", 2.0) if chg(e[2])[0] else (LINE, "", 1.4)
                b_front.append(f'<polyline points="{a},{ay} {a+34},{ay} {a+34},{ay+16} {a},{ay+16}" fill="none" stroke="{col}" stroke-width="{sw}" marker-end="url(#filled{sfx})"/>')
                y += 44
            elif k == "alt":
                frame("alt", e[1], depth)
            elif k == "opt":
                frame("opt", [(e[1], e[2])], depth)

    run(events, 0)
    y_end = y + 14

    heads = []
    for (pid, label, kind), x, w in zip(parts, xs, widths):
        b_back.insert(0, f'<line x1="{x}" y1="{life_y0}" x2="{x}" y2="{y_end}" stroke="#94a3b8" stroke-width="1.2" stroke-dasharray="5 5"/>')
        if kind == "actor":
            heads += actor(x, top + 20, "")[:-1]
            heads.append(text(x, life_y0 - 6, label, size=13, anchor="middle", bold=True))
        else:
            heads.append(f'<rect x="{x-w/2}" y="{top+22}" width="{w}" height="38" fill="{HEAD}" stroke="{LINE}" stroke-width="1.5"/>')
            heads.append(text(x, top + 46, label, size=13, anchor="middle", bold=True))
            b_back.append(f'<line x1="{x}" y1="{top+60}" x2="{x}" y2="{life_y0}" stroke="#94a3b8" stroke-width="1.2" stroke-dasharray="5 5"/>')
    b_front.extend(legend(16, y_end + 28))
    save(fname, W, y_end + 44, b_back + heads + b_front, title)


C = ("C", "Client", "actor")
UA = ("C", "User / Admin", "actor")
ADM = ("C", "Admin", "actor")
DB = ("DB", "MongoDB", "obj")
NA = "!401 Not authorized to access this route (was 201)"


def sequences():
    sequence("03-seq-register.svg", "Sequence Diagram — Register", [
        C, ("R", ":AuthRouter", "obj"), ("AC", ":AuthController", "obj"), ("U", ":User", "obj"), DB,
    ], [
        ("m", "C", "R", "!POST /api/v1/auth/register {name, tel, email, password}"),
        ("m", "R", "AC", "register(req, res)"),
        ("m", "AC", "U", "!User.create({name, email, tel, password, role})"),
        ("s", "U", "!validate schema (email, tel, password min 6)"),
        ("alt", [
            ("validation failed", [
                ("r", "U", "AC", "ValidationError"),
                ("r", "AC", "C", "!400 {success: false, message}"),
            ]),
            ("valid", [
                ("s", "U", "pre('save'): bcrypt.hash(password)"),
                ("m", "U", "DB", "insert user"),
                ("alt", [
                    ("!email already exists (code 11000)", [
                        ("r", "DB", "U", "E11000 duplicate key"),
                        ("r", "U", "AC", "error"),
                        ("r", "AC", "C", "!400 Email is already registered"),
                    ]),
                    ("saved", [
                        ("r", "DB", "U", "user"),
                        ("r", "U", "AC", "user"),
                        ("m", "AC", "U", "getSignedJwtToken()"),
                        ("r", "U", "AC", "token"),
                        ("r", "AC", "C", "!201 {success, _id, name, email, tel, token}"),
                    ]),
                ]),
            ]),
        ]),
    ])

    sequence("04-seq-login.svg", "Sequence Diagram — Login", [
        C, ("R", ":AuthRouter", "obj"), ("AC", ":AuthController", "obj"), ("U", ":User", "obj"), DB,
    ], [
        ("m", "C", "R", "POST /api/v1/auth/login {email, password}"),
        ("m", "R", "AC", "login(req, res)"),
        ("alt", [
            ("email or password missing", [
                ("r", "AC", "C", "400 Please provide an email and password"),
            ]),
            ("both provided", [
                ("m", "AC", "U", "findOne({email}).select('+password')"),
                ("m", "U", "DB", "query"),
                ("r", "DB", "U", "user | null"),
                ("r", "U", "AC", "user | null"),
                ("alt", [
                    ("user == null", [("r", "AC", "C", "!401 Invalid credentials (was 400)")]),
                    ("user found", [
                        ("m", "AC", "U", "matchPassword(password)"),
                        ("s", "U", "bcrypt.compare()"),
                        ("r", "U", "AC", "isMatch"),
                        ("alt", [
                            ("!isMatch", [("r", "AC", "C", "401 Invalid credentials")]),
                            ("isMatch", [
                                ("m", "AC", "U", "getSignedJwtToken()"),
                                ("r", "U", "AC", "token"),
                                ("r", "AC", "C", "!200 {success, _id, name, email, tel, token}"),
                            ]),
                        ]),
                    ]),
                ]),
            ]),
        ]),
    ])

    sequence("05-seq-logout.svg", "Sequence Diagram — Logout", [
        C, ("R", ":AuthRouter", "obj"), ("P", ":protect", "obj"), ("AC", ":AuthController", "obj"),
    ], [
        ("m", "C", "R", "GET /api/v1/auth/logout (Bearer token)"),
        ("m", "R", "P", "!protect(req, res, next)  (new on logout)"),
        ("alt", [
            ("token missing, invalid, or user deleted", [("r", "P", "C", NA)]),
            ("token valid", [
                ("m", "P", "AC", "next() → logout(req, res)"),
                ("s", "AC", "res.cookie('token', 'none', expires 10 s)"),
                ("r", "AC", "C", "200 {success: true, data: {}}"),
            ]),
        ]),
    ])

    sequence("06-seq-protect-authorize.svg", "Sequence Diagram — protect + authorize (every private route)", [
        C, ("P", ":protect", "obj"), ("U", ":User", "obj"), ("A", ":authorize(...roles)", "obj"), ("CT", ":Controller", "obj"),
    ], [
        ("m", "C", "P", "request with Authorization: Bearer token"),
        ("alt", [
            ("no token, or token == 'null'", [("r", "P", "C", NA)]),
            ("token present", [
                ("s", "P", "jwt.verify(token, JWT_SECRET)"),
                ("alt", [
                    ("verify throws", [("r", "P", "C", NA)]),
                    ("decoded {id}", [
                        ("m", "P", "U", "findById(decoded.id)"),
                        ("r", "U", "P", "user | null"),
                        ("alt", [
                            ("!user == null (account deleted)", [("r", "P", "C", NA)]),
                            ("user found", [
                                ("m", "P", "A", "next() with req.user"),
                                ("alt", [
                                    ("req.user.role not in roles", [("r", "A", "C", "!401 User role X is not authorized (was 403)")]),
                                    ("role allowed", [
                                        ("m", "A", "CT", "next()"),
                                        ("r", "CT", "C", "controller response"),
                                    ]),
                                ]),
                            ]),
                        ]),
                    ]),
                ]),
            ]),
        ]),
    ])

    SR = ("R", ":CoworkingSpaceRouter", "obj")
    SC = ("SC", ":CoworkingSpaceController", "obj")
    S = ("S", ":CoworkingSpace", "obj")
    sequence("07-seq-get-spaces.svg", "Sequence Diagram — View co-working space list", [C, SR, SC, S, DB], [
        ("m", "C", "R", "GET /api/v1/coworkingspaces?select=&sort=&page=&limit="),
        ("m", "R", "SC", "getCoworkingSpaces(req, res)"),
        ("s", "SC", "remove select/sort/page/limit, gt|gte|lt|lte|in → $gt..."),
        ("m", "SC", "S", "find(filter).select().sort().skip().limit()"),
        ("m", "S", "DB", "query"),
        ("alt", [
            ("query ok", [
                ("r", "DB", "S", "spaces"),
                ("r", "S", "SC", "spaces"),
                ("m", "SC", "S", "countDocuments()"),
                ("r", "S", "SC", "total"),
                ("s", "SC", "build pagination {next, prev}"),
                ("r", "SC", "C", "200 {success, count, data, pagination}"),
            ]),
            ("error", [("r", "SC", "C", "!400 {success: false, message}")]),
        ]),
    ])

    sequence("08-seq-get-space.svg", "Sequence Diagram — View co-working space detail", [C, SR, SC, S, DB], [
        ("m", "C", "R", "GET /api/v1/coworkingspaces/:id"),
        ("m", "R", "SC", "getCoworkingSpace(req, res)"),
        ("m", "SC", "S", "findById(id)"),
        ("m", "S", "DB", "query"),
        ("alt", [
            ("malformed id (CastError)", [("r", "SC", "C", "!400 {success: false, message}")]),
            ("not found", [("r", "DB", "S", "null"), ("r", "S", "SC", "null"), ("r", "SC", "C", "!404 {success: false} (was 400)")]),
            ("found", [("r", "DB", "S", "space"), ("r", "S", "SC", "space"), ("r", "SC", "C", "200 {success, data}")]),
        ]),
    ])

    PA = ("P", ":protect + authorize", "obj")
    RC = ("RC", ":ReservationController", "obj")
    RS = ("RS", ":Reservation", "obj")
    sequence("09-seq-add-reservation.svg", "Sequence Diagram — Reserve a co-working space (max 3)", [
        UA, ("R", ":Router (nested)", "obj"), PA, RC, S, RS, DB,
    ], [
        ("m", "C", "R", "POST /coworkingspaces/:coworkingSpaceId/reservations {reservationDate}"),
        ("m", "R", "P", "protect, authorize('admin','user')"),
        ("m", "P", "RC", "addReservation(req, res)"),
        ("m", "RC", "S", "findById(coworkingSpaceId)"),
        ("r", "S", "RC", "space | null"),
        ("alt", [
            ("space == null", [("r", "RC", "C", "404 No coworkingSpace with the id of ...")]),
            ("!reservationDate missing", [("r", "RC", "C", "!400 Please provide a reservationDate")]),
            ("else", [
                ("m", "RC", "RS", "!countDocuments({user: req.user.id})"),
                ("r", "RS", "RC", "count"),
                ("alt", [
                    ("count >= 3 and role != admin", [("r", "RC", "C", "400 User ... has already made 3 reservations")]),
                    ("allowed", [
                        ("m", "RC", "RS", "!create({reservationDate, coworkingSpace, user})  (whitelisted)"),
                        ("m", "RS", "DB", "insert"),
                        ("alt", [
                            ("!ValidationError / CastError", [
                                ("r", "RS", "RC", "error"),
                                ("r", "RC", "C", "!400 Date string is invalid"),
                            ]),
                            ("saved", [
                                ("r", "DB", "RS", "reservation"),
                                ("r", "RS", "RC", "reservation"),
                                ("r", "RC", "C", "201 {success, data}"),
                            ]),
                        ]),
                    ]),
                ]),
            ]),
        ]),
    ])

    PR = ("P", ":protect", "obj")
    sequence("10-seq-get-reservations.svg", "Sequence Diagram — View reservations", [UA, PR, RC, RS, DB], [
        ("m", "C", "P", "GET /reservations  (or /coworkingspaces/:id/reservations)"),
        ("m", "P", "RC", "getReservations(req, res)"),
        ("alt", [
            ("role != admin", [("m", "RC", "RS", "find({user: req.user.id}).populate(coworkingSpace)")]),
            ("admin with coworkingSpaceId", [("m", "RC", "RS", "find({coworkingSpace: id}).populate(coworkingSpace)")]),
            ("admin", [("m", "RC", "RS", "find().populate(coworkingSpace)")]),
        ]),
        ("m", "RS", "DB", "query"),
        ("alt", [
            ("ok", [
                ("r", "DB", "RS", "reservations"),
                ("r", "RS", "RC", "reservations"),
                ("r", "RC", "C", "200 {success, count, data}"),
            ]),
            ("error", [("r", "RC", "C", "500 Cannot find Reservation")]),
        ]),
    ])

    sequence("11-seq-get-reservation.svg", "Sequence Diagram — View one reservation", [UA, PR, RC, RS, DB], [
        ("m", "C", "P", "GET /reservations/:id"),
        ("m", "P", "RC", "getReservation(req, res)"),
        ("m", "RC", "RS", "findById(id).populate(coworkingSpace)"),
        ("m", "RS", "DB", "query"),
        ("r", "DB", "RS", "reservation | null"),
        ("r", "RS", "RC", "reservation | null"),
        ("alt", [
            ("reservation == null", [("r", "RC", "C", "404 No reservation with the id of ...")]),
            ("!not owner and not admin", [("r", "RC", "C", "!401 User ... is not authorized to view this reservation")]),
            ("owner or admin", [("r", "RC", "C", "200 {success, data}")]),
        ]),
    ])

    sequence("12-seq-update-reservation.svg", "Sequence Diagram — Edit reservation", [UA, PA, RC, RS, S, DB], [
        ("m", "C", "P", "PUT /reservations/:id {reservationDate?, coworkingSpace?}"),
        ("m", "P", "RC", "updateReservation(req, res)"),
        ("m", "RC", "RS", "findById(id)"),
        ("r", "RS", "RC", "reservation | null"),
        ("alt", [
            ("reservation == null", [("r", "RC", "C", "404 No reservation with the id of ...")]),
            ("not owner and not admin", [("r", "RC", "C", "401 User ... is not authorized to update this reservation")]),
            ("owner or admin", [
                ("s", "RC", "!updates = {reservationDate} (whitelist)"),
                ("opt", "!body.coworkingSpace given", [
                    ("m", "RC", "S", "!findById(body.coworkingSpace)"),
                    ("r", "S", "RC", "space | null"),
                    ("alt", [
                        ("space == null", [("r", "RC", "C", "!404 No co-working space with the id of ...")]),
                        ("found", [("s", "RC", "!updates.coworkingSpace = id")]),
                    ]),
                ]),
                ("m", "RC", "RS", "!findByIdAndUpdate(id, updates, {new, runValidators})"),
                ("m", "RS", "DB", "update"),
                ("r", "DB", "RS", "updated reservation"),
                ("r", "RS", "RC", "reservation"),
                ("r", "RC", "C", "200 {success, data}"),
            ]),
        ]),
    ])

    sequence("13-seq-delete-reservation.svg", "Sequence Diagram — Delete reservation", [UA, PA, RC, RS, DB], [
        ("m", "C", "P", "DELETE /reservations/:id"),
        ("m", "P", "RC", "deleteReservation(req, res)"),
        ("m", "RC", "RS", "findById(id)"),
        ("r", "RS", "RC", "reservation | null"),
        ("alt", [
            ("reservation == null", [("r", "RC", "C", "404 No reservation with the id of ...")]),
            ("not owner and not admin", [("r", "RC", "C", "401 User ... is not authorized to delete this reservation")]),
            ("owner or admin", [
                ("m", "RC", "RS", "reservation.deleteOne()"),
                ("m", "RS", "DB", "delete"),
                ("r", "RC", "C", "200 {success, data: reservation}"),
            ]),
        ]),
    ])

    sequence("14-seq-delete-space.svg", "Sequence Diagram — Admin deletes a co-working space (cascade)", [
        ADM, ("P", ":protect + authorize('admin')", "obj"), SC, S, RS, DB,
    ], [
        ("m", "C", "P", "DELETE /coworkingspaces/:id"),
        ("m", "P", "SC", "deleteCoworkingSpace(req, res)"),
        ("m", "SC", "S", "findById(id)"),
        ("r", "S", "SC", "space | null"),
        ("alt", [
            ("space == null", [("r", "SC", "C", "404 {success: false}")]),
            ("found", [
                ("m", "SC", "RS", "deleteMany({coworkingSpace: id})"),
                ("m", "RS", "DB", "delete reservations"),
                ("m", "SC", "S", "deleteOne({_id: id})"),
                ("m", "S", "DB", "delete space"),
                ("r", "SC", "C", "200 {success, data: space}"),
            ]),
        ]),
    ])


use_case()
class_profile()
sequences()
