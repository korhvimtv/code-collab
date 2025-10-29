import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../api/client'

export default function SearchBar() {
  const navigate = useNavigate()
  const [query, setQuery] = useState('')
  const [searchType, setSearchType] = useState('projects')
  const [results, setResults] = useState([])
  const [showResults, setShowResults] = useState(false)
  const [loading, setLoading] = useState(false)

  const handleSearch = async (e) => {
    e.preventDefault()
    if (!query.trim()) return

    setLoading(true)
    try {
      let searchResults = []
      if (searchType === 'projects') {
        searchResults = await api.searchProjectsByTitle(query)
      } else {
        searchResults = await api.searchUsersByUsername(query)
      }
      setResults(searchResults)
      setShowResults(true)
    } catch (error) {
      console.error('Search error:', error)
      setResults([])
      setShowResults(true)
    } finally {
      setLoading(false)
    }
  }

  const handleResultClick = (result) => {
    if (searchType === 'projects') {
      navigate(`/projects/${result.id}`)
    } else {
      navigate(`/users/${result.username}`)
    }
    setShowResults(false)
    setQuery('')
  }

  return (
    <div style={{ position: 'relative', display: 'flex', alignItems: 'center', gap: '8px' }}>
      <form onSubmit={handleSearch} style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
        <select 
          value={searchType} 
          onChange={(e) => setSearchType(e.target.value)}
          style={{ padding: '4px 8px', borderRadius: '4px', border: '1px solid #ccc' }}
        >
          <option value="projects">Projects</option>
          <option value="users">Users</option>
        </select>
        <input
          type="text"
          placeholder={`Search ${searchType}...`}
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          style={{ padding: '4px 8px', borderRadius: '4px', border: '1px solid #ccc', minWidth: '200px' }}
        />
        <button type="submit" disabled={loading} style={{ padding: '4px 12px', borderRadius: '4px', border: '1px solid #007bff', background: '#007bff', color: 'white', cursor: 'pointer' }}>
          {loading ? '...' : 'Search'}
        </button>
      </form>
      
      {showResults && (
        <div style={{ 
          position: 'absolute', 
          top: '100%', 
          left: '0', 
          right: '0', 
          background: 'white', 
          border: '1px solid #ccc', 
          borderRadius: '4px', 
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
          zIndex: 1000,
          maxHeight: '300px',
          overflowY: 'auto'
        }}>
          {results.length === 0 ? (
            <div style={{ padding: '12px', color: '#666' }}>No results found</div>
          ) : (
            results.map((result) => (
              <div
                key={searchType === 'projects' ? result.id : result.id}
                onClick={() => handleResultClick(result)}
                style={{ 
                  padding: '12px', 
                  cursor: 'pointer', 
                  borderBottom: '1px solid #eee',
                  ':hover': { background: '#f5f5f5' }
                }}
                onMouseEnter={(e) => e.target.style.background = '#f5f5f5'}
                onMouseLeave={(e) => e.target.style.background = 'white'}
              >
                <div style={{ fontWeight: 'bold' }}>
                  {searchType === 'projects' ? result.title : result.name}
                </div>
                <div style={{ fontSize: '0.9em', color: '#666' }}>
                  {searchType === 'projects' ? result.description : `@${result.username}`}
                </div>
              </div>
            ))
          )}
          <div style={{ padding: '8px', textAlign: 'center', borderTop: '1px solid #eee' }}>
            <button 
              onClick={() => setShowResults(false)}
              style={{ background: 'none', border: 'none', color: '#666', cursor: 'pointer', fontSize: '0.9em' }}
            >
              Close
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

