export type EnergyLevel = 'Low' | 'Medium' | 'High'
export type TaskType = 'Deep work' | 'Study' | 'Light work' | 'Rest'

export interface SessionPayload {
  mood: number
  energy: EnergyLevel
  taskType: TaskType
  goodSession?: boolean
}
