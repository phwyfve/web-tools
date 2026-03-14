import { useState, useEffect } from 'react'
import PageContainer from '../components/PageContainer'
import { Save, Plus, Trash2, Loader2, Pencil } from 'lucide-react'
import { lmnpApi, UsageData, LogementData } from '../services/lmnpApi'

export default function UsagePage() {
  const currentYear = new Date().getFullYear()
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [logements, setLogements] = useState<LogementData[]>([])
  const [usages, setUsages] = useState<UsageData[]>([])
  const [showForm, setShowForm] = useState(false)
  const [editingUsage, setEditingUsage] = useState<UsageData | null>(null)
  const [formData, setFormData] = useState<Partial<UsageData>>({
    logement_id: '',
    type_usage: '',
    date_debut: '',
    date_fin: '',
    nb_jours_location: undefined,
    nb_jours_perso: undefined,
    est_residence_principale: false,
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
      
      if (data.usage && Array.isArray(data.usage)) {
        setUsages(data.usage)
      } else {
        setUsages([])
      }
    } catch (error) {
      console.error('Erreur lors du chargement des données:', error)
    } finally {
      setLoading(false)
    }
  }

  const saveUsages = async (updatedUsages: UsageData[]) => {
    try {
      setSaving(true)
      await lmnpApi.updateUsage(currentYear, updatedUsages)
      setUsages(updatedUsages)
    } catch (error) {
      console.error('Erreur lors de la sauvegarde:', error)
    } finally {
      setSaving(false)
    }
  }

  const handleAddUsage = () => {
    if (formData.logement_id && formData.type_usage) {
      const usageToAdd: UsageData = {
        id: `usage-${Date.now()}`,
        logement_id: formData.logement_id || '',
        type_usage: formData.type_usage || undefined,
        date_debut: formData.date_debut || undefined,
        date_fin: formData.date_fin || undefined,
        nb_jours_location: formData.nb_jours_location,
        nb_jours_perso: formData.nb_jours_perso,
        est_residence_principale: formData.est_residence_principale,
      }
      
      const updatedUsages = [...usages, usageToAdd]
      saveUsages(updatedUsages)
      
      setFormData({
        logement_id: '',
        type_usage: '',
        date_debut: '',
        date_fin: '',
        nb_jours_location: undefined,
        nb_jours_perso: undefined,
        est_residence_principale: false,
      })
      setShowForm(false)
    }
  }

  const handleEditUsage = (usage: UsageData) => {
    setEditingUsage(usage)
    setFormData({
      logement_id: usage.logement_id,
      type_usage: usage.type_usage,
      date_debut: usage.date_debut,
      date_fin: usage.date_fin,
      nb_jours_location: usage.nb_jours_location,
      nb_jours_perso: usage.nb_jours_perso,
      est_residence_principale: usage.est_residence_principale,
    })
    setShowForm(true)
  }

  const handleUpdateUsage = () => {
    if (editingUsage && formData.logement_id && formData.type_usage) {
      const updatedUsage: UsageData = {
        ...editingUsage,
        logement_id: formData.logement_id || '',
        type_usage: formData.type_usage || undefined,
        date_debut: formData.date_debut || undefined,
        date_fin: formData.date_fin || undefined,
        nb_jours_location: formData.nb_jours_location,
        nb_jours_perso: formData.nb_jours_perso,
        est_residence_principale: formData.est_residence_principale,
      }
      
      const updatedUsages = usages.map(u => 
        u.id === editingUsage.id ? updatedUsage : u
      )
      saveUsages(updatedUsages)
      
      setFormData({
        logement_id: '',
        type_usage: '',
        date_debut: '',
        date_fin: '',
        nb_jours_location: undefined,
        nb_jours_perso: undefined,
        est_residence_principale: false,
      })
      setEditingUsage(null)
      setShowForm(false)
    }
  }

  const handleCancelEdit = () => {
    setFormData({
      logement_id: '',
      type_usage: '',
      date_debut: '',
      date_fin: '',
      nb_jours_location: undefined,
      nb_jours_perso: undefined,
      est_residence_principale: false,
    })
    setEditingUsage(null)
    setShowForm(false)
  }

  const handleDeleteUsage = (id: string) => {
    const updatedUsages = usages.filter((u) => u.id !== id)
    saveUsages(updatedUsages)
  }

  const getLogementNom = (logementId: string): string => {
    const logement = logements.find(l => l.id === logementId)
    return logement ? logement.nom : 'Inconnu'
  }

  if (loading) {
    return (
      <PageContainer title="Usage des Logements">
        <div className="flex items-center justify-center py-12">
          <Loader2 className="w-8 h-8 animate-spin text-primary-600" />
        </div>
      </PageContainer>
    )
  }

  return (
    <PageContainer title="Usage des Logements">
      <div className="mb-6">
        <button
          onClick={() => setShowForm(!showForm)}
          className="flex items-center gap-2 bg-primary-600 hover:bg-primary-700 text-white font-medium py-2 px-4 rounded-lg transition-colors"
        >
          <Plus className="w-4 h-4" />
          Ajouter un usage
        </button>
      </div>

      {showForm && (
        <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-6 mb-6">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            {editingUsage ? 'Modifier l\'Usage' : 'Nouvel Usage'}
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
                Type d'usage *
              </label>
              <select
                value={formData.type_usage || ''}
                onChange={(e) => setFormData({ ...formData, type_usage: e.target.value })}
                className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500"
                required
              >
                <option value="">Sélectionner un type...</option>
                <option value="location">Location meublée classique</option>
                <option value="location_courte_duree">Location courte durée</option>
                <option value="mixte">Mixte</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Date de début
              </label>
              <input
                type="date"
                value={formData.date_debut || ''}
                onChange={(e) => setFormData({ ...formData, date_debut: e.target.value })}
                className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Date de fin
              </label>
              <input
                type="date"
                value={formData.date_fin || ''}
                onChange={(e) => setFormData({ ...formData, date_fin: e.target.value })}
                className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Nombre de jours en location
              </label>
              <input
                type="number"
                value={formData.nb_jours_location || ''}
                onChange={(e) => setFormData({ ...formData, nb_jours_location: e.target.value ? parseInt(e.target.value) : undefined })}
                className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500"
                placeholder="300"
                min="0"
                max="365"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Nombre de jours à usage personnel
              </label>
              <input
                type="number"
                value={formData.nb_jours_perso || ''}
                onChange={(e) => setFormData({ ...formData, nb_jours_perso: e.target.value ? parseInt(e.target.value) : undefined })}
                className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500"
                placeholder="30"
                min="0"
                max="365"
              />
            </div>
          </div>

          <div className="flex items-center gap-3 mb-4">
            <input
              type="checkbox"
              id="estResidencePrincipale"
              checked={formData.est_residence_principale || false}
              onChange={(e) => setFormData({ ...formData, est_residence_principale: e.target.checked })}
              className="w-4 h-4 rounded text-primary-600"
            />
            <label htmlFor="estResidencePrincipale" className="text-sm text-gray-700 dark:text-gray-300">
              Est ma résidence principale
            </label>
          </div>

          <div className="flex gap-3">
            <button
              onClick={editingUsage ? handleUpdateUsage : handleAddUsage}
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
                  {editingUsage ? 'Mettre à jour' : 'Enregistrer'}
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

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {usages.length === 0 ? (
          <div className="col-span-full text-center py-12 text-gray-500 dark:text-gray-400">
            Aucun usage enregistré. Cliquez sur "Ajouter un usage" pour commencer.
          </div>
        ) : (
          usages.map((usage) => (
            <div
              key={usage.id}
              className="bg-white dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-lg p-6 hover:shadow-lg transition-shadow"
            >
              <div className="flex justify-between items-start mb-4 gap-2">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white flex-1 min-w-0">
                  {getLogementNom(usage.logement_id)}
                </h3>
                <div className="flex items-center gap-2 flex-shrink-0">
                  <button
                    onClick={() => handleEditUsage(usage)}
                    className="text-blue-600 hover:text-blue-700 dark:text-blue-400"
                    title="Modifier"
                  >
                    <Pencil className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => handleDeleteUsage(usage.id)}
                    className="text-red-600 hover:text-red-700 dark:text-red-400"
                    title="Supprimer"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
              <div className="space-y-2 text-sm">
                {usage.type_usage && (
                  <p className="text-gray-600 dark:text-gray-400">
                    <span className="font-medium">Type:</span>{' '}
                    {usage.type_usage === 'location' && 'Location meublée classique'}
                    {usage.type_usage === 'location_courte_duree' && 'Location courte durée'}
                    {usage.type_usage === 'mixte' && 'Mixte'}
                  </p>
                )}
                {usage.date_debut && (
                  <p className="text-gray-600 dark:text-gray-400">
                    <span className="font-medium">Début:</span> {new Date(usage.date_debut).toLocaleDateString('fr-FR')}
                  </p>
                )}
                {usage.date_fin && (
                  <p className="text-gray-600 dark:text-gray-400">
                    <span className="font-medium">Fin:</span> {new Date(usage.date_fin).toLocaleDateString('fr-FR')}
                  </p>
                )}
                {usage.nb_jours_location !== undefined && (
                  <p className="text-gray-600 dark:text-gray-400">
                    <span className="font-medium">Jours location:</span> {usage.nb_jours_location}
                  </p>
                )}
                {usage.nb_jours_perso !== undefined && (
                  <p className="text-gray-600 dark:text-gray-400">
                    <span className="font-medium">Jours perso:</span> {usage.nb_jours_perso}
                  </p>
                )}
                {usage.est_residence_principale && (
                  <p className="text-primary-600 dark:text-primary-400 font-medium">
                    Résidence principale
                  </p>
                )}
              </div>
            </div>
          ))
        )}
      </div>
    </PageContainer>
  )
}
