# Code changes: FinalProject vs Assignment 7 (vacqbackend)

FinalProject keeps the VacQ structure (config / models / middleware / controllers / routes / server.js).
The domain is renamed everywhere:

| Assignment 7 (VacQ) | FinalProject |
|---|---|
| `Hospital` model, `/api/v1/hospitals` | `CoworkingSpace` model, `/api/v1/coworkingspaces` |
| `Appointment` model, `/api/v1/appointments` | `Reservation` model, `/api/v1/reservations` |
| `/hospitals/:hospitalId/appointments` | `/coworkingspaces/:coworkingSpaceId/reservations` |
| `apptDate` | `reservationDate` |

Everything below is a change on top of that rename.

---

## Unchanged

- `config/db.js` (identical)
- `routes/reservations.js` (same as `routes/appointments.js`, renamed only)
- `deleteReservation` and `deleteCoworkingSpace` logic, including the cascade delete of reservations

---

## server.js

| Change | Why |
|---|---|
| Removed `express-mongo-sanitize`, `helmet`, `express-xss-sanitizer`, `express-rate-limit` | Not required by the project spec |
| Removed Swagger (`swagger-jsdoc`, `swagger-ui-express`, `/api-docs`) | Not required by the project spec |
| Routers mounted at `/api/v1/coworkingspaces` and `/api/v1/reservations` | Domain rename |

Kept: CORS, extended query parser, JSON body parser, the "Invalid JSON payload" handler, cookie-parser, `unhandledRejection` handler.

## package.json

- Removed the 6 security/Swagger packages above.
- `express` 4.22 → **5.3**, `dotenv` 17 → 18, `mongoose` 9.9 → 9.12.

---

## models/User.js

| Change | Detail |
|---|---|
| **New field `tel`** | `required`, must match `/^0\d{8,9}$/` (e.g. `0812345678`) |
| Password hook fixed | `pre("save")` now skips hashing when the password was not modified (`if (!this.isModified("password")) return;`). VacQ re-hashed on every save, which would corrupt the password if a user document were saved again. Also dropped the unused `next` parameter (Mongoose 9 style). |

## models/CoworkingSpace.js (was Hospital.js)

| VacQ Hospital | CoworkingSpace |
|---|---|
| `name`, `address` | kept |
| `tel` (optional) | `tel` **required** |
| `district`, `province`, `postalcode`, `region` | **removed** |
| — | **`openTime`, `closeTime`** (required, `HH:mm` format validated by regex) |
| virtual `appointments` | virtual `reservations` |

## models/Reservation.js (was Appointment.js)

- `apptDate` → `reservationDate`, with a custom "Please add a reservation date" message.
- `hospital` → `coworkingSpace` (ref `CoworkingSpace`).

---

## middleware/auth.js

| Change | VacQ | FinalProject |
|---|---|---|
| Missing/invalid token status | `201` (bug: a success code) | **`401`** |
| Typo in response key | `sucess` | `success` |
| Message | "Not authorize to access…" | "Not authorized to access…" |
| Token for a deleted user | `req.user = null`, then crashes later | **New check:** returns `401` if the user no longer exists |
| `authorize` wrong role status | `403` | `401` (note: 403 Forbidden is the more correct REST code here) |
| Debug output | `console.log(decoded)` | removed |

## routes/auth.js

- `GET /logout` now runs **`protect`** (VacQ allowed logout without a token).

## controllers/auth.js

| Function | Change |
|---|---|
| `register` | Accepts and saves **`tel`**. On error returns the real validation `message` (VacQ returned only `{sucess:false}`). Duplicate email (Mongo code `11000`) returns **"Email is already registered"**. |
| `login` | Response key `msg` → `message`. Unknown email returns **401** (VacQ returned 400), so it's the same as a wrong password. |
| `sendTokenResponse` | Response now includes **`tel`**. |
| Comments | `getMe` / `logout` route comments corrected (`GET`, not `POST`). |

---

## controllers/coworkingspaces.js (was hospitals.js)

| Function | Change |
|---|---|
| `getCoworkingSpaces` | No longer `.populate("appointments")` on the list; removed default sort `-createdAt` (the model has no `createdAt`); removed `console.log(reqQuery)`; error returns `message`. |
| `getCoworkingSpace` | Not found returns **404** (VacQ: 400). Error returns `message`. |
| `createCoworkingSpace` | Wrapped in **try/catch** → `400 {message}` on validation error. VacQ had no try/catch, so a bad body caused an unhandled promise rejection that **shut the server down**. |
| `updateCoworkingSpace` | Not found returns **404** (VacQ: 400). |
| `deleteCoworkingSpace` | Same logic (cascade delete), error returns `message`. |

## controllers/reservations.js (was appointments.js)

| Function | Change |
|---|---|
| (module) | `MAX_RESERVATIONS = 3` constant instead of a hard-coded `3`. |
| `getReservations` | Populates `name address tel openTime closeTime` (VacQ: `name province tel`). |
| `getReservation` | **New ownership check:** a user who is not the owner (and not admin) gets **401**. In VacQ any logged-in user could read anyone's appointment by id. Populate fields fixed (VacQ asked for `description`, which doesn't exist). |
| `addReservation` | **Explicit check** that `reservationDate` is present → 400. Uses `countDocuments` instead of loading all documents with `find()`. **Whitelists fields**: creates from `{reservationDate, coworkingSpace, user}` only. VacQ passed the whole `req.body` and mutated it. An invalid date (`ValidationError`/`CastError`) returns **400 "Date string is invalid"** instead of 500. |
| `updateReservation` | **Whitelists fields**: only `reservationDate` and `coworkingSpace` can be changed. VacQ passed `req.body` directly, so a user could reassign `user` to someone else. If a new `coworkingSpace` is given, it must exist (**404** otherwise). |
| `deleteReservation` | Renamed only. |

---

## New files

- `postman/Coworking.postman_collection.json`: demo/test collection
- `KORN_GUIDE.md`: build guide
- `docs/`: this file and the UML diagrams

## Not carried over from VacQ

`autograde.js`, `__tests__/`, `newman/`, `.github/`, `VacQ.postman_collection.json` (assignment autograding only).
