import { createContext, useContext, useState, ReactNode } from 'react'

interface FiscalYearContextType {
  fiscalYear: number
  setFiscalYear: (year: number) => void
  availableYears: number[]
}

const FiscalYearContext = createContext<FiscalYearContextType | undefined>(undefined)

export function FiscalYearProvider({ children }: { children: ReactNode }) {
  const currentYear = new Date().getFullYear()
  const [fiscalYear, setFiscalYear] = useState(currentYear)
  
  // Générer une liste d'années (5 ans dans le passé jusqu'à l'année courante)
  const availableYears = Array.from({ length: 6 }, (_, i) => currentYear - 5 + i)

  return (
    <FiscalYearContext.Provider value={{ fiscalYear, setFiscalYear, availableYears }}>
      {children}
    </FiscalYearContext.Provider>
  )
}

export function useFiscalYear() {
  const context = useContext(FiscalYearContext)
  if (context === undefined) {
    throw new Error('useFiscalYear must be used within a FiscalYearProvider')
  }
  return context
}
