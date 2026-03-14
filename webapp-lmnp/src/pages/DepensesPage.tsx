import { useState } from 'react'
import PageContainer from '../components/PageContainer'
import { Save, Plus, Trash2 } from 'lucide-react'

interface Depense {
  id: string
  date: string
  description: string
  montant: string
  categorie: string
}

export default function DepensesPage() {
  const [depenses, setDepenses] = useState<Depense[]>([
    { id: '1', date: '2026-03-05', description: 'Réparation chauffage', montant: '350', categorie: 'reparation' },
    { id: '2', date: '2026-02-15', description: 'Taxe foncière', montant: '1200', categorie: 'taxe' },
  ])

  const [showForm, setShowForm] = useState(false)
  const [newDepense, setNewDepense] = useState<Omit<Depense, 'id'>>({
    date: '',
    description: '',
    montant: '',
    categorie: 'reparation',
  })

  const handleAddDepense = () => {
    if (newDepense.date && newDepense.description && newDepense.montant) {
      setDepenses([
        {
          ...newDepense,
          id: Date.now().toString(),
        },
        ...depenses,
      ])
      setNewDepense({ date: '', description: '', montant: '', categorie: 'reparation' })
      setShowForm(false)
    }
  }

  const totalDepenses = depenses.reduce((sum, d) => sum + parseFloat(d.montant || '0'), 0)

  return (
    <PageContainer title="Dépenses">
      <div className="flex justify-between items-center mb-6">
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
          <p className="text-sm text-red-700 dark:text-red-400 mb-1">Total des dépenses</p>
          <p className="text-2xl font-bold text-red-900 dark:text-red-300">
            {totalDepenses.toLocaleString('fr-FR')} €
          </p>
        </div>

        <button
          onClick={() => setShowForm(!showForm)}
          className="flex items-center gap-2 bg-primary-600 hover:bg-primary-700 text-white font-medium py-2 px-4 rounded-lg transition-colors"
        >
          <Plus className="w-4 h-4" />
          Ajouter une dépense
        </button>
      </div>

      {showForm && (
        <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-6 mb-6">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Nouvelle Dépense
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Date
              </label>
              <input
                type="date"
                value={newDepense.date}
                onChange={(e) => setNewDepense({ ...newDepense, date: e.target.value })}
                className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Catégorie
              </label>
              <select
                value={newDepense.categorie}
                onChange={(e) => setNewDepense({ ...newDepense, categorie: e.target.value })}
                className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500"
              >
                <option value="reparation">Réparation</option>
                <option value="entretien">Entretien</option>
                <option value="taxe">Taxe</option>
                <option value="assurance">Assurance</option>
                <option value="charges">Charges</option>
                <option value="travaux">Travaux</option>
                <option value="autre">Autre</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Description
              </label>
              <input
                type="text"
                value={newDepense.description}
                onChange={(e) => setNewDepense({ ...newDepense, description: e.target.value })}
                className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500"
                placeholder="Ex: Réparation chauffage"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Montant (€)
              </label>
              <input
                type="number"
                value={newDepense.montant}
                onChange={(e) => setNewDepense({ ...newDepense, montant: e.target.value })}
                className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500"
                placeholder="350"
              />
            </div>
          </div>

          <div className="flex gap-2">
            <button
              onClick={handleAddDepense}
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
                Catégorie
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
            {depenses.map((depense) => (
              <tr key={depense.id} className="hover:bg-gray-50 dark:hover:bg-gray-600">
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                  {new Date(depense.date).toLocaleDateString('fr-FR')}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-orange-100 dark:bg-orange-900 text-orange-800 dark:text-orange-200">
                    {depense.categorie}
                  </span>
                </td>
                <td className="px-6 py-4 text-sm text-gray-900 dark:text-white">
                  {depense.description}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-semibold text-red-600 dark:text-red-400">
                  {parseFloat(depense.montant).toLocaleString('fr-FR')} €
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm">
                  <button
                    onClick={() => setDepenses(depenses.filter((d) => d.id !== depense.id))}
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
