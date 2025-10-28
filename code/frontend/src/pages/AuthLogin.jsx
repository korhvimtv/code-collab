import React from 'react'
import { useNavigate, NavLink } from 'react-router-dom'
import { api } from '../api/client'

export default function AuthLogin() {
  const nav = useNavigate()
  const [form, setForm] = React.useState({ username: '', password: '' })
  const [error, setError] = React.useState(null)

  const submit = async (e) => {
    e.preventDefault()
    setError(null)
    try {
      api.logout()
      await api.login(form)
      nav('/me')
    } catch (e) { setError(e.message) }
  }

  return (
    <div className="page">
      <h1 className="h1">Login</h1>
      {error && <div className="alert error">{error}</div>}
      <form className="card form" onSubmit={submit}>
        <div className="row">
          <input placeholder="Username" value={form.username} onChange={e => setForm(v => ({ ...v, username: e.target.value }))} required />
          <input type="password" placeholder="Password" value={form.password} onChange={e => setForm(v => ({ ...v, password: e.target.value }))} required />
          <button className="btn primary" type="submit">Login</button>
        </div>
      </form>
      <div className="card">No account? <NavLink to="/register">Register</NavLink></div>
    </div>
  )
}

