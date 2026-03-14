import { useState } from 'react'
import PageContainer from '../components/PageContainer'
import { Save } from 'lucide-react'

export default function OgaPage() {
  const [formData, setFormData] = useState({
    adhesion: false,
    nomOga: '',
    numeroAdhesion: '',
    dateAdhesion: '',
    cotisationAnnuelle: '',
    typeService: 'complet',
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    console.log('OGA data:', formData)
  }

  return (
    <PageContainer title="Organisme de Gestion Agréé (OGA)">
      <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4 mb-6">
        <h3 className="text-sm font-medium text-blue-900 dark:text-blue-300 mb-2">
          À propos de l'OGA
        </h3>
        <p className="text-sm text-blue-800 dark:text-blue-400">
          L'adhésion à un Organisme de Gestion Agréé (OGA) permet de bénéficier d'avantages fiscaux
          et d'un accompagnement dans la gestion de votre activité LMNP.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="flex items-center gap-3">
          <input
            type="checkbox"
            id="adhesion"
            checked={formData.adhesion}
            onChange={(e) => setFormData({ ...formData, adhesion: e.target.checked })}
            className="w-4 h-4 rounded text-primary-600"
          />
          <label htmlFor="adhesion" className="text-sm font-medium text-gray-700 dark:text-gray-300">
            Je suis adhérent à un OGA
          </label>
        </div>

        {formData.adhesion && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 p-6 bg-gray-50 dark:bg-gray-700 rounded-lg">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Nom de l'OGA
              </label>
              <input
                type="text"
                value={formData.nomOga}
                onChange={(e) => setFormData({ ...formData, nomOga: e.target.value })}
                className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500"
                placeholder="Ex: AGA BTP"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Numéro d'adhésion
              </label>
              <input
                type="text"
                value={formData.numeroAdhesion}
                onChange={(e) => setFormData({ ...formData, numeroAdhesion: e.target.value })}
                className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500"
                placeholder="ABC123456"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Date d'adhésion
              </label>
              <input
                type="date"
                value={formData.dateAdhesion}
                onChange={(e) => setFormData({ ...formData, dateAdhesion: e.target.value })}
                className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Cotisation annuelle (€)
              </label>
              <input
                type="number"
                value={formData.cotisationAnnuelle}
                onChange={(e) => setFormData({ ...formData, cotisationAnnuelle: e.target.value })}
                className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500"
                placeholder="300"
              />
            </div>

            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Type de service
              </label>
              <select
                value={formData.typeService}
                onChange={(e) => setFormData({ ...formData, typeService: e.target.value })}
                className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500"
              >
                <option value="complet">Service complet (avec tenue de comptabilité)</option>
                <option value="partiel">Service partiel (conseil uniquement)</option>
                <option value="distance">Service à distance</option>
              </select>
            </div>
          </div>
        )}

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
