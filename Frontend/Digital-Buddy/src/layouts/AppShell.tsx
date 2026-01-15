import { Outlet } from 'react-router-dom'
import { NavBar } from '../components/NavBar'
import { TabBar } from '../components/TabBar'

export const AppShell = () => {
  return (
    <div className='min-h-screen bg-background text-foreground flex flex-col'>
      <NavBar />
      <main className='flex-1 px-4 py-6'>
        <Outlet />
      </main>
      <TabBar />
    </div>
  )
}
