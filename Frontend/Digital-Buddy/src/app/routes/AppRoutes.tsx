import { Navigate, Route, Routes } from 'react-router-dom'
import { RequireAuth } from '../../auth/RequireAuth'
import { AppShell } from '../../layouts/AppShell'
import { Login } from '../../pages/Login'
import { Register } from '../../pages/Register'
import { Onboarding } from '../../pages/Onboarding'
import { Home } from '../../pages/Home'
import { LogSession } from '../../pages/LogSession'
import { Insights } from '../../pages/Insights'
import { History } from '../../pages/History'
import { Settings } from '../../pages/Settings'

export const AppRoutes = () => {
  return (
    <Routes>
      <Route path='/' element={<Navigate to='/login' replace />} />
      <Route path='/login' element={<Login />} />
      <Route path='/register' element={<Register />} />
      <Route element={<RequireAuth />}>
        <Route path='/onboarding' element={<Onboarding />} />
        <Route element={<AppShell />}>
          <Route path='/home' element={<Home />} />
          <Route path='/log' element={<LogSession />} />
          <Route path='/insights' element={<Insights />} />
          <Route path='/history' element={<History />} />
          <Route path='/settings' element={<Settings />} />
        </Route>
      </Route>
      <Route path='*' element={<Navigate to='/login' replace />} />
    </Routes>
  )
}
