import { useMemo, useState } from 'react'
import { Brain, BookOpen, Feather, Moon } from 'lucide-react'
import { createSession } from '../../api/sessions'
import { ApiError } from '../../api/client'
import { Button } from '../../components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../components/ui/card'

type MoodOption = 1 | 2 | 3 | 4 | 5
type EnergyLevel = 'Low' | 'Medium' | 'High'
type TaskType = 'Deep work' | 'Study' | 'Light work' | 'Rest'

interface SessionFormValues {
  mood: MoodOption | null
  energy: EnergyLevel | null
  taskType: TaskType | null
  goodSession: boolean
}

const moodOptions: Array<{ value: MoodOption; label: string }> = [
  { value: 1, label: '😞' },
  { value: 2, label: '😐' },
  { value: 3, label: '🙂' },
  { value: 4, label: '😄' },
  { value: 5, label: '🔥' },
]

const energyOptions: EnergyLevel[] = ['Low', 'Medium', 'High']

const taskOptions: Array<{ value: TaskType; icon: React.ComponentType<{ className?: string }> }> =
  [
    { value: 'Deep work', icon: Brain },
    { value: 'Study', icon: BookOpen },
    { value: 'Light work', icon: Feather },
    { value: 'Rest', icon: Moon },
  ]

const MoodButton = ({
  option,
  selected,
  onSelect,
}: {
  option: { value: MoodOption; label: string }
  selected: boolean
  onSelect: (value: MoodOption) => void
}) => (
  <button
    type='button'
    onClick={() => onSelect(option.value)}
    className={[
      'flex h-12 items-center justify-center rounded-lg border text-2xl transition',
      selected
        ? 'border-indigo-500 bg-indigo-500/10'
        : 'border-slate-800 hover:border-indigo-500/60',
    ].join(' ')}
  >
    <span aria-hidden>{option.label}</span>
  </button>
)

const EnergyPill = ({
  value,
  selected,
  onSelect,
}: {
  value: EnergyLevel
  selected: boolean
  onSelect: (value: EnergyLevel) => void
}) => (
  <button
    type='button'
    onClick={() => onSelect(value)}
    className={[
      'rounded-full border px-4 py-2 text-sm transition',
      selected
        ? 'border-indigo-500 bg-indigo-500/10 text-slate-100'
        : 'border-slate-800 text-slate-400 hover:border-indigo-500/60 hover:text-slate-100',
    ].join(' ')}
  >
    {value}
  </button>
)

const TaskCard = ({
  value,
  icon: Icon,
  selected,
  onSelect,
}: {
  value: TaskType
  icon: React.ComponentType<{ className?: string }>
  selected: boolean
  onSelect: (value: TaskType) => void
}) => (
  <button
    type='button'
    onClick={() => onSelect(value)}
    className={[
      'flex items-center gap-3 rounded-lg border px-4 py-3 text-left transition',
      selected
        ? 'border-indigo-500 bg-indigo-500/10'
        : 'border-slate-800 hover:border-indigo-500/60',
    ].join(' ')}
  >
    <Icon className='h-5 w-5 text-slate-200' />
    <span className='text-sm text-slate-100'>{value}</span>
  </button>
)

const SessionForm = ({
  values,
  onChange,
  onSubmit,
  submitting,
  feedback,
}: {
  values: SessionFormValues
  onChange: (next: Partial<SessionFormValues>) => void
  onSubmit: () => Promise<void>
  submitting: boolean
  feedback: { type: 'success' | 'error'; message: string } | null
}) => {
  const canSubmit = Boolean(values.mood && values.energy && values.taskType)

  return (
    <form
      className='space-y-8'
      onSubmit={(event) => {
        event.preventDefault()
        if (canSubmit && !submitting) {
          onSubmit()
        }
      }}
    >
      <div className='mb-8 space-y-3'>
        <h3 className='text-sm font-medium text-slate-100'>Mood</h3>
        <div className='grid grid-cols-5 gap-2'>
          {moodOptions.map((option) => (
            <MoodButton
              key={option.value}
              option={option}
              selected={values.mood === option.value}
              onSelect={(value) => onChange({ mood: value })}
            />
          ))}
        </div>
      </div>

      <div className='mb-8 space-y-3'>
        <h3 className='text-sm font-medium text-slate-100'>Energy</h3>
        <div className='flex flex-wrap gap-2'>
          {energyOptions.map((energy) => (
            <EnergyPill
              key={energy}
              value={energy}
              selected={values.energy === energy}
              onSelect={(value) => onChange({ energy: value })}
            />
          ))}
        </div>
      </div>

      <div className='mb-8 space-y-3'>
        <h3 className='text-sm font-medium text-slate-100'>Task type</h3>
        <div className='grid gap-3 sm:grid-cols-2'>
          {taskOptions.map((task) => (
            <TaskCard
              key={task.value}
              value={task.value}
              icon={task.icon}
              selected={values.taskType === task.value}
              onSelect={(value) => onChange({ taskType: value })}
            />
          ))}
        </div>
      </div>

      <div className='mb-8 flex items-center justify-between rounded-lg border border-slate-800 px-4 py-3'>
        <div className='space-y-1'>
          <p className='text-sm text-slate-100'>This was a good session</p>
          <p className='text-xs text-slate-400'>Optional. Helps with recommendations.</p>
        </div>
        <button
          type='button'
          onClick={() => onChange({ goodSession: !values.goodSession })}
          className={[
            'h-6 w-11 rounded-full border transition',
            values.goodSession ? 'border-indigo-500 bg-indigo-500/50' : 'border-slate-800 bg-slate-900',
          ].join(' ')}
          aria-pressed={values.goodSession}
        >
          <span
            className={[
              'block h-5 w-5 rounded-full bg-slate-100 transition',
              values.goodSession ? 'translate-x-5' : 'translate-x-1',
            ].join(' ')}
          />
        </button>
      </div>

      {feedback ? (
        <p
          className={[
            'text-sm',
            feedback.type === 'success' ? 'text-emerald-400' : 'text-rose-400',
          ].join(' ')}
        >
          {feedback.message}
        </p>
      ) : null}

      <Button
        className='w-full h-12 bg-indigo-500 text-slate-100 hover:bg-indigo-400 text-black'
        type='submit'
        disabled={!canSubmit || submitting}
      >
        {submitting ? 'Saving...' : 'Save session'}
      </Button>
    </form>
  )
}

export const LogSession = () => {
  const [values, setValues] = useState<SessionFormValues>({
    mood: null,
    energy: null,
    taskType: null,
    goodSession: false,
  })
  const [submitting, setSubmitting] = useState(false)
  const [feedback, setFeedback] = useState<{ type: 'success' | 'error'; message: string } | null>(
    null
  )

  const handleSubmit = async () => {
    setSubmitting(true)
    setFeedback(null)
    try {
      if (!values.mood || !values.energy || !values.taskType) {
        setFeedback({ type: 'error', message: 'Select mood, energy, and task type.' })
        return
      }

      await createSession({
        mood: values.mood,
        energy: values.energy,
        taskType: values.taskType,
        goodSession: values.goodSession,
      })
      setFeedback({ type: 'success', message: 'Session saved.' })
      setValues({ mood: null, energy: null, taskType: null, goodSession: false })
    } catch (err) {
      const message =
        err instanceof ApiError
          ? err.message
          : err instanceof Error
          ? err.message
          : 'Unable to save session. Try again.'
      setFeedback({ type: 'error', message })
    } finally {
      setSubmitting(false)
    }
  }

  const description = useMemo(
    () => 'Log how you feel right now so your insights stay sharp.',
    []
  )

  return (
    <section className='min-h-[calc(100vh-8rem)] bg-slate-950 text-slate-100 px-4 py-10 flex items-center justify-center'>
      <Card className='w-full max-w-2xl border-slate-800 bg-slate-900 p-6'>
        <CardHeader className='p-0 mb-8 space-y-2'>
          <CardTitle className='text-2xl text-slate-100'>Log Session</CardTitle>
          <CardDescription className='text-slate-400'>{description}</CardDescription>
        </CardHeader>
        <CardContent className='p-0'>
          <SessionForm
            values={values}
            onChange={(next) => setValues((prev) => ({ ...prev, ...next }))}
            onSubmit={handleSubmit}
            submitting={submitting}
            feedback={feedback}
          />
        </CardContent>
      </Card>
    </section>
  )
}
