# API Spec

See `/api/schema/` for OpenAPI schema and `/api/docs/` for Swagger UI.

Key endpoints:
- `POST /api/auth/send-otp/` - send OTP (dev logs OTP)
- `POST /api/auth/verify-otp/` - verify OTP and receive JWT tokens
- `GET /api/requests/` - list requests (public)
- `POST /api/requests/` - create request (auth required)
- `POST /api/donations/` - create donation (returns simulated payment_intent)
- `POST /api/payments/webhook/` - webhook to update payment status
