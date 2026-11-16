# Code changes: FinalProject vs Assignment 7 (vacqbackend)

FinalProject keeps the VacQ structure (config / models / middleware / controllers / routes / server.js).

## 1. Renamed domain

| Assignment 7 (VacQ) | FinalProject |
|---|---|
| `Hospital` model, `/api/v1/hospitals` | `CoworkingSpace` model, `/api/v1/coworkingspaces` |
| `Appointment` model, `/api/v1/appointments` | `Reservation` model, `/api/v1/reservations` |
| `/hospitals/:hospitalId/appointments` | `/coworkingspaces/:coworkingSpaceId/reservations` |
| `apptDate` | `reservationDate` |

Files renamed to match: `models/`, `controllers/` and `routes/` for both resources.

## 2. Removed

| Where | What |
|---|---|
| `server.js`, `package.json` | Security middleware: `express-mongo-sanitize`, `helmet`, `express-xss-sanitizer`, `express-rate-limit` |
| `server.js`, `package.json` | Swagger: `swagger-jsdoc`, `swagger-ui-express`, the `/api-docs` route and the `@swagger` comments in the routes |
| `models/CoworkingSpace.js` | Hospital fields `district`, `province`, `postalcode`, `region` |

## 3. Behaviour changes (red in the diagrams)

| Area | Change | Files |
|---|---|---|
| Register / User | New **`tel`** field: required, Thai phone format `0` + 8–9 digits (e.g. `0812345678`). Register accepts it, and register/login responses return it. | `models/User.js`, `controllers/auth.js` |
| Co-working space | New **`openTime`** and **`closeTime`** (required, `HH:mm`). **`tel`** is required. | `models/CoworkingSpace.js` |
| Logout | `GET /auth/logout` now **requires login** (`protect`). | `routes/auth.js` |
| View one reservation | `GET /reservations/:id` is **owner or admin only**. Other users get 401. | `controllers/reservations.js` |
| Edit reservation | `PUT /reservations/:id` only changes **`reservationDate`** and **`coworkingSpace`**. A new `coworkingSpace` must exist (404 otherwise). | `controllers/reservations.js` |

## 4. Other code changes

| Where | Change |
|---|---|
| `package.json` | `express` 4 → 5, `dotenv` 17 → 18, `mongoose` 9.9 → 9.12 |
| `controllers/reservations.js` | Reservation limit is a constant, `MAX_RESERVATIONS = 3`. Populated space fields are `name address tel openTime closeTime`. |

## 5. New files

- `postman/Coworking.postman_collection.json`: demo/test collection
- `KORN_GUIDE.md`: build guide
- `docs/`: this file, the PlantUML sources (`puml/`), the images (`img/`) and `gen_uml.py`
