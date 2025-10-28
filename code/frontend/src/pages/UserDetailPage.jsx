import React from 'react'
import { useParams, Link } from 'react-router-dom'
import { api } from '../api/client'

export default function UserDetailPage() {
  const { username } = useParams()
  const [user, setUser] = React.useState(null)
  const [projects, setProjects] = React.useState([])
  const [error, setError] = React.useState(null)

  React.useEffect(() => {
    (async () => {
      try {
        const [u, prj] = await Promise.all([
          api.getUserByUsername(username),
          api.getUserProjectsByUsername(username)
        ])
        setUser(u)
        setProjects(prj)
      } catch (e) { setError(e.message) }
    })()
  }, [username])

  return (
    <div className="page">
      <h1 className="h1">User @{username}</h1>
      {error && <div className="alert error">{error}</div>}
      {user && (
        <div className="card">
          <div className="title">{user.name}</div>
          <div className="muted">@{user.username} · {user.email}</div>
        </div>
      )}

      <div className="card" style={{ marginTop: 16 }}>
        <div className="subtitle">Projects ({projects.length})</div>
        <div className="grid-cards">
          {projects.map(p => (
            <div key={p.id} className="card">
              <div className="card-title">{p.title}</div>
              <div className="muted">{p.description}</div>
              <div className="card-meta">
                <span className="muted">Members: {p.members?.length || 0}</span>
                <Link className="btn" to={`/projects/${p.id}`}>Open</Link>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}



