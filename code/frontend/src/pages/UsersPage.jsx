import React from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api/client'
import { useAuth } from '../hooks/useAuth'

export default function UsersPage() {
  const { isAuthed } = useAuth()
  const [users, setUsers] = React.useState([])
  const [loading, setLoading] = React.useState(false)
  const [error, setError] = React.useState(null)

  const load = async () => {
    setLoading(true); setError(null)
    try { setUsers(await api.listUsers()) } catch (e) { setError(e.message) } finally { setLoading(false) }
  }
  React.useEffect(() => { if (isAuthed) load() }, [isAuthed])

  return (
    <div className="page">
      <h1 className="h1">Users</h1>

      {error && <div className="alert error">{error}</div>}
      {!isAuthed ? <div className="card">Please sign in to view users.</div> : loading ? <div>Loading...</div> : (
        <div className="grid-cards">
          {users.map(u => (
            <div key={u.id} className="card">
              <div className="card-title">{u.name}</div>
              <div className="muted">@{u.username}</div>
              <div className="card-meta">
                <span className="muted">{u.email}</span>
                <div className="align-center" style={{ gap: 8 }}>
                  <Link className="btn" to={`/users/${encodeURIComponent(u.username)}`}>Open</Link>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

