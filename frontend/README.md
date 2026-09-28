# SyncSphere — Offline-First Enterprise Frontend

React + TypeScript + Vite + Material UI frontend for the Offline-First Data Synchronization System.

## Backend

Default API:

`http://127.0.0.1:8000/api/v1`

Create `.env` from `.env.example` if your backend URL differs.

## Run

```bash
npm install
npm run dev
```

Production build:

```bash
npm run build
npm run preview
```

## Features

- JWT authentication and protected routes
- Enterprise dashboard
- Record CRUD
- IndexedDB local cache
- Offline create/update/delete queue
- Automatic synchronization when connectivity returns
- Push/pull sync center
- Conflict management and resolution
- Sync history
- User administration view
- Responsive Material UI design
- Network/offline status indicator
