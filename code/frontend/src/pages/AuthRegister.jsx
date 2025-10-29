import React from 'react'
import { useNavigate, NavLink } from 'react-router-dom'
import { api } from '../api/client'

export default function AuthRegister() {
  const nav = useNavigate()
  const [form, setForm] = React.useState({ name: '', username: '', email: '', password: '' })
  const [error, setError] = React.useState(null)

  const submit = async (e) => {
    e.preventDefault()
    setError(null)
    try {
      await api.register(form)
      await api.login({ username: form.username, password: form.password })
      nav('/me')
    } catch (e) { setError(e.message) }
  }

  return (
    <div className="page">
      <h1 className="h1">Register</h1>
      {error && <div className="alert error">{error}</div>}
      <form className="card form" onSubmit={submit}>
        <div className="row">
          <input placeholder="Name" value={form.name} onChange={e => setForm(v => ({ ...v, name: e.target.value }))} required />
          <input placeholder="Username" value={form.username} onChange={e => setForm(v => ({ ...v, username: e.target.value }))} required />
          <input type="email" placeholder="Email" value={form.email} onChange={e => setForm(v => ({ ...v, email: e.target.value }))} required />
          <input type="password" placeholder="Password" value={form.password} onChange={e => setForm(v => ({ ...v, password: e.target.value }))} required />
          <button className="btn primary" type="submit">Create account</button>
        </div>
      </form>
      <div className="card">Have an account? <NavLink to="/login">Login</NavLink></div>
    </div>
  )
}





