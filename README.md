# Hotel Booking System

Backend for a hotel booking platform: owners onboard properties, guests search, book, pay and cancel.

Built with **Python 3.11+, Django and Django REST Framework**, using SQLite (no database to install). Payments go through a mocked gateway.

## Quick start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
python manage.py migrate
python manage.py runserver  # http://127.0.0.1:8000
```

## Commands

| Command | Purpose |
|---|---|
| `python manage.py migrate` | Create / update the SQLite database |
| `python manage.py runserver` | Start the API on port 8000 |

## API docs

- Swagger UI: http://127.0.0.1:8000/api/docs/ (needs internet, loads scripts from a CDN)
- OpenAPI schema: http://127.0.0.1:8000/api/schema/

## Endpoints

| Endpoint | What it does |
|---|---|
| `POST /api/owners/` | Register an owner |
| `POST /api/owners/{owner_id}/properties/` | Add a property with room types, amenities and prices |
| `GET /api/properties/{property_id}/` | Read a property |
| `GET /api/properties/search/` | Search free room types (`city`, `check_in`, `check_out`, `guests`; optional `min_price`, `max_price`, `amenities`, `min_stars`, `locality`) |
| `POST /api/bookings/` | Book a room type (held until paid) |
| `GET /api/bookings/{booking_id}/` | Read a booking |
| `POST /api/bookings/{booking_id}/pay/` | Pay by card, UPI or wallet |
| `POST /api/bookings/{booking_id}/cancel/` | Cancel and get the refund amount |

Errors look like `{"error": "message"}`. Status codes: 400 bad input, 404 not found, 409 state conflict (e.g. cancel twice, no room left).

## Configuration (`.env`)

| Variable | Meaning |
|---|---|
| `DJANGO_DEBUG` | `true` for local development |
| `DJANGO_ALLOWED_HOSTS` | Comma-separated hosts |
| `MOCK_GATEWAY_DECLINE_SUFFIX` | Payments whose details end with this are declined (default `0000`; empty declines nothing) |

## Project layout

```
domain/    business rules and interfaces (no Django)
services/  one class per use case: onboarding, search, booking, payment, cancellation
store/     Django models, migrations, repository implementations
api/       views, serializers, URLs, error handling, container.py (wiring)
config/    Django settings and root URLs
```
