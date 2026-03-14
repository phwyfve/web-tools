import { useState } from 'react'
import PageContainer from '../components/PageContainer'
import { Save } from 'lucide-react'

export default function UsagePage() {
  const [formData, setFormData] = useState({
    logementId: '',
    typeUsage: 'location',
    dateDebut: '',
    dateFin: '',
    tauxOccupation: '',
    loyerMensuel: '',
    chargesIncluses: false,
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    console.log('Usage data:', formData)
  }

  return (
    <PageContainer title="Usage du Logement">
      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Logement concerné
            </label>
            <select
              value={formData.logementId}
              onChange={(e) => setFormData({ ...formData, logementId: e.target.value })}
              className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500"
            >
              <option value="">Sélectionner un logement...</option>
              <option value="1">Appartement 101</option>
              <option value="2">Maison 202</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Type d'usage
            </label>
            <select
              value={formData.typeUsage}
              onChange={(e) => setFormData({ ...formData, typeUsage: e.target.value })}
              className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500"
            >
              <option value="location">Location meublée</option>
              <option value="saisonniere">Location saisonnière</option>
              <option value="courte-duree">Location courte durée</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Date de début
            </label>
            <input
              type="date"
              value={formData.dateDebut}
              onChange={(e) => setFormData({ ...formData, dateDebut: e.target.value })}
              className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Date de fin (optionnelle)
            </label>
            <input
              type="date"
              value={formData.dateFin}
              onChange={(e) => setFormData({ ...formData, dateFin: e.target.value })}
              className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Taux d'occupation (%)
            </label>
            <input
              type="number"
              value={formData.tauxOccupation}
              onChange={(e) => setFormData({ ...formData, tauxOccupation: e.target.value })}
              className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500"
              placeholder="85"
              min="0"
              max="100"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Loyer mensuel (€)
            </label>
            <input
              type="number"
              value={formData.loyerMensuel}
              onChange={(e) => setFormData({ ...formData, loyerMensuel: e.target.value })}
              className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500"
              placeholder="1200"
            />
          </div>
        </div>

        <div className="flex items-center gap-3">
          <input
            type="checkbox"
            id="chargesIncluses"
            checked={formData.chargesIncluses}
            onChange={(e) => setFormData({ ...formData, chargesIncluses: e.target.checked })}
            className="w-4 h-4 rounded text-primary-600"
          />
          <label htmlFor="chargesIncluses" className="text-sm text-gray-700 dark:text-gray-300">
            Charges incluses dans le loyer
          </label>
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
