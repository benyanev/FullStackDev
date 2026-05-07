# SocialApp

A React-based social media feed application built with Material UI. The app fetches posts from the [JSONPlaceholder](https://jsonplaceholder.typicode.com/) API and displays them in a responsive, paginated grid.

## Features

- **TopBar** — Navigation bar with the app name on the left and menu buttons (Home, Users, About, Login) on the right. Built with MUI `AppBar` and `Toolbar`.
- **Feed** — Loads 10 posts at a time from all users, with a "Load More" button to fetch the next batch. Displays a spinner (`CircularProgress`) while loading. Uses MUI `Grid` for a responsive layout.
- **SinglePost** — Displays the post title, author email, and the first 3 lines of the body. A "Read More" button expands to show the full text using MUI `Card` and `Collapse`.
- **API Service** — A dedicated `api.js` module with a `fetchPosts` function for paginated post retrieval and a `fetchUser` function with in-memory caching to avoid redundant network requests.

## Tech Stack

- **React 19** — UI library
- **Vite** — Build tool and dev server
- **Material UI (MUI) v9** — Component library for styling and layout
- **JSONPlaceholder** — Free REST API used as the data source

## Project Structure

```
src/
├── components/
│   ├── TopBar.jsx          — Navigation bar
│   ├── SinglePost.jsx      — Expandable post card
│   └── Feed.jsx            — Post grid with pagination and spinner
├── services/
│   └── api.js              — API fetch functions (fetchPosts, fetchUser)
├── App.jsx                 — Root component (composes TopBar + Feed)
├── index.css               — Global styles and resets
└── main.jsx                — React entry point
```

## Getting Started

### Prerequisites

- [Node.js](https://nodejs.org/) (v18 or higher)

### Installation

```bash
npm install
```

### Running the App

```bash
npm run dev
```

The app will be available at `http://localhost:5173`.

### Building for Production

```bash
npm run build
```

### Linting

```bash
npm run lint
```
