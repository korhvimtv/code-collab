const API_URL = 'http://localhost:8000'

function getToken() {
  return localStorage.getItem('token') || ''
}

function setToken(token) {
  if (token) localStorage.setItem('token', token)
  else localStorage.removeItem('token')
  
  window.dispatchEvent(new Event('authChange'))
}

async function request(path, options = {}) {
  const authHeader = getToken() ? { 'Authorization': `Bearer ${getToken()}` } : {}
  let res
  try {
    res = await fetch(API_URL + path, {
      headers: { 'Content-Type': 'application/json', ...authHeader, ...(options.headers || {}) },
      ...options,
    })
  } catch (e) {
    throw new Error('Network error: ' + (e?.message || 'Failed to fetch'))
  }
  if (!res.ok) {
    let bodyText = ''
    try { bodyText = await res.text() } catch (_) {}
    let message = res.status + ' ' + res.statusText
    try {
      const json = bodyText ? JSON.parse(bodyText) : null
      message = (json && (json.detail || json.message)) || message
    } catch (_) {
      if (bodyText) message = bodyText
    }
    if (res.status === 401) {
      setToken('')
    }
    throw new Error(message)
  }
  const text = await res.text()
  return text ? JSON.parse(text) : null
}

export const api = {
  saveToken: setToken,
  getToken,
  logout: () => setToken(''),
  register: (data) => request('/auth/register', { method: 'POST', body: JSON.stringify(data) }),
  login: async (data) => {
    const res = await request('/auth/login', { method: 'POST', body: JSON.stringify(data) })
    setToken(res.access_token)
    return res
  },
  me: () => request('/me'),
  myProjects: () => request('/me/projects'),

  listUsers: () => request('/users'),
  getUser: (id) => request(`/users/${id}`),
  getUserByUsername: (username) => request(`/users/by-username/${encodeURIComponent(username)}`),
  getUserProjectsByUsername: (username) => request(`/users/by-username/${encodeURIComponent(username)}/projects`),
  searchUsersByUsername: (username) => request(`/users/search?username=${encodeURIComponent(username)}`),
  createUser: (data) => request('/users', { method: 'POST', body: JSON.stringify(data) }),
  updateUser: (id, data) => request(`/users/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  deleteUser: (id) => request(`/users/${id}`, { method: 'DELETE' }),

  createProject: (data) => request(`/projects`, { method: 'POST', body: JSON.stringify(data) }),
  listAllProjects: () => request(`/projects`),
  searchProjectsByTitle: (title) => request(`/projects/search?title=${encodeURIComponent(title)}`),
  getProject: (id) => request(`/projects/${id}`),
  updateProject: (id, data) => request(`/projects/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  deleteProject: (id) => request(`/projects/${id}`, { method: 'DELETE' }),
  inviteToProject: (payload) => request('/projects/invite', { method: 'POST', body: JSON.stringify(payload) }),

  createTask: (projectId, userId, data) => request(`/tasks?project_id=${projectId}&user_id=${userId}`, { method: 'POST', body: JSON.stringify(data) }),
  getProjectTasks: (projectId) => request(`/projects/${projectId}/tasks`),
  getTask: (id) => request(`/task/${id}`),
  updateTask: (id, data) => request(`/task/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  deleteTask: (id) => request(`/task/${id}`, { method: 'DELETE' }),
  inviteToTask: (id, payload) => request(`/task/${id}`, { method: 'POST', body: JSON.stringify(payload) }),
}

export function useAsync(asyncFn, deps = []) {
  const [state, setState] = React.useState({ loading: false, error: null, data: null })
  const run = React.useCallback(async (...args) => {
    setState({ loading: true, error: null, data: null })
    try {
      const data = await asyncFn(...args)
      setState({ loading: false, error: null, data })
      return data
    } catch (e) {
      setState({ loading: false, error: e, data: null })
      throw e
    }
  }, deps)
  return [state, run]
}

