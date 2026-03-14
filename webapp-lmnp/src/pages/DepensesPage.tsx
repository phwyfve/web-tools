import { useState, useEffect } from 'react'
import PageContainer from '../components/PageContainer'
import { Save, Plus, Trash2, Loader2, Pencil } from 'lucide-react'
import { lmnpApi, DepenseData, LogementData } from '../services/lmnpApi'

const CATEGORIES = [
  { group: 'Taxes', items: [
    { value: 'taxe_fonciere', label: 'Taxe foncière' },
    { value: 'taxe_habitation', label: 'Taxe d\'habitation' },
  ]},
  { group: 'Assurance', items: [
    { value: 'assurance_pno', label: 'Assurances propriétaire non occupant (PNO)' },
    { value: 'assurance_gli', label: 'Assurance Loyer Impayé (GLI)' },
  ]},
  { group: 'Comptabilité', items: [
    { value: 'cotisation_oga', label: 'Cotisation Organisme de Gestion Agréé (OGA)' },
    { value: 'frais_logiciel', label: 'Frais Logiciel de Gestion' },
  ]},
  { group: 'Energie', items: [
    { value: 'abonnement_eau', label: 'Abonnement eau' },
    { value: 'abonnement_electricite', label: 'Abonnement électricité' },
    { value: 'abonnement_gaz', label: 'Abonnement gaz' },
  ]},
  { group: 'Tech', items: [
    { value: 'abonnement_tv_streaming', label: 'Abonnements TV & Streaming' },
    { value: 'abonnement_internet', label: 'Abonnement Internet' },
  ]},
  { group: 'Co Propriété', items: [
    { value: 'depenses_copropriete', label: 'Dépenses de co-propriété' },
  ]},
  { group: 'Electroménager', items: [
    { value: 'gros_ameublement', label: 'Gros ameublements et électroménagers (> 500 € TTC)' },
    { value: 'petit_ameublement', label: 'Petits ameublements et électroménagers (< 500 € TTC)' },
  ]},
]

export default function DepensesPage() {
  const currentYear = new Date().getFullYear()
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [logements, setLogements] = useState<LogementData[]>([])
  const [depenses, setDepenses] = useState<DepenseData[]>([])
  const [showForm, setShowForm] = useState(false)
  const [editingDepense, setEditingDepense] = useState<DepenseData | null>(null)
  const [formData, setFormData] = useState<Partial<DepenseData>>({
    logement_id: '',
    date: '',
    montant: undefined,
    description: '',
    categorie: '',
  })

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      setLoading(true)
      const data = await lmnpApi.getData(currentYear)
      
      if (data.logements) {
        setLogements(data.logements)
      }
      
      if (data.depenses) {
        setDepenses(data.depenses)
      }
    } catch (error) {
      console.error('Erreur lors du chargement des données:', error)
    } finally {
      setLoading(false)
    }
  }

  const saveDepenses = async (updatedDepenses: DepenseData[]) => {
    try {
      setSaving(true)
      await lmnpApi.updateDepenses(currentYear, updatedDepenses)
      setDepenses(updatedDepenses)
    } catch (error) {
      console.error('Erreur lors de la sauvegarde:', error)
    } finally {
      setSaving(false)
    }
  }

  const handleAddDepense = () => {
    if (formData.logement_id && formData.date && formData.montant && formData.categorie) {
      const depenseToAdd: DepenseData = {
        id: `depense-${Date.now()}`,
        logement_id: formData.logement_id,
        date: formData.date,
        montant: formData.montant,
        description: formData.description || undefined,
        categorie: formData.categorie,
      }
      
      const updatedDepenses = [...depenses, depenseToAdd]
      saveDepenses(updatedDepenses)
      
      setFormData({
        logement_id: '',
        date: '',
        montant: undefined,
        description: '',
        categorie: '',
      })
      setShowForm(false)
    }
  }

  const handleEditDepense = (depense: DepenseData) => {
    setEditingDepense(depense)
    setFormData({
      logement_id: depense.logement_id,
      date: depense.date,
      montant: depense.montant,
      description: depense.description,
      categorie: depense.categorie,
    })
    setShowForm(true)
  }

  const handleUpdateDepense = () => {
    if (editingDepense && formData.logement_id && formData.date && formData.montant && formData.categorie) {
      const updatedDepense: DepenseData = {
        ...editingDepense,
        logement_id: formData.logement_id,
        date: formData.date,
        montant: formData.montant,
        description: formData.description || undefined,
        categorie: formData.categorie,
      }
      
      const updatedDepenses = depenses.map(d => 
        d.id === editingDepense.id ? updatedDepense : d
      )
      saveDepenses(updatedDepenses)
      
      setFormData({
        logement_id: '',
        date: '',
        montant: undefined,
        description: '',
        categorie: '',
      })
      setEditingDepense(null)
      setShowForm(false)
    }
  }

  const handleCancelEdit = () => {
    setFormData({
      logement_id: '',
      date: '',
      montant: undefined,
      description: '',
      categorie: '',
    })
    setEditingDepense(null)
    setShowForm(false)
  }

  const handleDeleteDepense = (id: string) => {
    const updatedDepenses = depenses.filter((d) => d.id !== id)
    saveDepenses(updatedDepenses)
  }

  const getLogementNom = (logementId?: string): string => {
    if (!logementId) return 'Non spécifié'
    const logement = logements.find(l => l.id === logementId)
    return logement ? logement.nom : 'Inconnu'
  }

  const getCategorieLabel = (categorieValue?: string): string => {
    if (!categorieValue) return 'Non spécifié'
    for (const group of CATEGORIES) {
      const item = group.items.find(i => i.value === categorieValue)
      if (item) return item.label
    }
    return categorieValue
  }

  const totalDepenses = depenses.reduce((sum, d) => sum + (d.montant || 0), 0)

  if (loading) {
    return (
      <PageContainer title="Dépenses">
        <div className="flex items-center justify-center py-12">
          <Loader2 className="w-8 h-8 animate-spin text-primary-600" />
        </div>
      </PageContainer>
    )
  }

  return (
    <PageContainer title="Dépenses">
      <div className="flex justify-between items-center mb-6">
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
          <p className="text-sm text-red-700 dark:text-red-400 mb-1">Total des dépenses</p>
          <p className="text-2xl font-bold text-red-900 dark:text-red-300">
            {totalDepenses.toLocaleString('fr-FR', { minimumFractionDigits: 2 })} €
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
            {editingDepense ? 'Modifier la Dépense' : 'Nouvelle Dépense'}
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Logement *
              </label>
              <select
                value={formData.logement_id || ''}
                onChange={(e) => setFormData({ ...formData, logement_id: e.target.value })}
                className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500"
                required
              >
                <option value="">Sélectionner un logement...</option>
                {logements.map((logement) => (
                  <option key={logement.id} value={logement.id}>
                    {logement.nom}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Catégorie *
              </label>
              <select
                value={formData.categorie || ''}
                onChange={(e) => setFormData({ ...formData, categorie: e.target.value })}
                className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500"
                required
              >
                <option value="">Sélectionner une catégorie...</option>
                {CATEGORIES.map((group) => (
                  <optgroup key={group.group} label={group.group}>
                    {group.items.map((item) => (
                      <option key={item.value} value={item.value}>
                        {item.label}
                      </option>
                    ))}
                  </optgroup>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Année *
              </label>
              <input
                type="number"
                value={formData.date || ''}
                onChange={(e) => setFormData({ ...formData, date: e.target.value })}
                className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500"
                placeholder="2026"
                min="2000"
                max="2100"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Montant (€) *
              </label>
              <input
                type="number"
                step="0.01"
                value={formData.montant || ''}
                onChange={(e) => setFormData({ ...formData, montant: e.target.value ? parseFloat(e.target.value) : undefined })}
                className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500"
                placeholder="350.00"
                required
              />
            </div>

            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Description
              </label>
              <input
                type="text"
                value={formData.description || ''}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500"
                placeholder="Réparation chauffage"
              />
            </div>
          </div>

          <div className="flex gap-3">
            <button
              onClick={editingDepense ? handleUpdateDepense : handleAddDepense}
              disabled={saving}
              type="button"
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
                  {editingDepense ? 'Mettre à jour' : 'Enregistrer'}
                </>
              )}
            </button>
            <button
              onClick={handleCancelEdit}
              type="button"
              className="bg-gray-300 dark:bg-gray-600 hover:bg-gray-400 dark:hover:bg-gray-500 text-gray-900 dark:text-white font-medium py-2 px-4 rounded-lg transition-colors"
            >
              Annuler
            </button>
          </div>
        </div>
      )}

      <div className="space-y-3">
        {depenses.length === 0 ? (
          <div className="text-center py-12 text-gray-500 dark:text-gray-400">
            Aucune dépense enregistrée. Cliquez sur "Ajouter une dépense" pour commencer.
          </div>
        ) : (
          depenses
            .sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime())
            .map((depense) => (
              <div
                key={depense.id}
                className="bg-white dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-lg p-4 hover:shadow-md transition-shadow"
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                        {getLogementNom(depense.logement_id)}
                      </h3>
                      <span className="px-2 py-1 text-xs font-medium bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-400 rounded">
                        {getCategorieLabel(depense.categorie)}
                      </span>
                    </div>
                    <div className="text-sm text-gray-600 dark:text-gray-400 space-y-1">
                      <p>
                        <span className="font-medium">Année:</span>{' '}
                        {depense.date}
                      </p>
                      {depense.description && (
                        <p>
                          <span className="font-medium">Description:</span> {depense.description}
                        </p>
                      )}
                    </div>
                  </div>
                  <div className="flex items-center gap-3 flex-shrink-0">
                    <div className="text-right">
                      <p className="text-xl font-bold text-red-600 dark:text-red-400">
                        {depense.montant.toLocaleString('fr-FR', { minimumFractionDigits: 2 })} €
                      </p>
                    </div>
                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => handleEditDepense(depense)}
                        className="text-blue-600 hover:text-blue-700 dark:text-blue-400"
                        title="Modifier"
                      >
                        <Pencil className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => handleDeleteDepense(depense.id)}
                        className="text-red-600 hover:text-red-700 dark:text-red-400"
                        title="Supprimer"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            ))
        )}
      </div>
    </PageContainer>
  )
}
