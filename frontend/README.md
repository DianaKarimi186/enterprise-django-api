# Enterprise Inventory React frontend

This frontend lives beside the existing Django API in `frontend/`. It does not replace the existing Django/HTMX dashboard.

## Requirements

- Node.js 20 or newer
- The Django API running locally, normally at `http://127.0.0.1:8000`

## Run locally

```bash
cd frontend
npm install
npm run dev
```

Open the Vite URL printed in the terminal (normally `http://localhost:5173`). Vite proxies `/api` requests to Django. To use a different local API origin, set `DJANGO_API_ORIGIN` before starting Vite.

## Production build

```bash
npm run build
npm run preview
```

The build is written to `frontend/dist/`.

Set `VITE_API_BASE_URL` at build time if the API is hosted on a different origin, for example `https://your-api.example.com`. In that deployment arrangement, Django must allow the frontend origin through CORS and the host must serve the built frontend over HTTPS. If frontend and API share one origin, leave this variable empty.

## Authentication

The UI uses the existing Simple JWT endpoint at `/api/accounts/login/`. Access and refresh tokens are kept in `sessionStorage` for the current browser tab session. The frontend sends the access token in the Authorization header. An expired access token sends the user back to the sign-in screen; automatic refresh is not yet implemented.

## API endpoints used

- `POST /api/accounts/login/`
- `GET /api/products/`
- `GET /api/products/categories/`
- `GET /api/products/dashboard/metrics/`
- `POST /api/products/`
- `PATCH /api/products/:id/`
- `DELETE /api/products/:id/`

The categories and metrics endpoints are added by the accompanying backend changes on the feature branch.
