import { useState, useEffect } from 'react'
import PageContainer from '../components/PageContainer'
import { Save, Plus, Trash2, Loader2, Pencil } from 'lucide-react'
import { lmnpApi, RecetteData, LogementData } from '../services/lmnpApi'
import { useFiscalYear } from '../contexts/FiscalYearContext'

export default function RecettesPage() {
  const { fiscalYear } = useFiscalYear()
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [logements, setLogements] = useState<LogementData[]>([])
  const [recettes, setRecettes] = useState<RecetteData[]>([])
  const [showForm, setShowForm] = useState(false)
  const [editingRecette, setEditingRecette] = useState<RecetteData | null>(null)
  const [formData, setFormData] = useState<Partial<RecetteData>>({
    logement_id: '',
    date: '',
    montant: undefined,
    description: '',
    type_recette: 'loyer_mensuel',
  })

  useEffect(() => {
    loadData()
  }, [fiscalYear])

  const loadData = async () => {
    try {
      setLoading(true)
      const data = await lmnpApi.getData(fiscalYear)
      
      if (data.logements) {
        setLogements(data.logements)
      }
      
      if (data.recettes) {
        setRecettes(data.recettes)
      }
    } catch (error) {
      console.error('Erreur lors du chargement des données:', error)
    } finally {
      setLoading(false)
    }
  }

  const saveRecettes = async (updatedRecettes: RecetteData[]) => {
    try {
      setSaving(true)
      await lmnpApi.updateRecettes(fiscalYear, updatedRecettes)
      setRecettes(updatedRecettes)
    } catch (error) {
      console.error('Erreur lors de la sauvegarde:', error)
    } finally {
      setSaving(false)
    }
  }

  const handleAddRecette = () => {
    if (formData.logement_id && formData.date && formData.montant) {
      const recetteToAdd: RecetteData = {
        id: `recette-${Date.now()}`,
        logement_id: formData.logement_id,
        date: formData.date,
        montant: formData.montant,
        description: formData.description,
        type_recette: formData.type_recette,
      }
      
      const updatedRecettes = [...recettes, recetteToAdd]
      saveRecettes(updatedRecettes)
      
      setFormData({
        logement_id: '',
        date: '',
        montant: undefined,
        description: '',
        type_recette: 'loyer_mensuel',
      })
      setShowForm(false)
    }
  }

  const handleEditRecette = (recette: RecetteData) => {
    setEditingRecette(recette)
    setFormData({
      logement_id: recette.logement_id,
      date: recette.date,
      montant: recette.montant,
      description: recette.description,
      type_recette: recette.type_recette,
    })
    setShowForm(true)
  }

  const handleUpdateRecette = () => {
    if (editingRecette && formData.logement_id && formData.date && formData.montant) {
      const updatedRecette: RecetteData = {
        ...editingRecette,
        logement_id: formData.logement_id,
        date: formData.date,
        montant: formData.montant,
        description: formData.description,
        type_recette: formData.type_recette,
      }
      
      const updatedRecettes = recettes.map(r => 
        r.id === editingRecette.id ? updatedRecette : r
      )
      saveRecettes(updatedRecettes)
      
      setFormData({
        logement_id: '',
        date: '',
        montant: undefined,
        description: '',
        type_recette: 'loyer_mensuel',
      })
      setEditingRecette(null)
      setShowForm(false)
    }
  }

  const handleCancelEdit = () => {
    setFormData({
      logement_id: '',
      date: '',
      montant: undefined,
      description: '',
      type_recette: 'loyer_mensuel',
    })
    setEditingRecette(null)
    setShowForm(false)
  }

  const handleDeleteRecette = (id: string) => {
    const updatedRecettes = recettes.filter((r) => r.id !== id)
    saveRecettes(updatedRecettes)
  }

  const getLogementNom = (logementId?: string): string => {
    if (!logementId) return 'Non spécifié'
    const logement = logements.find(l => l.id === logementId)
    return logement ? logement.nom : 'Inconnu'
  }

  const totalRecettes = recettes.reduce((sum, r) => sum + (r.montant || 0), 0)

  if (loading) {
    return (
      <PageContainer title="Recettes">
        <div className="flex items-center justify-center py-12">
          <Loader2 className="w-8 h-8 animate-spin text-primary-600" />
        </div>
      </PageContainer>
    )
  }

  return (
    <PageContainer title="Recettes">
      <div className="flex justify-between items-center mb-6">
        <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-4">
          <p className="text-sm text-green-700 dark:text-green-400 mb-1">Total des recettes</p>
          <p className="text-2xl font-bold text-green-900 dark:text-green-300">
            {totalRecettes.toLocaleString('fr-FR', { minimumFractionDigits: 2 })} €
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
            {editingRecette ? 'Modifier la Recette' : 'Nouvelle Recette'}
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
                Type de recette *
              </label>
              <select
                value={formData.type_recette || 'loyer_mensuel'}
                onChange={(e) => setFormData({ ...formData, type_recette: e.target.value })}
                className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500"
              >
                <option value="loyer_mensuel">Loyer mensuel</option>
                <option value="loyer_annuel">Loyer annuel</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                {formData.type_recette === 'loyer_annuel' ? 'Année *' : 'Mois *'}
              </label>
              {formData.type_recette === 'loyer_annuel' ? (
                <input
                  type="number"
                  value={formData.date ? new Date(formData.date).getFullYear() : ''}
                  onChange={(e) => setFormData({ ...formData, date: `${e.target.value}-01-01` })}
                  className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500"
                  placeholder="2026"
                  min="2000"
                  max="2100"
                  required
                />
              ) : (
                <input
                  type="month"
                  value={formData.date ? formData.date.substring(0, 7) : ''}
                  onChange={(e) => setFormData({ ...formData, date: `${e.target.value}-01` })}
                  className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500"
                  required
                />
              )}
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
                placeholder="1200.00"
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
                placeholder="Loyer de mars 2026"
              />
            </div>
          </div>

          <div className="flex gap-3">
            <button
              onClick={editingRecette ? handleUpdateRecette : handleAddRecette}
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
                  {editingRecette ? 'Mettre à jour' : 'Enregistrer'}
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
        {recettes.length === 0 ? (
          <div className="text-center py-12 text-gray-500 dark:text-gray-400">
            Aucune recette enregistrée. Cliquez sur "Ajouter une recette" pour commencer.
          </div>
        ) : (
          recettes
            .sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime())
            .map((recette) => (
              <div
                key={recette.id}
                className="bg-white dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-lg p-4 hover:shadow-md transition-shadow"
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                        {getLogementNom(recette.logement_id)}
                      </h3>
                      <span className="px-2 py-1 text-xs font-medium bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-400 rounded">
                        {recette.type_recette === 'loyer_mensuel' && 'Loyer mensuel'}
                        {recette.type_recette === 'loyer_annuel' && 'Loyer annuel'}
                        {recette.type_recette === 'loyer' && 'Loyer'}
                      </span>
                    </div>
                    <div className="text-sm text-gray-600 dark:text-gray-400 space-y-1">
                      <p>
                        <span className="font-medium">{recette.type_recette === 'loyer_annuel' ? 'Année:' : 'Mois:'}</span>{' '}
                        {recette.type_recette === 'loyer_annuel' 
                          ? new Date(recette.date).getFullYear()
                          : new Date(recette.date).toLocaleDateString('fr-FR', { year: 'numeric', month: 'long' })
                        }
                      </p>
                      {recette.description && (
                        <p>
                          <span className="font-medium">Description:</span> {recette.description}
                        </p>
                      )}
                    </div>
                  </div>
                  <div className="flex items-center gap-3 flex-shrink-0">
                    <div className="text-right">
                      <p className="text-xl font-bold text-green-600 dark:text-green-400">
                        {recette.montant.toLocaleString('fr-FR', { minimumFractionDigits: 2 })} €
                      </p>
                    </div>
                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => handleEditRecette(recette)}
                        className="text-blue-600 hover:text-blue-700 dark:text-blue-400"
                        title="Modifier"
                      >
                        <Pencil className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => handleDeleteRecette(recette.id)}
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
