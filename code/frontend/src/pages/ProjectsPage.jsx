import React from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api/client'
import { useAuth } from '../hooks/useAuth'

export default function ProjectsPage() {
  const { isAuthed } = useAuth()
  const [form, setForm] = React.useState({ title: '', description: '' })
  const [my, setMy] = React.useState([])
  const [allProjects, setAllProjects] = React.useState([])
  const [error, setError] = React.useState(null)
  const [me, setMe] = React.useState(null)

  const submit = async (e) => {
    e.preventDefault()
    try {
      const created = await api.createProject(form)
      setForm({ title: '', description: '' })
    } catch (e) { setError(e.message) }
  }

  const loadMy = async () => {
    try { setMy(await api.myProjects()) } catch (e) { /* ignore */ }
  }
  const loadAll = async () => {
    try { setAllProjects(await api.listAllProjects()) } catch (e) { /* ignore */ }
  }
  
  const loadMe = async () => {
    try { setMe(await api.me()) } catch (e) { /* ignore */ }
  }
  
  React.useEffect(() => { loadMy(); loadAll(); loadMe() }, [])

  const isProjectMember = (project) => {
    if (!me || !project) return false
    return (project.members || []).some(m => m.user_id === me.id)
  }

  const isProjectCreator = (project) => {
    if (!me || !project) return false
    return (project.members || []).some(m => m.user_id === me.id && m.is_creator)
  }

  return (
    <div className="page">
      <h1 className="h1">Projects</h1>

      {isAuthed && (
        <form className="card form" onSubmit={submit}>
          <div className="row">
            <input placeholder="Title" value={form.title} onChange={e => setForm({ ...form, title: e.target.value })} required />
            <input placeholder="Description" value={form.description} onChange={e => setForm({ ...form, description: e.target.value })} />
            <button className="btn primary" type="submit">Create</button>
          </div>
        </form>
      )}

      {error && <div className="alert error">{error}</div>}

      <div className="spacer" />
      <div className="card">
        <div className="subtitle">My projects</div>
        <div className="grid-cards">
          {my.map(p => (
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

      <div className="card">
        <div className="subtitle">All projects</div>
        <div className="grid-cards">
          {allProjects
            .filter(p => !my.some(mp => mp.id === p.id))
            .map(p => (
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

