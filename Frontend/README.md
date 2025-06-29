# React + Vite

This template provides a minimal setup to get React working in Vite with HMR and some ESLint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Babel](https://babeljs.io/) for Fast Refresh
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/) for Fast Refresh

## Expanding the ESLint configuration

If you are developing a production application, we recommend using TypeScript with type-aware lint rules enabled. Check out the [TS template](https://github.com/vitejs/vite/tree/main/packages/create-vite/template-react-ts) for information on how to integrate TypeScript and [`typescript-eslint`](https://typescript-eslint.io) in your project.

# CodeOracle Frontend

This is the React.js frontend for the CodeOracle project. It features a beautiful dark theme with gradients and glitters, and allows users to:

- Input a GitHub repository URL for ingestion
- Chat with the AI (Gemini) about the codebase
- View responses in a modern chat interface

## Getting Started

1. Install dependencies:
   ```sh
   npm install
   ```
2. Start the development server:
   ```sh
   npm run dev
   ```

## Connecting to Backend
- The frontend expects the Flask backend to be running and accessible (by default at `http://localhost:8080`).
- Update API endpoints in the frontend code if your backend runs on a different port or host.

## Customization
- The UI uses a dark theme with gradients and glitter effects for a modern, visually appealing experience.

---

For more details, see the backend README and project documentation.
