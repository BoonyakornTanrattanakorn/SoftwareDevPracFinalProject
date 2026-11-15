# Co-working Space Reservation API — Korn's Step-by-Step Guide

Covers every requirement assigned to **Korn** (register, login/logout, spaces list, reservation CRUD for user + admin) and the **Postman collection** used in the live demo.
The project mirrors the structure of `vacqbackend` — Hospital → **CoworkingSpace**, Appointment → **Reservation**.

## Key dates

| When | What |
|---|---|
| Mon 16 Nov 2026, before midnight | Code pushed to GitHub + slides uploaded to MCV |
| Tue 17 Nov 2026 | Presentation (7 min demo + 3 min Q&A, -0.5 pt per minute over) |

Suggested pace: Steps 1–4 by Wed 11, Steps 5–7 by Fri 13, Step 8 (Postman) + full Newman run by Sat 14. That leaves Sun–Mon for Best's merges and the slides.

Things the rules say you **don't** need: Swagger, security middleware (helmet/xss/rate-limit), frontend, cloud deployment. Run on `localhost`.

---

## Target structure

```
coworkingbackend/
├── config/
│   ├── config.env          # NOT committed
│   └── db.js               # copy as-is from vacqbackend
├── controllers/
│   ├── auth.js
│   ├── coworkingspaces.js
│   └── reservations.js
├── middleware/
│   └── auth.js
├── models/
│   ├── User.js
│   ├── CoworkingSpace.js
│   └── Reservation.js
├── routes/
│   ├── auth.js
│   ├── coworkingspaces.js
│   └── reservations.js
├── postman/
│   └── Coworking.postman_collection.json
├── .gitignore
├── package.json
└── server.js
```

## API endpoints you will build

| Method | Route | Access | Requirement |
|---|---|---|---|
| POST | `/api/v1/auth/register` | Public | Register (name, tel, email, password) |
| POST | `/api/v1/auth/login` | Public | Login |
| GET | `/api/v1/auth/logout` | Private | Logout |
| GET | `/api/v1/auth/me` | Private | (helper) |
| GET | `/api/v1/coworkingspaces` | Public | Space list |
| GET | `/api/v1/coworkingspaces/:id` | Public | Space detail |
| POST/PUT/DELETE | `/api/v1/coworkingspaces[/:id]` | Admin | Seed data for the demo |
| POST | `/api/v1/coworkingspaces/:coworkingSpaceId/reservations` | User/Admin | Reserve (max 3) |
| GET | `/api/v1/reservations` | User = own, Admin = all | View |
| GET | `/api/v1/reservations/:id` | Owner or Admin | View one |
| PUT | `/api/v1/reservations/:id` | Owner or Admin | Edit |
| DELETE | `/api/v1/reservations/:id` | Owner or Admin | Delete |

---

## Step 1 — Create the project

1. Create the GitHub repo (personal account is fine) and clone it. **Add Best as a collaborator now.** The contributors graph (`Insights → Contributors`) is shown in the presentation.
2. Install packages. Only the ones you need; the security packages are not required:
   ```bash
   npm init -y
   npm i express mongoose dotenv bcryptjs jsonwebtoken cookie-parser cors
   npm i -D nodemon
   ```
3. In `package.json` add `"dev": "nodemon server.js"` under `scripts`.
4. `.gitignore`:
   ```
   node_modules/
   config/config.env
   ```
5. Copy `config/db.js` from vacqbackend unchanged.
6. Create `config/config.env` with the same keys as vacqbackend (`NODE_ENV`, `PORT`, `MONGO_URI`, `JWT_SECRET`, `JWT_EXPIRE`, `JWT_COOKIE_EXPIRE`). Point `MONGO_URI` at a **new database name** in your Atlas cluster (e.g. `.../coworking?...`) so it doesn't mix with VacQ data. Send Best the values privately (not in git).
7. `server.js`: copy vacqbackend's version and **delete** the helmet, mongoSanitize, xss, rateLimit and swagger blocks. Change the routers:
   ```js
   const coworkingspaces = require("./routes/coworkingspaces");
   const reservations = require("./routes/reservations");
   const auth = require("./routes/auth");
   ...
   app.use("/api/v1/coworkingspaces", coworkingspaces);
   app.use("/api/v1/reservations", reservations);
   app.use("/api/v1/auth", auth);
   ```
   Keep the "Invalid JSON payload" handler. It's useful in the demo.

✅ Check: `npm run dev` prints `MongoDB Connected`. (It will crash on missing route files until Step 4. Create empty routers first if you want to test now.)

Commit: `Project setup`

---

## Step 2 — User model + register / login / logout

**Requirement:** register with name, **telephone**, email, password; login with email + password; logout.

### `models/User.js`: copy from vacqbackend, then change:

1. Add the telephone field:
   ```js
   tel: {
     type: String,
     required: [true, "Please add a telephone number"],
     match: [/^0\d{8,9}$/, "Please add a valid telephone number (e.g. 0812345678)"],
   },
   ```
2. Fix the password hook so it only hashes when the password changes. Best's "update profile" feature calls `save()`, and without this the hash would get hashed again:
   ```js
   UserSchema.pre("save", async function () {
     if (!this.isModified("password")) return;
     const salt = await bcrypt.genSalt(10);
     this.password = await bcrypt.hash(this.password, salt);
   });
   ```

### `controllers/auth.js`: copy from vacqbackend, then change:

1. `register`: read `tel` too: `const { name, tel, email, password, role } = req.body;` and pass it to `User.create`.
2. Make the register error useful for the **"Validation Check"** demo (step 1 of the presentation):
   ```js
   } catch (err) {
     let message = err.message;
     if (err.code === 11000) message = "Email is already registered";
     return res.status(400).json({ success: false, message });
   }
   ```
3. Add `tel` to the response object in `sendTokenResponse` (next to name/email).
4. Fix the typos `sucess` → `success` and `msg` → `message` so all responses look the same.

### `routes/auth.js`: same as vacqbackend, but protect logout:
```js
router.get("/logout", protect, logout);
```

> **Admin accounts:** register with `"role": "admin"` in the body. That's the same as VacQ and fine for this project.

✅ Check in Postman: register → 201 + token; register again with the same email → 400; missing `tel` → 400; login → 200; wrong password → 401.

Commit: `Add user registration with telephone, login and logout`

---

## Step 3 — Auth middleware

Copy `middleware/auth.js` from vacqbackend and fix two bugs, or your "logged-out" and "not allowed" tests will give misleading results:

1. Unauthorised responses use **201**. Change both to **401**:
   ```js
   return res.status(401).json({ success: false, message: "Not authorized to access this route" });
   ```
2. If the user from the token was deleted, `req.user` is `null` and the next line crashes. After `findById`:
   ```js
   if (!req.user) return res.status(401).json({ success: false, message: "Not authorized to access this route" });
   ```

Remove the `console.log(decoded)` while you're there.

Commit: `Fix auth middleware status codes`

---

## Step 4 — CoworkingSpace model, controller, routes

**Requirement:** a space has name, address, telephone number, open time, close time. The list is provided to the user.

### `models/CoworkingSpace.js`: based on `Hospital.js`

Fields:
```js
name:      { type: String, required: [true, "Please add a name"], unique: true, trim: true,
             maxlength: [50, "Name can not be more than 50 characters"] },
address:   { type: String, required: [true, "Please add an address"] },
tel:       { type: String, required: [true, "Please add a telephone number"] },
openTime:  { type: String, required: [true, "Please add an open time"],
             match: [/^([01]\d|2[0-3]):[0-5]\d$/, "Use HH:mm format, e.g. 08:00"] },
closeTime: { type: String, required: [true, "Please add a close time"],
             match: [/^([01]\d|2[0-3]):[0-5]\d$/, "Use HH:mm format, e.g. 20:00"] },
```
Keep the `toJSON/toObject: { virtuals: true }` options and rename the virtual:
```js
CoworkingSpaceSchema.virtual("reservations", {
  ref: "Reservation", localField: "_id", foreignField: "coworkingSpace", justOne: false,
});
```

### `controllers/coworkingspaces.js`: copy `controllers/hospitals.js`

- Find/replace `Hospital` → `CoworkingSpace`, `hospital` → `coworkingSpace`, `Appointment` → `Reservation`.
- In `getCoworkingSpaces`, **don't** `.populate("reservations")`. A normal user must not see other people's bookings in the public list.
- Wrap `createCoworkingSpace` in try/catch and return 400 with `err.message` (the VacQ version has none, so bad input crashes the request).
- `deleteCoworkingSpace` keeps the cascade: `Reservation.deleteMany({ coworkingSpace: req.params.id })`.

### `routes/coworkingspaces.js`: copy `routes/hospitals.js`

- Re-route: `router.use("/:coworkingSpaceId/reservations/", reservationRouter);`
- GET routes public; POST/PUT/DELETE `protect, authorize("admin")`.
- Delete all the swagger comments.

✅ Check: admin creates a space → 201; user tries to create → 403; `GET /coworkingspaces` without a token → 200 with the list.

Commit: `Add co-working space model, controller and routes`

---

## Step 5 — Reservation model

`models/Reservation.js`: based on `Appointment.js`:
```js
reservationDate: { type: Date, required: [true, "Please add a reservation date"] },
user:            { type: mongoose.Schema.ObjectId, ref: "User", required: true },
coworkingSpace:  { type: mongoose.Schema.ObjectId, ref: "CoworkingSpace", required: true },
createdAt:       { type: Date, default: Date.now },
```

Commit together with Step 6.

---

## Step 6 — Reservation controller + routes

Copy `controllers/appointments.js` → `controllers/reservations.js` and rename everything (Appointment → Reservation, hospital → coworkingSpace, `hospitalId` → `coworkingSpaceId`). Populate `select: "name address tel openTime closeTime"`.
Copy `routes/appointments.js` → `routes/reservations.js` (keep `mergeParams: true`, same middleware).

Then make the changes below. These are the parts graders poke at in Q&A.

### 6.1 Create: limit of 3 + "create condition" errors (presentation step 4)

Put the limit in one constant at the top of the file. Best's requirement replaces it with an admin-configurable value later, so this keeps the change to one line:
```js
const MAX_RESERVATIONS = 3;
```
In `addReservation`:
```js
// 1. date is required → clean 400 instead of 500
if (!req.body.reservationDate) {
  return res.status(400).json({ success: false, message: "Please provide a reservationDate" });
}
// 2. space must exist → 404 (already in VacQ code, just renamed)
// 3. limit
const count = await Reservation.countDocuments({ user: req.user.id });
if (count >= MAX_RESERVATIONS && req.user.role !== "admin") {
  return res.status(400).json({
    success: false,
    message: `The user with ID ${req.user.id} has already made ${MAX_RESERVATIONS} reservations`,
  });
}
// 4. only trust these fields from the body
const reservation = await Reservation.create({
  reservationDate: req.body.reservationDate,
  coworkingSpace: req.params.coworkingSpaceId,
  user: req.user.id,
});
```
Also: an invalid date string (`"abc"`) throws a Mongoose `CastError`/`ValidationError`. In the `catch`, return 400 for `err.name === "ValidationError" || err.name === "CastError"`, otherwise 500.

*Optional extra condition:* reject dates in the past (`new Date(req.body.reservationDate) < startOfToday` → 400). It's an easy extra "fail" case to show in the demo.

### 6.2 View own / view any (presentation steps 5 and 10)

`getReservations` already works: users get `find({ user: req.user.id })`, admins get everything (optionally filtered by `coworkingSpaceId`).

**Bug in VacQ to fix:** `getAppointment` (single, by id) has **no owner check**. Any user can read anyone's booking. Add the same check that update/delete have:
```js
if (reservation.user.toString() !== req.user.id && req.user.role !== "admin") {
  return res.status(403).json({ success: false, message: `User ${req.user.id} is not authorized to view this reservation` });
}
```
(VacQ uses 401 for this. 403 "forbidden" is more correct; pick one and use it everywhere.)

### 6.3 Edit own / edit any (steps 6 and 11)

Keep the owner-or-admin check, but **don't pass `req.body` straight in**. A user could change the `user` field and give the booking to someone else. Whitelist:
```js
const updates = {};
if (req.body.reservationDate) updates.reservationDate = req.body.reservationDate;
if (req.body.coworkingSpace) {
  const space = await CoworkingSpace.findById(req.body.coworkingSpace);
  if (!space) return res.status(404).json({ success: false, message: `No co-working space with the id of ${req.body.coworkingSpace}` });
  updates.coworkingSpace = req.body.coworkingSpace;
}
reservation = await Reservation.findByIdAndUpdate(req.params.id, updates, { new: true, runValidators: true });
```

### 6.4 Delete own / delete any (steps 7 and 12)

The VacQ logic is already correct. Just rename.

✅ Check: user makes 3 reservations → 201 each; 4th → 400; user GETs → count 3; user edits own → 200; user deletes own → 200; admin GET → sees everyone's.

Commit: `Add reservation CRUD with limit and ownership checks`

---

## Step 7 — Quick self-review against the requirements

| # | Requirement | Where | Postman folder |
|---|---|---|---|
| 1 | Register: name, tel, email, password | `auth.register`, `User.tel` | 01 |
| 2 | Login / logout | `auth.login`, `auth.logout` | 02, 08 |
| 3 | Reserve ≤ 3 by date + space; space list (name, address, tel, open/close) | `reservations.addReservation`, `CoworkingSpace` | 03, 04 |
| 4 | User views own | `getReservations` / `getReservation` | 05 |
| 5 | User edits own | `updateReservation` | 06 |
| 6 | User deletes own | `deleteReservation` | 07 |
| 7–9 | Admin view / edit / delete any | same functions, admin branch | 10, 11, 12 |
| NFR | Respond within 3 s | collection-level test | all |

---

## Step 8 — Postman collection for the live demo

The demo **must run through Postman Runner or Newman**. Clicking requests one by one is not allowed because there isn't enough time. So the collection must run **top to bottom with no manual edits**, and **it must work every time you rerun it** (use unique emails).

### 8.1 Collection variables

Collection → *Variables*:

| Variable | Initial value |
|---|---|
| `baseURL` | `http://localhost:5000/api/v1` |
| `userEmail`, `adminEmail` | (set by scripts) |
| `userToken`, `adminToken` | (set by scripts) |
| `spaceId`, `spaceId2`, `reservationId`, `reservationId2` | (set by scripts) |

### 8.2 Collection-level scripts

Collection → *Scripts → Post-response* (runs after **every** request, covers the 3-second NFR):
```js
pm.test("Responds within 3 seconds", () => {
  pm.expect(pm.response.responseTime).to.be.below(3000);
});
```

### 8.3 Folder layout = presentation order

Name folders with numbers so they match the slide steps. Use `Authorization → Bearer Token → {{userToken}}` or `{{adminToken}}` on each request.

**00 Setup** (runs first, so admin and spaces exist)
- *Register Admin*: Pre-request:
  ```js
  pm.collectionVariables.set("adminEmail", `admin${Date.now()}@test.com`);
  ```
  Body: `{ "name": "Admin", "tel": "0811111111", "email": "{{adminEmail}}", "password": "123456", "role": "admin" }`
  Post-response: save `adminToken` from `pm.response.json().token`.
- *Create Space 1* and *Create Space 2* (admin): save `spaceId` / `spaceId2` from `json.data._id`. Use `Date.now()` in the name (e.g. `"Korn Space {{$timestamp}}"`) since names are unique.

**01 User Registration + Validation Check**
- *Register – missing tel* → expect 400
- *Register – invalid email* → expect 400
- *Register – password too short* → expect 400
- *Register – success*: Pre-request sets `userEmail` = `user${Date.now()}@test.com`; expect 201; save `userToken`
- *Register – duplicate email* (reuse `{{userEmail}}`) → expect 400

**02 User Log-in**
- *Login – wrong password* → 401
- *Login – success* → 200; save `userToken` (overwrite)

**03 User View Product**
- *Get all spaces* → 200; test that `data` is an array and each item has `name, address, tel, openTime, closeTime`
- *Get space by id* `{{spaceId}}` → 200

**04 User Create Booking + Check Create Condition**
- *Create reservation 1* → 201; save `reservationId`
- *Create reservation 2* → 201; save `reservationId2`
- *Create reservation 3* → 201
- *Create reservation 4 (over limit)* → **400**, test message contains `"3"`
- *Create – space not found* (`/coworkingspaces/000000000000000000000000/reservations`) → 404
- *Create – missing date* → 400

  These two still return 400/404 even though the limit is already reached, because `addReservation` checks the date and the space *before* it checks the limit (Step 6.1 order).

**05 User View Own Booking**
- *Get my reservations* → 200, `count === 3`, every `data[i].user === <my id>` (save your id from the login response `_id`)

**06 User Edit Own Booking**
- *Update reservation 1* body `{ "reservationDate": "2026-12-20", "coworkingSpace": "{{spaceId2}}" }` → 200; test the new date/space came back

**07 User Delete Own Booking**
- *Delete reservation 2* → 200
- *Get my reservations* → `count === 2`

**08 User Log-out**
- *Logout* → 200. Post-response: `pm.collectionVariables.unset("userToken");`
- *Get reservations without token* → **401** (proves you're logged out)

**09 Admin Log-in**
- *Admin login* with `{{adminEmail}}` → 200; save `adminToken`

**10 Admin View Any Booking**
- *Admin get all reservations* → 200; test that `reservationId` is in the list (it belongs to the user, not the admin)

**11 Admin Edit Any Booking**
- *Admin update `{{reservationId}}`* → 200

**12 Admin Delete Any Booking**
- *Admin delete `{{reservationId}}`* → 200
- *Admin get `{{reservationId}}`* → 404

Example post-response test (adapt the status code per request):
```js
pm.test("Status 201", () => pm.response.to.have.status(201));
const json = pm.response.json();
pm.test("success is true", () => pm.expect(json.success).to.be.true);
pm.collectionVariables.set("reservationId", json.data._id);
```

### 8.4 Run it

- **Postman Runner:** right-click the collection → *Run* → keep the order → *Run*. Everything should be green.
- **Newman** (same as in vacqbackend):
  ```bash
  npx newman run postman/Coworking.postman_collection.json
  ```
  Export the collection (*… → Export → v2.1*) into `postman/` and commit it so Best can add requests for their features. Best's extras go in a separate folder, **13+ Extra**, so the main demo order stays the same.

### 8.5 Rehearse

- Start the server **before** the Zoom call, run Newman once to warm up the DB connection.
- Do a timed run of steps 1–12. Aim for ≤ 4 minutes so the slides and Best's extra-credit demo fit in 7.
- If something fails mid-demo, everything after it fails too (missing tokens/ids). Run the full collection at least 2–3 times in a row beforehand.

Commit: `Add Postman demo collection`

---

## Step 9 — Before the deadline (Mon 16 Nov, midnight)

- [ ] Fresh clone → `npm i` → add `config.env` → `npm run dev` → Newman run is all green
- [ ] Best's branches merged, and the collection still passes after the merge
- [ ] Both of you show up under `Insights → Contributors` (commits made with your own GitHub email)
- [ ] GitHub link added to the slides
- [ ] Slides uploaded to MCV

## Notes for working with Best

- Limit constant: `MAX_RESERVATIONS` in `controllers/reservations.js` is the single place to replace with the admin-configurable setting.
- The User `pre("save")` hook already skips re-hashing, so profile updates via `save()` are safe.
- Confirmation email and public-holiday checks fit inside `addReservation`: the holiday check goes before `Reservation.create`, the email after it.
- Agree on response shape: `{ success, message }` for errors and `{ success, data }` / `{ success, count, data }` for success.
