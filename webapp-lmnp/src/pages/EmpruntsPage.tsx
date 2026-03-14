import { useState, useEffect } from 'react'
import PageContainer from '../components/PageContainer'
import { Save, Plus, Trash2, Loader2, Pencil } from 'lucide-react'
import { lmnpApi, EmpruntData, LogementData } from '../services/lmnpApi'

export default function EmpruntsPage() {
  const currentYear = new Date().getFullYear()
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [logements, setLogements] = useState<LogementData[]>([])
  const [emprunts, setEmprunts] = useState<EmpruntData[]>([])
  const [showForm, setShowForm] = useState(false)
  const [editingEmprunt, setEditingEmprunt] = useState<EmpruntData | null>(null)
  const [formData, setFormData] = useState<Partial<EmpruntData>>({
    logement_id: '',
    organisme: '',
    montant_initial: undefined,
    taux: undefined,
    date_debut: '',
    duree_mois: undefined,
    mensualite: undefined,
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
      
      if (data.emprunts && Array.isArray(data.emprunts)) {
        setEmprunts(data.emprunts)
      } else {
        setEmprunts([])
      }
    } catch (error) {
      console.error('Erreur lors du chargement des données:', error)
    } finally {
      setLoading(false)
    }
  }

  const saveEmprunts = async (updatedEmprunts: EmpruntData[]) => {
    try {
      setSaving(true)
      await lmnpApi.updateEmprunts(currentYear, updatedEmprunts)
      setEmprunts(updatedEmprunts)
    } catch (error) {
      console.error('Erreur lors de la sauvegarde:', error)
    } finally {
      setSaving(false)
    }
  }

  const handleAddEmprunt = () => {
    if (formData.logement_id && formData.organisme && formData.montant_initial && formData.taux && formData.date_debut && formData.duree_mois) {
      const empruntToAdd: EmpruntData = {
        id: `emprunt-${Date.now()}`,
        logement_id: formData.logement_id,
        organisme: formData.organisme,
        montant_initial: formData.montant_initial,
        taux: formData.taux,
        date_debut: formData.date_debut,
        duree_mois: formData.duree_mois,
        mensualite: formData.mensualite,
      }
      
      const updatedEmprunts = [...emprunts, empruntToAdd]
      saveEmprunts(updatedEmprunts)
      
      setFormData({
        logement_id: '',
        organisme: '',
        montant_initial: undefined,
        taux: undefined,
        date_debut: '',
        duree_mois: undefined,
        mensualite: undefined,
      })
      setShowForm(false)
    }
  }

  const handleEditEmprunt = (emprunt: EmpruntData) => {
    setEditingEmprunt(emprunt)
    setFormData({
      logement_id: emprunt.logement_id,
      organisme: emprunt.organisme,
      montant_initial: emprunt.montant_initial,
      taux: emprunt.taux,
      date_debut: emprunt.date_debut,
      duree_mois: emprunt.duree_mois,
      mensualite: emprunt.mensualite,
    })
    setShowForm(true)
  }

  const handleUpdateEmprunt = () => {
    if (editingEmprunt && formData.logement_id && formData.organisme && formData.montant_initial && formData.taux && formData.date_debut && formData.duree_mois) {
      const updatedEmprunt: EmpruntData = {
        ...editingEmprunt,
        logement_id: formData.logement_id,
        organisme: formData.organisme,
        montant_initial: formData.montant_initial,
        taux: formData.taux,
        date_debut: formData.date_debut,
        duree_mois: formData.duree_mois,
        mensualite: formData.mensualite || undefined,
      }
      
      const updatedEmprunts = emprunts.map(e => 
        e.id === editingEmprunt.id ? updatedEmprunt : e
      )
      saveEmprunts(updatedEmprunts)
      
      setFormData({
        logement_id: '',
        organisme: '',
        montant_initial: undefined,
        taux: undefined,
        date_debut: '',
        duree_mois: undefined,
        mensualite: undefined,
      })
      setEditingEmprunt(null)
      setShowForm(false)
    }
  }

  const handleCancelEdit = () => {
    setFormData({
      logement_id: '',
      organisme: '',
      montant_initial: undefined,
      taux: undefined,
      date_debut: '',
      duree_mois: undefined,
      mensualite: undefined,
    })
    setEditingEmprunt(null)
    setShowForm(false)
  }

  const handleDeleteEmprunt = (id: string) => {
    const updatedEmprunts = emprunts.filter((e) => e.id !== id)
    saveEmprunts(updatedEmprunts)
  }

  const getLogementNom = (logementId?: string): string => {
    if (!logementId) return 'Non spécifié'
    const logement = logements.find(l => l.id === logementId)
    return logement ? logement.nom : 'Inconnu'
  }

  const totalEmprunts = emprunts.reduce((sum, e) => sum + (e.montant_initial || 0), 0)

  if (loading) {
    return (
      <PageContainer title="Emprunts">
        <div className="flex items-center justify-center py-12">
          <Loader2 className="w-8 h-8 animate-spin text-primary-600" />
        </div>
      </PageContainer>
    )
  }

  return (
    <PageContainer title="Emprunts">
      <div className="flex justify-between items-center mb-6">
        <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
          <p className="text-sm text-blue-700 dark:text-blue-400 mb-1">Total emprunté</p>
          <p className="text-2xl font-bold text-blue-900 dark:text-blue-300">
            {totalEmprunts.toLocaleString('fr-FR', { minimumFractionDigits: 2 })} €
          </p>
        </div>
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
            {editingEmprunt ? 'Modifier l\'Emprunt' : 'Nouvel Emprunt'}
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
                Organisme prêteur *
              </label>
              <input
                type="text"
                value={formData.organisme || ''}
                onChange={(e) => setFormData({ ...formData, organisme: e.target.value })}
                className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500"
                placeholder="Crédit Agricole"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Montant initial (€) *
              </label>
              <input
                type="number"
                step="0.01"
                value={formData.montant_initial || ''}
                onChange={(e) => setFormData({ ...formData, montant_initial: e.target.value ? parseFloat(e.target.value) : undefined })}
                className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500"
                placeholder="200000"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Taux d'intérêt (%) *
              </label>
              <input
                type="number"
                step="0.01"
                value={formData.taux || ''}
                onChange={(e) => setFormData({ ...formData, taux: e.target.value ? parseFloat(e.target.value) : undefined })}
                className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500"
                placeholder="1.5"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Durée (mois) *
              </label>
              <input
                type="number"
                value={formData.duree_mois || ''}
                onChange={(e) => setFormData({ ...formData, duree_mois: e.target.value ? parseInt(e.target.value) : undefined })}
                className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500"
                placeholder="240"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Date de début *
              </label>
              <input
                type="date"
                value={formData.date_debut || ''}
                onChange={(e) => setFormData({ ...formData, date_debut: e.target.value })}
                className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Mensualité (€)
              </label>
              <input
                type="number"
                step="0.01"
                value={formData.mensualite || ''}
                onChange={(e) => setFormData({ ...formData, mensualite: e.target.value ? parseFloat(e.target.value) : undefined })}
                className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500"
                placeholder="965"
              />
            </div>
          </div>

          <div className="flex gap-3">
            <button
              onClick={editingEmprunt ? handleUpdateEmprunt : handleAddEmprunt}
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
                  {editingEmprunt ? 'Mettre à jour' : 'Enregistrer'}
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
        {emprunts.length === 0 ? (
          <div className="text-center py-12 text-gray-500 dark:text-gray-400">
            Aucun emprunt enregistré. Cliquez sur "Ajouter un emprunt" pour commencer.
          </div>
        ) : (
          emprunts
            .sort((a, b) => new Date(a.date_debut).getTime() - new Date(b.date_debut).getTime())
            .map((emprunt) => (
              <div
                key={emprunt.id}
                className="bg-white dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-lg p-4 hover:shadow-md transition-shadow"
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                        {getLogementNom(emprunt.logement_id)}
                      </h3>
                      <span className="px-2 py-1 text-xs font-medium bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-400 rounded">
                        {emprunt.organisme}
                      </span>
                    </div>
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-3 text-sm text-gray-600 dark:text-gray-400">
                      <div>
                        <span className="font-medium">Montant initial:</span>{' '}
                        {emprunt.montant_initial.toLocaleString('fr-FR', { minimumFractionDigits: 2 })} €
                      </div>
                      <div>
                        <span className="font-medium">Taux:</span> {emprunt.taux}%
                      </div>
                      <div>
                        <span className="font-medium">Durée:</span> {emprunt.duree_mois} mois
                      </div>
                      <div>
                        <span className="font-medium">Date début:</span>{' '}
                        {new Date(emprunt.date_debut).toLocaleDateString('fr-FR')}
                      </div>
                      {emprunt.mensualite && (
                        <div>
                          <span className="font-medium">Mensualité:</span>{' '}
                          {emprunt.mensualite.toLocaleString('fr-FR', { minimumFractionDigits: 2 })} €
                        </div>
                      )}
                    </div>
                  </div>
                  <div className="flex items-center gap-2 flex-shrink-0">
                    <button
                      onClick={() => handleEditEmprunt(emprunt)}
                      className="text-blue-600 hover:text-blue-700 dark:text-blue-400"
                      title="Modifier"
                    >
                      <Pencil className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => handleDeleteEmprunt(emprunt.id)}
                      className="text-red-600 hover:text-red-700 dark:text-red-400"
                      title="Supprimer"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </div>
            ))
        )}
      </div>
    </PageContainer>
  )
}
