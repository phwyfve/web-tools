import { useState } from 'react'
import PageContainer from '../components/PageContainer'
import { Save, Plus, Trash2 } from 'lucide-react'

interface Emprunt {
  id: string
  banque: string
  montantInitial: string
  tauxInteret: string
  duree: string
  dateDebut: string
  mensualite: string
}

export default function EmpruntsPage() {
  const [emprunts, setEmprunts] = useState<Emprunt[]>([
    {
      id: '1',
      banque: 'Crédit Agricole',
      montantInitial: '200000',
      tauxInteret: '1.5',
      duree: '20',
      dateDebut: '2023-01-15',
      mensualite: '965',
    },
  ])

  const [showForm, setShowForm] = useState(false)
  const [newEmprunt, setNewEmprunt] = useState<Omit<Emprunt, 'id'>>({
    banque: '',
    montantInitial: '',
    tauxInteret: '',
    duree: '',
    dateDebut: '',
    mensualite: '',
  })

  const handleAddEmprunt = () => {
    if (newEmprunt.banque && newEmprunt.montantInitial) {
      setEmprunts([
        ...emprunts,
        {
          ...newEmprunt,
          id: Date.now().toString(),
        },
      ])
      setNewEmprunt({
        banque: '',
        montantInitial: '',
        tauxInteret: '',
        duree: '',
        dateDebut: '',
        mensualite: '',
      })
      setShowForm(false)
    }
  }

  return (
    <PageContainer title="Emprunts">
      <div className="mb-6">
        <button
          onClick={() => setShowForm(!showForm)}
          className="flex items-center gap-2 bg-primary-600 hover:bg-primary-700 text-white font-medium py-2 px-4 rounded-lg transition-colors"
        >
          <Plus className="w-4 h-4" />
          Ajouter un emprunt
        </button>
      </div>

      {showForm && (
        <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-6 mb-6">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Nouvel Emprunt
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Banque
              </label>
              <input
                type="text"
                value={newEmprunt.banque}
                onChange={(e) => setNewEmprunt({ ...newEmprunt, banque: e.target.value })}
                className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500"
                placeholder="Ex: Crédit Agricole"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Montant initial (€)
              </label>
              <input
                type="number"
                value={newEmprunt.montantInitial}
                onChange={(e) => setNewEmprunt({ ...newEmprunt, montantInitial: e.target.value })}
                className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500"
                placeholder="200000"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Taux d'intérêt (%)
              </label>
              <input
                type="number"
                step="0.1"
                value={newEmprunt.tauxInteret}
                onChange={(e) => setNewEmprunt({ ...newEmprunt, tauxInteret: e.target.value })}
                className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500"
                placeholder="1.5"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Durée (années)
              </label>
              <input
                type="number"
                value={newEmprunt.duree}
                onChange={(e) => setNewEmprunt({ ...newEmprunt, duree: e.target.value })}
                className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500"
                placeholder="20"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Date de début
              </label>
              <input
                type="date"
                value={newEmprunt.dateDebut}
                onChange={(e) => setNewEmprunt({ ...newEmprunt, dateDebut: e.target.value })}
                className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Mensualité (€)
              </label>
              <input
                type="number"
                value={newEmprunt.mensualite}
                onChange={(e) => setNewEmprunt({ ...newEmprunt, mensualite: e.target.value })}
                className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500"
                placeholder="965"
              />
            </div>
          </div>

          <div className="flex gap-2">
            <button
              onClick={handleAddEmprunt}
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

      <div className="space-y-4">
        {emprunts.map((emprunt) => (
          <div
            key={emprunt.id}
            className="bg-white dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-lg p-6"
          >
            <div className="flex justify-between items-start mb-4">
              <div>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-1">
                  {emprunt.banque}
                </h3>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Depuis le {new Date(emprunt.dateDebut).toLocaleDateString('fr-FR')}
                </p>
              </div>
              <button
                onClick={() => setEmprunts(emprunts.filter((e) => e.id !== emprunt.id))}
                className="text-red-600 hover:text-red-700 dark:text-red-400"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div>
                <p className="text-xs text-gray-600 dark:text-gray-400 mb-1">Montant initial</p>
                <p className="text-lg font-semibold text-gray-900 dark:text-white">
                  {parseFloat(emprunt.montantInitial).toLocaleString('fr-FR')} €
                </p>
              </div>
              <div>
                <p className="text-xs text-gray-600 dark:text-gray-400 mb-1">Taux</p>
                <p className="text-lg font-semibold text-gray-900 dark:text-white">
                  {emprunt.tauxInteret} %
                </p>
              </div>
              <div>
                <p className="text-xs text-gray-600 dark:text-gray-400 mb-1">Durée</p>
                <p className="text-lg font-semibold text-gray-900 dark:text-white">
                  {emprunt.duree} ans
                </p>
              </div>
              <div>
                <p className="text-xs text-gray-600 dark:text-gray-400 mb-1">Mensualité</p>
                <p className="text-lg font-semibold text-primary-600 dark:text-primary-400">
                  {parseFloat(emprunt.mensualite).toLocaleString('fr-FR')} €
                </p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </PageContainer>
  )
}
