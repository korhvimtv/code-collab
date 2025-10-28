import { Routes, Route, NavLink, Navigate } from 'react-router-dom'
import UsersPage from './pages/UsersPage.jsx'
import ProjectsPage from './pages/ProjectsPage.jsx'
import ProjectDetailPage from './pages/ProjectDetailPage.jsx'
import AuthLogin from './pages/AuthLogin.jsx'
import AuthRegister from './pages/AuthRegister.jsx'
import MePage from './pages/MePage.jsx'
import { useAuth } from './hooks/useAuth'
import UserDetailPage from './pages/UserDetailPage.jsx'
import SearchBar from './components/SearchBar.jsx'

export default function App() {
  const { isAuthed } = useAuth()
  return (
    <div className="app-root">
      <header className="app-header">
        <div className="container">
          <nav className="nav">
            <NavLink to="/" className="brand">CodeCollab</NavLink>
            <NavLink to="/projects" className="link">Projects</NavLink>
            {isAuthed && <NavLink to="/users" className="link">Users</NavLink>}
            <div style={{ marginLeft: 'auto' }} />
            <SearchBar />
            {isAuthed ? (
              <NavLink to="/me" className="link">Me</NavLink>
            ) : (
              <NavLink to="/login" className="link">Sign In</NavLink>
            )}
          </nav>
        </div>
      </header>

      <main className="container">
        <Routes>
          <Route path="/" element={<Navigate to="/projects" replace />} />
          <Route path="/login" element={<AuthLogin />} />
          <Route path="/register" element={<AuthRegister />} />
          <Route path="/me" element={<MePage />} />
          <Route path="/users" element={<UsersPage />} />
          <Route path="/users/:username" element={<UserDetailPage />} />
          <Route path="/projects" element={<ProjectsPage />} />
          <Route path="/projects/:id" element={<ProjectDetailPage />} />
        </Routes>
      </main>
    </div>
  )
}

