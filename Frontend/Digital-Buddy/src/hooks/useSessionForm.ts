import { useState } from 'react'
import type { SessionPayload } from '../types/session'

export const useSessionForm = (initialValues: SessionPayload) => {
  const [values, setValues] = useState<SessionPayload>(initialValues)

  const setField = <K extends keyof SessionPayload>(field: K, value: SessionPayload[K]) => {
    setValues((prev) => ({ ...prev, [field]: value }))
  }

  const handleChange = (event: React.ChangeEvent<HTMLInputElement >) => {
    const { name, value, type, checked } = event.target
    if (type === 'checkbox') {
      setField(name as keyof SessionPayload, checked as SessionPayload[keyof SessionPayload])
      return
    }

    if (name === 'mood') {
      setField('mood', Number(value))
      return
    }

    setField(name as keyof SessionPayload, value as SessionPayload[keyof SessionPayload])
  }

  return {
    values,
    setValues,
    setField,
    handleChange,
  }
}
