import { Link } from 'react-router-dom'

export const NavBar = () => {
  return (
    <header className='border-b border-border'>
      <nav className='flex items-center justify-between px-4 py-3'>
        <Link to='/home' className='text-lg font-semibold'>
          MoodSync
        </Link>
      </nav>
    </header>
  )
}
