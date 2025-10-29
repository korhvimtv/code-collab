import React from 'react'
import { api } from '../api/client'

export default function TasksPage() {
  const [taskId, setTaskId] = React.useState('')
  const [task, setTask] = React.useState(null)
  const [invite, setInvite] = React.useState({ user_id: '', project_id: '', task_id: '' })
  const [updateForm, setUpdateForm] = React.useState({ title: '', description: '' })
  const [error, setError] = React.useState(null)

  const load = async () => {
    if (!taskId) return
    setError(null)
    try { setTask(await api.getTask(taskId)) } catch (e) { setError(e.message); setTask(null) }
  }

  const doInvite = async (e) => {
    e.preventDefault()
    try {
      await api.inviteToTask(taskId, { user_id: Number(invite.user_id), project_id: Number(invite.project_id), task_id: Number(taskId) })
      setInvite({ user_id: '', project_id: '', task_id: '' })
      await load()
    } catch (e) { setError(e.message) }
  }

  const doUpdate = async (e) => {
    e.preventDefault()
    try {
      await api.updateTask(taskId, updateForm)
      setUpdateForm({ title: '', description: '' })
      await load()
    } catch (e) { setError(e.message) }
  }

  const remove = async () => {
    if (!task) return
    if (!confirm('Delete task?')) return
    try { await api.deleteTask(task.id); setTask(null); setTaskId('') } catch (e) { setError(e.message) }
  }

  return (
    <div className="page">
      <h1 className="h1">Tasks</h1>

      <div className="card form">
        <div className="row">
          <input placeholder="Task id" value={taskId} onChange={e => setTaskId(e.target.value)} />
          <button className="btn" onClick={load}>Load</button>
        </div>
      </div>

      {error && <div className="alert error">{error}</div>}

      {task && (
        <div className="grid2">
          <div className="card">
            <div className="title">{task.title}</div>
            <div className="muted">{task.description}</div>
            <div className="muted">Deadline: {new Date(task.deadline).toLocaleString()}</div>
            <div className="muted">Project: {task.project?.project_title} (id: {task.project?.project_id})</div>
            <div className="muted" style={{ marginTop: 8 }}>Members:</div>
            <ul className="list-plain">
              {(task.members || []).map(m => (
                <li key={m.user_id}>@{m.username} (id: {m.user_id})</li>
              ))}
            </ul>
            <div className="actions">
              <button className="btn danger" onClick={remove}>Delete</button>
            </div>
          </div>

          <div>
            <form className="card form" onSubmit={doInvite}>
              <div className="subtitle">Invite user</div>
              <div className="row">
                <input placeholder="User id" value={invite.user_id} onChange={e => setInvite(v => ({ ...v, user_id: e.target.value }))} required />
                <input placeholder="Project id" value={invite.project_id} onChange={e => setInvite(v => ({ ...v, project_id: e.target.value }))} required />
                <button className="btn" type="submit">Invite</button>
              </div>
            </form>

            <form className="card form" onSubmit={doUpdate}>
              <div className="subtitle">Update task</div>
              <div className="row">
                <input placeholder="Title" value={updateForm.title} onChange={e => setUpdateForm(v => ({ ...v, title: e.target.value }))} />
                <input placeholder="Description" value={updateForm.description} onChange={e => setUpdateForm(v => ({ ...v, description: e.target.value }))} />
                <button className="btn primary" type="submit">Update</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}




