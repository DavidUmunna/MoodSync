import { AppProviders } from './providers/AppProviders'
import { AppRoutes } from './routes/AppRoutes'

export const App = () => {
  return (
    <AppProviders>
      <AppRoutes />
    </AppProviders>
  )
}
