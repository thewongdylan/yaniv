// Entry point for React app
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App.jsx';

// Find "root" div in index.html
const rootElement = document.getElementById('root');

// Inject app component into the screen
ReactDOM.createRoot(rootElement).render(
    <App />
);