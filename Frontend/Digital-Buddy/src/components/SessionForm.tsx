import type { SessionPayload } from '../types/session'

const MOOD_OPTIONS = [
  { value: 1, label: '😞' },
  { value: 2, label: '😕' },
  { value: 3, label: '😐' },
  { value: 4, label: '🙂' },
  { value: 5, label: '😄' },
]

const ENERGY_OPTIONS: Array<SessionPayload['energy']> = ['Low', 'Medium', 'High']
const TASK_OPTIONS: Array<SessionPayload['taskType']> = ['Deep work', 'Study', 'Light work', 'Rest']

interface SessionFormProps {
  values: SessionPayload
  onChange: (event: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => void
  onSubmit: (event: React.FormEvent<HTMLFormElement>) => void
  submitting: boolean
  error: string | null
  includeGoodSession?: boolean
  submitLabel: string
}

export const SessionForm = ({
  values,
  onChange,
  onSubmit,
  submitting,
  error,
  includeGoodSession = false,
  submitLabel,
}: SessionFormProps) => {
  return (
    <form onSubmit={onSubmit}>
      <fieldset>
        <legend>Mood</legend>
        {MOOD_OPTIONS.map((option) => (
          <label key={option.value}>
            <input
              type='radio'
              name='mood'
              value={option.value}
              checked={values.mood === option.value}
              onChange={onChange}
              disabled={submitting}
            />
            {option.label}
          </label>
        ))}
      </fieldset>

      <fieldset>
        <legend>Energy</legend>
        {ENERGY_OPTIONS.map((option) => (
          <label key={option}>
            <input
              type='radio'
              name='energy'
              value={option}
              checked={values.energy === option}
              onChange={onChange}
              disabled={submitting}
            />
            {option}
          </label>
        ))}
      </fieldset>

      <label>
        Task type
        <select name='taskType' value={values.taskType} onChange={onChange} disabled={submitting}>
          {TASK_OPTIONS.map((option) => (
            <option key={option} value={option}>
              {option}
            </option>
          ))}
        </select>
      </label>

      {includeGoodSession ? (
        <label>
          <input
            type='checkbox'
            name='goodSession'
            checked={Boolean(values.goodSession)}
            onChange={onChange}
            disabled={submitting}
          />
          Good session
        </label>
      ) : null}

      {error ? <p>{error}</p> : null}

      <button type='submit' disabled={submitting}>
        {submitting ? 'Saving...' : submitLabel}
      </button>
    </form>
  )
}
