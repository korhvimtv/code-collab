import React from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { api } from '../api/client'

export default function ProjectDetailPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [project, setProject] = React.useState(null)
  const [tasks, setTasks] = React.useState([])
  const [invite, setInvite] = React.useState({ user_id: '', is_creator: false })
  const [taskForm, setTaskForm] = React.useState({ title: '', description: '', deadline: '' })
  const [assigneeId, setAssigneeId] = React.useState('')
  const [error, setError] = React.useState(null)
  const [me, setMe] = React.useState(null)
  const [editProject, setEditProject] = React.useState({ title: '', description: '' })

  const load = async () => {
    try {
      const [proj, current, projectTasks] = await Promise.all([
        api.getProject(id),
        api.me().catch(() => null),
        api.getProjectTasks(id).catch(() => [])
      ])
      setProject(proj)
      setMe(current)
      setTasks(projectTasks)
      setEditProject({ title: proj.title || '', description: proj.description || '' })
    } catch (e) { setError(e.message) }
  }
  React.useEffect(() => { load() }, [id])

  const doInvite = async (e) => {
    e.preventDefault()
    try {
      await api.inviteToProject({ project_id: Number(id), user_id: Number(invite.user_id), is_creator: !!invite.is_creator })
      setInvite({ user_id: '', is_creator: false })
      await load()
    } catch (e) { setError(e.message) }
  }

  const createTask = async (e) => {
    e.preventDefault()
    try {
      const payload = { ...taskForm, deadline: new Date(taskForm.deadline).toISOString() }
      await api.createTask(Number(id), Number(assigneeId), payload)
      setTaskForm({ title: '', description: '', deadline: '' })
      setAssigneeId('')
      await load() // Reload to show new task
    } catch (e) { setError(e.message) }
  }

  const isCreator = React.useMemo(() => {
    if (!project || !me) return false
    return (project.members || []).some(m => m.user_id === me.id && m.is_creator)
  }, [project, me])

  const isMember = React.useMemo(() => {
    if (!project || !me) return false
    return (project.members || []).some(m => m.user_id === me.id)
  }, [project, me])

  const saveProject = async (e) => {
    e.preventDefault()
    try {
      await api.updateProject(Number(id), editProject)
      await load()
    } catch (e) { setError(e.message) }
  }

  const deleteProject = async () => {
    if (!confirm('Delete this project?')) return
    try {
      await api.deleteProject(Number(id))
      navigate('/projects')
    } catch (e) { setError(e.message) }
  }

  return (
    <div className="page">
      <h1 className="h1">Project #{id}</h1>
      {error && <div className="alert error">{error}</div>}
      {project ? (
        <div className="grid2">
          <div>
            <div className="card">
              <div className="title">{project.title}</div>
              <div className="muted">{project.description}</div>
            </div>

            <div className="card">
              <div className="subtitle">Members</div>
              <ul className="list-plain">
                {(project.members || []).map(m => (
                  <li key={m.user_id}>
                    <span className="badge">{m.is_creator ? 'owner' : 'member'}</span> {m.username} (id: {m.user_id})
                  </li>
                ))}
              </ul>
            </div>

            <div className="card">
              <div className="subtitle">Tasks {isMember ? `(${tasks.length})` : ''}</div>
              {!isMember ? (
                <div className="muted">Only project members can view tasks.</div>
              ) : tasks.length === 0 ? (
                <div className="muted">No tasks yet. Create one using the form on the right.</div>
              ) : (
                <div className="list-plain">
                  {tasks.map(task => (
                    <div key={task.id} className="card" style={{ marginBottom: '8px', opacity: task.completed ? 0.6 : 1 }}>
                      <div className="card-title">{task.title}</div>
                      <div className="muted">{task.description}</div>
                      <div className="card-meta">
                        <span className="muted">Deadline: {new Date(task.deadline).toLocaleString()}</span>
                        <span className="muted">Assignees: {task.members.map(m => m.username).join(', ')}</span>
                      </div>
                      <div className="actions">
                        <button className="btn" onClick={async () => { try { await api.updateTask(task.id, { completed: !task.completed }); await load(); } catch (e) { setError(e.message) } }}>
                          {task.completed ? 'Mark as not done' : 'Mark as done'}
                        </button>
                        {isCreator && (
                          <button className="btn danger" onClick={async () => { if (!confirm('Delete this task?')) return; try { await api.deleteTask(task.id); await load(); } catch (e) { setError(e.message) } }}>Delete</button>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          <div>
            {isCreator && (
              <form className="card form" onSubmit={doInvite}>
                <div className="subtitle">Invite user to project</div>
                <div className="row">
                  <input placeholder="User id" value={invite.user_id} onChange={e => setInvite(v => ({ ...v, user_id: e.target.value }))} required />
                  <label className="checkbox"><input type="checkbox" checked={invite.is_creator} onChange={e => setInvite(v => ({ ...v, is_creator: e.target.checked }))} /> Creator</label>
                  <button className="btn" type="submit">Invite</button>
                </div>
              </form>
            )}

            {isMember && (
            <form className="card form" onSubmit={createTask}>
              <div className="subtitle">Create task</div>
              <div className="row">
                <input placeholder="Title" value={taskForm.title} onChange={e => setTaskForm(v => ({ ...v, title: e.target.value }))} required />
                <input placeholder="Description" value={taskForm.description} onChange={e => setTaskForm(v => ({ ...v, description: e.target.value }))} />
                <input type="datetime-local" value={taskForm.deadline} onChange={e => setTaskForm(v => ({ ...v, deadline: e.target.value }))} required />
                <input placeholder="Assignee user id" value={assigneeId} onChange={e => setAssigneeId(e.target.value)} required />
                <button className="btn primary" type="submit">Create</button>
              </div>
            </form>
            )}

            {isCreator && (
              <form className="card form" onSubmit={saveProject}>
                <div className="subtitle">Project settings</div>
                <div className="row">
                  <input placeholder="Title" value={editProject.title} onChange={e => setEditProject(v => ({ ...v, title: e.target.value }))} required />
                  <input placeholder="Description" value={editProject.description} onChange={e => setEditProject(v => ({ ...v, description: e.target.value }))} />
                  <button className="btn" type="submit">Save</button>
                  <button className="btn danger" type="button" onClick={deleteProject}>Delete</button>
                </div>
              </form>
            )}
          </div>
        </div>
      ) : (
        <div className="card">Load a project by id first.</div>
      )}
    </div>
  )
}

