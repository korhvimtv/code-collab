import React from 'react'
import { api } from '../api/client'

export function useAuth() {
  const [token, setToken] = React.useState(api.getToken())

  React.useEffect(() => {
    const onStorage = (e) => {
      if (e.key === 'token') setToken(api.getToken())
    }
    
    const onAuthChange = () => {
      setToken(api.getToken())
    }
    
    window.addEventListener('storage', onStorage)
    window.addEventListener('authChange', onAuthChange)
    
    return () => {
      window.removeEventListener('storage', onStorage)
      window.removeEventListener('authChange', onAuthChange)
    }
  }, [])

  return { isAuthed: !!token, token }
}




