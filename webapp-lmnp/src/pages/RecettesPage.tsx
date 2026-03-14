import { useState } from 'react'
import PageContainer from '../components/PageContainer'
import { Save, Plus, Trash2 } from 'lucide-react'

interface Recette {
  id: string
  date: string
  description: string
  montant: string
  type: string
}

export default function RecettesPage() {
  const [recettes, setRecettes] = useState<Recette[]>([
    { id: '1', date: '2026-03-01', description: 'Loyer Mars - Apt 101', montant: '1200', type: 'loyer' },
    { id: '2', date: '2026-02-01', description: 'Loyer Février - Apt 101', montant: '1200', type: 'loyer' },
  ])

  const [showForm, setShowForm] = useState(false)
  const [newRecette, setNewRecette] = useState<Omit<Recette, 'id'>>({
    date: '',
    description: '',
    montant: '',
    type: 'loyer',
  })

  const handleAddRecette = () => {
    if (newRecette.date && newRecette.description && newRecette.montant) {
      setRecettes([
        {
          ...newRecette,
          id: Date.now().toString(),
        },
        ...recettes,
      ])
      setNewRecette({ date: '', description: '', montant: '', type: 'loyer' })
      setShowForm(false)
    }
  }

  const totalRecettes = recettes.reduce((sum, r) => sum + parseFloat(r.montant || '0'), 0)

  return (
    <PageContainer title="Recettes">
      <div className="flex justify-between items-center mb-6">
        <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-4">
          <p className="text-sm text-green-700 dark:text-green-400 mb-1">Total des recettes</p>
          <p className="text-2xl font-bold text-green-900 dark:text-green-300">
            {totalRecettes.toLocaleString('fr-FR')} €
          </p>
        </div>

        <button
          onClick={() => setShowForm(!showForm)}
          className="flex items-center gap-2 bg-primary-600 hover:bg-primary-700 text-white font-medium py-2 px-4 rounded-lg transition-colors"
        >
          <Plus className="w-4 h-4" />
          Ajouter une recette
        </button>
      </div>

      {showForm && (
        <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-6 mb-6">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Nouvelle Recette
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Date
              </label>
              <input
                type="date"
                value={newRecette.date}
                onChange={(e) => setNewRecette({ ...newRecette, date: e.target.value })}
                className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Type
              </label>
              <select
                value={newRecette.type}
                onChange={(e) => setNewRecette({ ...newRecette, type: e.target.value })}
                className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500"
              >
                <option value="loyer">Loyer</option>
                <option value="charges">Charges</option>
                <option value="caution">Caution</option>
                <option value="autre">Autre</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Description
              </label>
              <input
                type="text"
                value={newRecette.description}
                onChange={(e) => setNewRecette({ ...newRecette, description: e.target.value })}
                className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500"
                placeholder="Ex: Loyer Mars - Appartement 101"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Montant (€)
              </label>
              <input
                type="number"
                value={newRecette.montant}
                onChange={(e) => setNewRecette({ ...newRecette, montant: e.target.value })}
                className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500"
                placeholder="1200"
              />
            </div>
          </div>

          <div className="flex gap-2">
            <button
              onClick={handleAddRecette}
              className="flex items-center gap-2 bg-primary-600 hover:bg-primary-700 text-white font-medium py-2 px-4 rounded-lg transition-colors"
            >
              <Save className="w-4 h-4" />
              Enregistrer
            </button>
            <button
              onClick={() => setShowForm(false)}
              className="bg-gray-300 dark:bg-gray-600 hover:bg-gray-400 dark:hover:bg-gray-500 text-gray-900 dark:text-white font-medium py-2 px-4 rounded-lg transition-colors"
            >
              Annuler
            </button>
          </div>
        </div>
      )}

      <div className="bg-white dark:bg-gray-700 rounded-lg overflow-hidden border border-gray-200 dark:border-gray-600">
        <table className="w-full">
          <thead className="bg-gray-50 dark:bg-gray-800">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                Date
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                Type
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                Description
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                Montant
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200 dark:divide-gray-600">
            {recettes.map((recette) => (
              <tr key={recette.id} className="hover:bg-gray-50 dark:hover:bg-gray-600">
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                  {new Date(recette.date).toLocaleDateString('fr-FR')}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200">
                    {recette.type}
                  </span>
                </td>
                <td className="px-6 py-4 text-sm text-gray-900 dark:text-white">
                  {recette.description}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-semibold text-green-600 dark:text-green-400">
                  {parseFloat(recette.montant).toLocaleString('fr-FR')} €
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm">
                  <button
                    onClick={() => setRecettes(recettes.filter((r) => r.id !== recette.id))}
                    className="text-red-600 hover:text-red-700 dark:text-red-400"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </PageContainer>
  )
}
