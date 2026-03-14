/**
 * LMNP API Service
 * Service pour gérer les données LMNP (Location Meublée Non Professionnelle)
 */

import { api } from './api'

// ============================================================================
// TypeScript Types
// ============================================================================

export interface SirenData {
  numero?: string
  denomination?: string
  prenom?: string
  nom?: string
  pays_residence?: string
  adresse?: string
  code_postal?: string
  ville?: string
  date_creation?: string
  updated_at?: string
}

export interface LogementData {
  id: string
  nom: string
  adresse: string
  code_postal?: string
  ville?: string
  surface?: number
  nb_pieces?: number
  date_acquisition?: string
  prix_acquisition?: number
  updated_at?: string
}

export interface UsageData {
  type_usage?: string // 'location' | 'location_courte_duree' | 'mixte'
  date_debut?: string
  date_fin?: string
  nb_jours_location?: number
  nb_jours_perso?: number
  est_residence_principale?: boolean
  updated_at?: string
}

export interface RecetteData {
  id: string
  date: string
  montant: number
  description?: string
  type_recette?: string // 'loyer' | 'charges' | 'autre'
  logement_id?: string
  updated_at?: string
}

export interface DepenseData {
  id: string
  date: string
  montant: number
  description?: string
  categorie?: string // 'travaux' | 'entretien' | 'charges' | 'assurance'
  logement_id?: string
  est_amortissable?: boolean
  updated_at?: string
}

export interface EmpruntData {
  id: string
  organisme: string
  montant_initial: number
  taux: number
  date_debut: string
  duree_mois: number
  mensualite?: number
  logement_id?: string
  updated_at?: string
}

export interface OgaData {
  nom?: string
  numero_adhesion?: string
  date_adhesion?: string
  montant_cotisation?: number
  updated_at?: string
}

export interface StatutFiscalData {
  regime_fiscal?: string // 'reel' | 'micro_bic'
  option_amortissement?: boolean
  duree_amortissement?: number
  adherent_cga?: boolean
  numero_cga?: string
  updated_at?: string
}

export interface LmnpUserData {
  _id?: string
  user_id: string
  fiscal_year: number
  siren?: SirenData | null
  logements?: LogementData[]
  usage?: UsageData | null
  recettes?: RecetteData[]
  depenses?: DepenseData[]
  emprunts?: EmpruntData[]
  oga?: OgaData | null
  statut_fiscal?: StatutFiscalData | null
  created_at?: string
  updated_at?: string
  is_complete?: boolean
  version?: number
}

export interface LmnpApiResponse<T = any> {
  success: boolean
  message?: string
  data?: T
  error?: string
}

// ============================================================================
// LMNP API Functions
// ============================================================================

export const lmnpApi = {
  /**
   * Récupère toutes les données LMNP pour une année fiscale
   */
  getData: async (fiscalYear: number): Promise<LmnpUserData> => {
    const response = await api.get<LmnpApiResponse<LmnpUserData>>(
      `/api/lmnp/data/${fiscalYear}`
    )
    return response.data.data!
  },

  /**
   * Met à jour les données SIREN
   */
  updateSiren: async (
    fiscalYear: number,
    data: Partial<SirenData>
  ): Promise<LmnpUserData> => {
    const response = await api.patch<LmnpApiResponse<LmnpUserData>>(
      `/api/lmnp/data/${fiscalYear}/siren`,
      data
    )
    return response.data.data!
  },

  /**
   * Met à jour la liste des logements
   */
  updateLogements: async (
    fiscalYear: number,
    logements: LogementData[]
  ): Promise<LmnpUserData> => {
    const response = await api.patch<LmnpApiResponse<LmnpUserData>>(
      `/api/lmnp/data/${fiscalYear}/logements`,
      { logements }
    )
    return response.data.data!
  },

  /**
   * Met à jour les données d'usage
   */
  updateUsage: async (
    fiscalYear: number,
    data: Partial<UsageData>
  ): Promise<LmnpUserData> => {
    const response = await api.patch<LmnpApiResponse<LmnpUserData>>(
      `/api/lmnp/data/${fiscalYear}/usage`,
      data
    )
    return response.data.data!
  },

  /**
   * Met à jour la liste des recettes
   */
  updateRecettes: async (
    fiscalYear: number,
    recettes: RecetteData[]
  ): Promise<LmnpUserData> => {
    const response = await api.patch<LmnpApiResponse<LmnpUserData>>(
      `/api/lmnp/data/${fiscalYear}/recettes`,
      { recettes }
    )
    return response.data.data!
  },

  /**
   * Met à jour la liste des dépenses
   */
  updateDepenses: async (
    fiscalYear: number,
    depenses: DepenseData[]
  ): Promise<LmnpUserData> => {
    const response = await api.patch<LmnpApiResponse<LmnpUserData>>(
      `/api/lmnp/data/${fiscalYear}/depenses`,
      { depenses }
    )
    return response.data.data!
  },

  /**
   * Met à jour la liste des emprunts
   */
  updateEmprunts: async (
    fiscalYear: number,
    emprunts: EmpruntData[]
  ): Promise<LmnpUserData> => {
    const response = await api.patch<LmnpApiResponse<LmnpUserData>>(
      `/api/lmnp/data/${fiscalYear}/emprunts`,
      { emprunts }
    )
    return response.data.data!
  },

  /**
   * Met à jour les données OGA
   */
  updateOga: async (
    fiscalYear: number,
    data: Partial<OgaData>
  ): Promise<LmnpUserData> => {
    const response = await api.patch<LmnpApiResponse<LmnpUserData>>(
      `/api/lmnp/data/${fiscalYear}/oga`,
      data
    )
    return response.data.data!
  },

  /**
   * Met à jour le statut fiscal
   */
  updateStatutFiscal: async (
    fiscalYear: number,
    data: Partial<StatutFiscalData>
  ): Promise<LmnpUserData> => {
    const response = await api.patch<LmnpApiResponse<LmnpUserData>>(
      `/api/lmnp/data/${fiscalYear}/statut-fiscal`,
      data
    )
    return response.data.data!
  },

  /**
   * Exporte toutes les données pour génération de la liasse fiscale
   */
  exportData: async (fiscalYear: number): Promise<any> => {
    const response = await api.get<LmnpApiResponse<LmnpUserData>>(
      `/api/lmnp/export/${fiscalYear}`
    )
    return response.data
  },

  /**
   * Supprime les données d'une année fiscale
   */
  deleteData: async (fiscalYear: number): Promise<void> => {
    await api.delete(`/api/lmnp/data/${fiscalYear}`)
  },

  /**
   * Liste toutes les années fiscales disponibles
   */
  listYears: async (): Promise<number[]> => {
    const response = await api.get<LmnpApiResponse<{ years: number[] }>>(
      '/api/lmnp/years'
    )
    return response.data.data?.years || []
  },
}
