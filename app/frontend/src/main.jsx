import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'
import Compte from './compte.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <Compte />
  </StrictMode>,
)
