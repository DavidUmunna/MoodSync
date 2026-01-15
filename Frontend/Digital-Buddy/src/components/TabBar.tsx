import { NavLink } from 'react-router-dom'

export const TabBar = () => {
  return (
    <footer className='border-t border-border'>
      <nav className='flex items-center justify-around px-4 py-3 text-sm'>
        <NavLink to='/home'>Today</NavLink>
        <NavLink to='/log'>Log</NavLink>
        <NavLink to='/insights'>Insights</NavLink>
        <NavLink to='/history'>History</NavLink>
        <NavLink to='/settings'>Settings</NavLink>
      </nav>
    </footer>
  )
}
