import { useState, useEffect } from 'react'
import PageContainer from '../components/PageContainer'
import { Save, Loader2 } from 'lucide-react'
import { lmnpApi, StatutFiscalData } from '../services/lmnpApi'
import { useFiscalYear } from '../contexts/FiscalYearContext'

export default function StatutFiscalPage() {
  const { fiscalYear } = useFiscalYear()
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [formData, setFormData] = useState<Partial<StatutFiscalData>>({
    regime_fiscal: '',
    assujetti_tva: false,
    soumis_cfe: true,
    option_amortissement: false,
    duree_amortissement: undefined,
    adherent_cga: false,
    numero_cga: '',
  })

  useEffect(() => {
    loadData()
  }, [fiscalYear])

  const loadData = async () => {
    try {
      setLoading(true)
      const data = await lmnpApi.getData(fiscalYear)
      
      if (data.statut_fiscal) {
        setFormData({
          regime_fiscal: data.statut_fiscal.regime_fiscal || '',
          assujetti_tva: data.statut_fiscal.assujetti_tva || false,
          soumis_cfe: data.statut_fiscal.soumis_cfe !== undefined ? data.statut_fiscal.soumis_cfe : true,
          option_amortissement: data.statut_fiscal.option_amortissement || false,
          duree_amortissement: data.statut_fiscal.duree_amortissement,
          adherent_cga: data.statut_fiscal.adherent_cga || false,
          numero_cga: data.statut_fiscal.numero_cga || '',
        })
      }
    } catch (error) {
      console.error('Erreur lors du chargement des données:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleRegimeFiscalChange = (regime: string) => {
    // Règles métier :
    // - assujetti_tva = true seulement si regime === 'reel_normal'
    // - soumis_cfe = false seulement si regime === 'micro_bic'
    const assujetti_tva = regime === 'reel_normal'
    const soumis_cfe = regime !== 'micro_bic'
    
    setFormData({
      ...formData,
      regime_fiscal: regime,
      assujetti_tva,
      soumis_cfe,
    })
  }

  const handleSave = async () => {
    try {
      setSaving(true)
      await lmnpApi.updateStatutFiscal(fiscalYear, {
        regime_fiscal: formData.regime_fiscal || undefined,
        assujetti_tva: formData.assujetti_tva,
        soumis_cfe: formData.soumis_cfe,
        option_amortissement: formData.option_amortissement,
        duree_amortissement: formData.duree_amortissement || undefined,
        adherent_cga: formData.adherent_cga,
        numero_cga: formData.numero_cga || undefined,
      })
      console.log('Statut fiscal sauvegardé')
    } catch (error) {
      console.error('Erreur lors de la sauvegarde:', error)
    } finally {
      setSaving(false)
    }
  }

  if (loading) {
    return (
      <PageContainer title="Statut Fiscal et Social">
        <div className="flex items-center justify-center py-12">
          <Loader2 className="w-8 h-8 animate-spin text-primary-600" />
        </div>
      </PageContainer>
    )
  }

  return (
    <PageContainer title="Statut Fiscal et Social">
      <div className="space-y-8">
        {/* Section Régime Fiscal */}
        <div className="bg-white dark:bg-gray-700 rounded-lg p-6 border border-gray-200 dark:border-gray-600">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
            Régime Fiscal
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Régime fiscal *
              </label>
              <select
                value={formData.regime_fiscal || ''}
                onChange={(e) => handleRegimeFiscalChange(e.target.value)}
                className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500"
                required
              >
                <option value="">Sélectionner un régime...</option>
                <option value="micro_bic">Micro-BIC</option>
                <option value="reel_simplifie">Régime Réel Simplifié</option>
                <option value="reel_normal">Régime Réel Normal</option>
              </select>
            </div>

            <div className="flex items-center gap-3">
              <input
                type="checkbox"
                id="assujetti_tva"
                checked={formData.assujetti_tva || false}
                disabled
                className="w-4 h-4 rounded text-primary-600 disabled:opacity-50 disabled:cursor-not-allowed"
              />
              <label htmlFor="assujetti_tva" className="text-sm text-gray-700 dark:text-gray-300">
                Assujetti à la TVA
                <span className="ml-2 text-xs text-gray-500 dark:text-gray-400">
                  (automatique si Régime Réel Normal)
                </span>
              </label>
            </div>

            <div className="flex items-center gap-3">
              <input
                type="checkbox"
                id="soumis_cfe"
                checked={formData.soumis_cfe !== false}
                disabled
                className="w-4 h-4 rounded text-primary-600 disabled:opacity-50 disabled:cursor-not-allowed"
              />
              <label htmlFor="soumis_cfe" className="text-sm text-gray-700 dark:text-gray-300">
                Soumis à la CFE
                <span className="ml-2 text-xs text-gray-500 dark:text-gray-400">
                  (non soumis si Micro-BIC)
                </span>
              </label>
            </div>
          </div>
        </div>

        {/* Section Amortissement */}
        <div className="bg-white dark:bg-gray-700 rounded-lg p-6 border border-gray-200 dark:border-gray-600">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
            Option Amortissement
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="flex items-center gap-3">
              <input
                type="checkbox"
                id="option_amortissement"
                checked={formData.option_amortissement || false}
                onChange={(e) => setFormData({ ...formData, option_amortissement: e.target.checked })}
                className="w-4 h-4 rounded text-primary-600"
              />
              <label htmlFor="option_amortissement" className="text-sm text-gray-700 dark:text-gray-300">
                Option pour l'amortissement des biens
              </label>
            </div>

            {formData.option_amortissement && (
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Durée d'amortissement (années)
                </label>
                <input
                  type="number"
                  value={formData.duree_amortissement || ''}
                  onChange={(e) => setFormData({ ...formData, duree_amortissement: e.target.value ? parseInt(e.target.value) : undefined })}
                  className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500"
                  placeholder="20"
                  min="1"
                />
              </div>
            )}
          </div>
        </div>

        {/* Section CGA/OGA */}
        <div className="bg-white dark:bg-gray-700 rounded-lg p-6 border border-gray-200 dark:border-gray-600">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
            Centre de Gestion Agréé (CGA/OGA)
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="flex items-center gap-3">
              <input
                type="checkbox"
                id="adherent_cga"
                checked={formData.adherent_cga || false}
                onChange={(e) => setFormData({ ...formData, adherent_cga: e.target.checked })}
                className="w-4 h-4 rounded text-primary-600"
              />
              <label htmlFor="adherent_cga" className="text-sm text-gray-700 dark:text-gray-300">
                Adhérent à un CGA/OGA
              </label>
            </div>

            {formData.adherent_cga && (
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Numéro d'adhésion CGA
                </label>
                <input
                  type="text"
                  value={formData.numero_cga || ''}
                  onChange={(e) => setFormData({ ...formData, numero_cga: e.target.value })}
                  className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500"
                  placeholder="123456789"
                />
              </div>
            )}
          </div>
        </div>

        {/* Information */}
        <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
          <h3 className="text-sm font-medium text-blue-900 dark:text-blue-300 mb-2">
            Informations
          </h3>
          <ul className="text-sm text-blue-800 dark:text-blue-400 space-y-1 list-disc list-inside">
            <li>L'assujettissement à la TVA est automatique en Régime Réel Normal</li>
            <li>Le Micro-BIC n'est pas soumis à la CFE (Cotisation Foncière des Entreprises)</li>
            <li>L'option amortissement permet de déduire l'usure des biens sur plusieurs années</li>
            <li>L'adhésion à un CGA/OGA permet de bénéficier d'avantages fiscaux</li>
          </ul>
        </div>

        {/* Bouton Sauvegarder */}
        <div className="flex justify-end">
          <button
            onClick={handleSave}
            disabled={saving}
            className="flex items-center gap-2 bg-primary-600 hover:bg-primary-700 disabled:bg-gray-400 text-white font-medium py-2 px-6 rounded-lg transition-colors"
          >
            {saving ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                Enregistrement...
              </>
            ) : (
              <>
                <Save className="w-4 h-4" />
                Enregistrer
              </>
            )}
          </button>
        </div>
      </div>
    </PageContainer>
  )
}
