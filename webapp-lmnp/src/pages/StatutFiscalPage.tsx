import { useState } from 'react'
import PageContainer from '../components/PageContainer'
import { Save } from 'lucide-react'

export default function StatutFiscalPage() {
  const [formData, setFormData] = useState({
    regimeFiscal: 'reel',
    optionTVA: false,
    numeroTVA: '',
    regimeSocial: 'independant',
    numeroSS: '',
    cfe: true,
    montantCfe: '',
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    console.log('Statut fiscal data:', formData)
  }

  return (
    <PageContainer title="Statut Fiscal et Social">
      <form onSubmit={handleSubmit} className="space-y-8">
        {/* Section Fiscale */}
        <div>
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
            Situation Fiscale
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Régime fiscal
              </label>
              <select
                value={formData.regimeFiscal}
                onChange={(e) => setFormData({ ...formData, regimeFiscal: e.target.value })}
                className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500"
              >
                <option value="micro">Micro-BIC</option>
                <option value="reel">Régime Réel Simplifié</option>
                <option value="reel-normal">Régime Réel Normal</option>
              </select>
            </div>

            <div className="flex items-center gap-3 pt-8">
              <input
                type="checkbox"
                id="optionTVA"
                checked={formData.optionTVA}
                onChange={(e) => setFormData({ ...formData, optionTVA: e.target.checked })}
                className="w-4 h-4 rounded text-primary-600"
              />
              <label htmlFor="optionTVA" className="text-sm text-gray-700 dark:text-gray-300">
                Assujetti à la TVA
              </label>
            </div>

            {formData.optionTVA && (
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Numéro de TVA intracommunautaire
                </label>
                <input
                  type="text"
                  value={formData.numeroTVA}
                  onChange={(e) => setFormData({ ...formData, numeroTVA: e.target.value })}
                  className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500"
                  placeholder="FR12345678901"
                />
              </div>
            )}
          </div>
        </div>

        {/* Section Sociale */}
        <div>
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
            Situation Sociale
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Régime social
              </label>
              <select
                value={formData.regimeSocial}
                onChange={(e) => setFormData({ ...formData, regimeSocial: e.target.value })}
                className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500"
              >
                <option value="independant">Travailleur Indépendant</option>
                <option value="salarie">Salarié (activité secondaire)</option>
                <option value="retraite">Retraité</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Numéro de Sécurité Sociale
              </label>
              <input
                type="text"
                value={formData.numeroSS}
                onChange={(e) => setFormData({ ...formData, numeroSS: e.target.value })}
                className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500"
                placeholder="1 23 45 67 890 123 45"
              />
            </div>
          </div>
        </div>

        {/* Section CFE */}
        <div>
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
            Cotisation Foncière des Entreprises (CFE)
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="flex items-center gap-3">
              <input
                type="checkbox"
                id="cfe"
                checked={formData.cfe}
                onChange={(e) => setFormData({ ...formData, cfe: e.target.checked })}
                className="w-4 h-4 rounded text-primary-600"
              />
              <label htmlFor="cfe" className="text-sm text-gray-700 dark:text-gray-300">
                Soumis à la CFE
              </label>
            </div>

            {formData.cfe && (
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Montant CFE annuel (€)
                </label>
                <input
                  type="number"
                  value={formData.montantCfe}
                  onChange={(e) => setFormData({ ...formData, montantCfe: e.target.value })}
                  className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500"
                  placeholder="500"
                />
              </div>
            )}
          </div>
        </div>

        {/* Informations complémentaires */}
        <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-4">
          <h3 className="text-sm font-medium text-yellow-900 dark:text-yellow-300 mb-2">
            Informations importantes
          </h3>
          <ul className="text-sm text-yellow-800 dark:text-yellow-400 space-y-1 list-disc list-inside">
            <li>Le régime réel permet de déduire l'ensemble des charges réelles</li>
            <li>Le régime micro-BIC applique un abattement forfaitaire de 50%</li>
            <li>L'adhésion à un OGA permet d'éviter une majoration de 25% du bénéfice imposable</li>
            <li>La CFE est due même en l'absence de chiffre d'affaires</li>
          </ul>
        </div>

        <div className="flex justify-end">
          <button
            type="submit"
            className="flex items-center gap-2 bg-primary-600 hover:bg-primary-700 text-white font-medium py-2 px-6 rounded-lg transition-colors"
          >
            <Save className="w-4 h-4" />
            Enregistrer
          </button>
        </div>
      </form>
    </PageContainer>
  )
}
