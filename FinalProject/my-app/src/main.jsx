import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { ThemeProvider, createTheme, responsiveFontSizes } from '@mui/material/styles'
import './index.css'
import App from './App.jsx'

// Default MUI theme + responsive typography: headings (h4, h5, ...) scale
// down automatically on small screens.
const theme = responsiveFontSizes(createTheme())

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <ThemeProvider theme={theme}>
      <App />
    </ThemeProvider>
  </StrictMode>,
)
