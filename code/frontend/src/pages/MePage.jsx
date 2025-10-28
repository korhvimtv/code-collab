import React from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { api } from '../api/client'

export default function MePage() {
  const nav = useNavigate()
  const [me, setMe] = React.useState(null)
  const [projects, setProjects] = React.useState([])
  const [error, setError] = React.useState(null)
  const [edit, setEdit] = React.useState({ name: '', username: '', email: '', password: '' })
  const [createProject, setCreateProject] = React.useState({ title: '', description: '' })

  const load = async () => {
    setError(null)
    try {
      const [meRes, prjRes] = await Promise.all([api.me(), api.myProjects()])
      setMe(meRes)
      setProjects(prjRes)
      setEdit({ name: meRes.name, username: meRes.username, email: meRes.email, password: '' })
    } catch (e) { setError(e.message) }
  }
  React.useEffect(() => { load() }, [])

  const saveProfile = async (e) => {
    e.preventDefault()
    try {
      const payload = { name: edit.name, username: edit.username, email: edit.email }
      if (edit.password) payload.password = edit.password
      await api.updateUser(me.id, payload)
      await load()
    } catch (e) { setError(e.message) }
  }

  const deleteMyAccount = async () => {
    if (!confirm('Delete your account? This action cannot be undone.')) return
    try {
      await api.deleteUser(me.id)
      api.logout()
      nav('/register')
    } catch (e) { setError(e.message) }
  }

  const createNewProject = async (e) => {
    e.preventDefault()
    try {
      const res = await api.createProject(createProject)
      setCreateProject({ title: '', description: '' })
      setProjects([res, ...projects])
    } catch (e) { setError(e.message) }
  }

  const logout = () => { api.logout(); nav('/login') }

  return (
    <div className="page">
      <h1 className="h1">My account</h1>
      {error && <div className="alert error">{error}</div>}
      {me && (
        <div className="grid2">
          <form className="card form" onSubmit={saveProfile}>
            <div className="subtitle">Profile</div>
            <div className="row">
              <input placeholder="Name" value={edit.name} onChange={e => setEdit(v => ({ ...v, name: e.target.value }))} required />
              <input placeholder="Username" value={edit.username} onChange={e => setEdit(v => ({ ...v, username: e.target.value }))} required />
              <input type="email" placeholder="Email" value={edit.email} onChange={e => setEdit(v => ({ ...v, email: e.target.value }))} required />
              <input type="password" placeholder="New password (optional)" value={edit.password} onChange={e => setEdit(v => ({ ...v, password: e.target.value }))} />
              <button className="btn primary" type="submit">Save</button>
            </div>
          </form>

          <form className="card form" onSubmit={createNewProject}>
            <div className="subtitle">Create project</div>
            <div className="row">
              <input placeholder="Title" value={createProject.title} onChange={e => setCreateProject(v => ({ ...v, title: e.target.value }))} required />
              <input placeholder="Description" value={createProject.description} onChange={e => setCreateProject(v => ({ ...v, description: e.target.value }))} />
              <button className="btn primary" type="submit">Create</button>
            </div>
          </form>
        </div>
      )}

      <div className="card">
        <div className="subtitle">My projects</div>
        <div className="list">
          {projects.map(p => (
            <div key={p.id} className="list-item">
              <div>
                <div className="title">{p.title}</div>
                <div className="muted">{p.description}</div>
              </div>
              <div className="actions">
                <Link className="btn" to={`/projects/${p.id}`}>Open</Link>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="actions">
        <button className="btn" onClick={logout}>Logout</button>
        <button className="btn danger" onClick={deleteMyAccount}>Delete my account</button>
      </div>
    </div>
  )
}

