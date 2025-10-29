import React from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import App from './App.jsx'
import './styles/github.css'

const rootEl = document.getElementById('root')
if (!rootEl) throw new Error('Root element not found')
const root = createRoot(rootEl)

root.render(
  <React.StrictMode>
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </React.StrictMode>
)




