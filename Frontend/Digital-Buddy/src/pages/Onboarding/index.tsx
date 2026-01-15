import { useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Brain, BookOpen, Feather, Moon, Zap, Battery, BatteryFull } from 'lucide-react'
import { Button } from '../../components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../components/ui/card'
import { cn } from '../../lib/utils'

type EnergyLevel = 'Low' | 'Medium' | 'High'
type TaskType = 'Deep work' | 'Study' | 'Light work' | 'Rest'

const moodOptions = [
  { value: 1, label: '😞', text: 'Low' },
  { value: 2, label: '😕', text: 'Meh' },
  { value: 3, label: '😐', text: 'Neutral' },
  { value: 4, label: '🙂', text: 'Good' },
  { value: 5, label: '😄', text: 'Great' },
]

const energyOptions: Array<{ value: EnergyLevel; icon: React.ComponentType<{ className?: string }> }> = [
  { value: 'Low', icon: Battery },
  { value: 'Medium', icon: Zap },
  { value: 'High', icon: BatteryFull },
]

const taskOptions: Array<{
  value: TaskType
  icon: React.ComponentType<{ className?: string }>
  description: string
}> = [
  { value: 'Deep work', icon: Brain, description: 'Focused, high-value tasks' },
  { value: 'Study', icon: BookOpen, description: 'Learning and practice' },
  { value: 'Light work', icon: Feather, description: 'Shallow or admin work' },
  { value: 'Rest', icon: Moon, description: 'Recover and recharge' },
]

export const Onboarding = () => {
  const [mood, setMood] = useState(3)
  const [energy, setEnergy] = useState<EnergyLevel>('Medium')
  const [taskType, setTaskType] = useState<TaskType>('Deep work')
  const navigate = useNavigate()

  const selectedMood = useMemo(() => moodOptions.find((option) => option.value === mood), [mood])

  return (
    <section className='min-h-[calc(100vh-8rem)] flex items-center justify-center px-4 py-10'>
      <Card className='w-full max-w-xl'>
        <CardHeader className='space-y-2 text-center'>
          <CardTitle className='text-2xl'>First Check-in</CardTitle>
          <CardDescription>
            Tell us how you feel right now so we can tailor your day.
          </CardDescription>
        </CardHeader>
        <CardContent className='space-y-8'>
          <div className='space-y-3'>
            <p className='text-sm font-medium'>Mood</p>
            <div className='grid grid-cols-5 gap-2'>
              {moodOptions.map((option) => (
                <button
                  key={option.value}
                  type='button'
                  onClick={() => setMood(option.value)}
                  className={cn(
                    'flex flex-col items-center justify-center gap-1 rounded-lg border px-2 py-3 text-xl transition',
                    mood === option.value
                      ? 'border-primary bg-primary/10'
                      : 'border-border hover:border-primary/50'
                  )}
                >
                  <span aria-hidden>{option.label}</span>
                  <span className='text-xs text-muted-foreground'>{option.text}</span>
                </button>
              ))}
            </div>
            <p className='text-xs text-muted-foreground'>
              Selected: {selectedMood?.text ?? 'Neutral'}
            </p>
          </div>

          <div className='space-y-3'>
            <p className='text-sm font-medium'>Energy</p>
            <div className='flex flex-wrap gap-3'>
              {energyOptions.map((option) => {
                const Icon = option.icon
                const active = energy === option.value
                return (
                  <button
                    key={option.value}
                    type='button'
                    onClick={() => setEnergy(option.value)}
                    className={cn(
                      'flex items-center gap-2 rounded-full border px-4 py-2 text-sm transition',
                      active ? 'border-primary bg-primary/10' : 'border-border hover:border-primary/50'
                    )}
                  >
                    <Icon className='h-4 w-4' />
                    {option.value}
                  </button>
                )
              })}
            </div>
          </div>

          <div className='space-y-3'>
            <p className='text-sm font-medium'>Task type</p>
            <div className='grid gap-3 sm:grid-cols-2'>
              {taskOptions.map((option) => {
                const Icon = option.icon
                const active = taskType === option.value
                return (
                  <button
                    key={option.value}
                    type='button'
                    onClick={() => setTaskType(option.value)}
                    className={cn(
                      'flex items-start gap-3 rounded-lg border px-4 py-3 text-left transition',
                      active ? 'border-primary bg-primary/10' : 'border-border hover:border-primary/50'
                    )}
                  >
                    <Icon className='h-5 w-5 mt-1' />
                    <div>
                      <p className='text-sm font-semibold'>{option.value}</p>
                      <p className='text-xs text-muted-foreground'>{option.description}</p>
                    </div>
                  </button>
                )
              })}
            </div>
          </div>

          <Button className='w-full h-12 text-base' onClick={() => navigate('/home')}>
            Start my day
          </Button>
        </CardContent>
      </Card>
    </section>
  )
}
