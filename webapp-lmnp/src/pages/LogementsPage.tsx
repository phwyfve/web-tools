import { useState, useEffect } from 'react'
import PageContainer from '../components/PageContainer'
import { Save, Plus, Trash2, Loader2, Pencil } from 'lucide-react'
import { lmnpApi, LogementData } from '../services/lmnpApi'
import { useFiscalYear } from '../contexts/FiscalYearContext'

export default function LogementsPage() {
  const { fiscalYear } = useFiscalYear()
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [logements, setLogements] = useState<LogementData[]>([])
  const [showForm, setShowForm] = useState(false)
  const [editingLogement, setEditingLogement] = useState<LogementData | null>(null)
  const [formData, setFormData] = useState<Partial<LogementData>>({
    nom: '',
    adresse: '',
    code_postal: '',
    ville: '',
    surface: undefined,
    nb_pieces: undefined,
    date_acquisition: '',
    prix_acquisition: undefined,
    valeur_estimee: undefined,
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
    } catch (error) {
      console.error('Erreur lors du chargement des logements:', error)
    } finally {
      setLoading(false)
    }
  }

  const saveLogements = async (updatedLogements: LogementData[]) => {
    try {
      setSaving(true)
      await lmnpApi.updateLogements(fiscalYear, updatedLogements)
      setLogements(updatedLogements)
    } catch (error) {
      console.error('Erreur lors de la sauvegarde:', error)
    } finally {
      setSaving(false)
    }
  }

  const handleAddLogement = () => {
    if (formData.nom && formData.adresse) {
      const logementToAdd: LogementData = {
        id: `logement-${Date.now()}`,
        nom: formData.nom || '',
        adresse: formData.adresse || '',
        code_postal: formData.code_postal,
        ville: formData.ville,
        surface: formData.surface,
        nb_pieces: formData.nb_pieces,
        date_acquisition: formData.date_acquisition,
        prix_acquisition: formData.prix_acquisition,
        valeur_estimee: formData.valeur_estimee,
      }
      
      const updatedLogements = [...logements, logementToAdd]
      saveLogements(updatedLogements)
      
      setFormData({
        nom: '',
        adresse: '',
        code_postal: '',
        ville: '',
        surface: undefined,
        nb_pieces: undefined,
        date_acquisition: '',
        prix_acquisition: undefined,
        valeur_estimee: undefined,
      })
      setShowForm(false)
    }
  }

  const handleEditLogement = (logement: LogementData) => {
    setEditingLogement(logement)
    setFormData({
      nom: logement.nom,
      adresse: logement.adresse,
      code_postal: logement.code_postal,
      ville: logement.ville,
      surface: logement.surface,
      nb_pieces: logement.nb_pieces,
      date_acquisition: logement.date_acquisition,
      prix_acquisition: logement.prix_acquisition,
      valeur_estimee: logement.valeur_estimee,
    })
    setShowForm(true)
  }

  const handleUpdateLogement = () => {
    if (editingLogement && formData.nom && formData.adresse) {
      const updatedLogement: LogementData = {
        ...editingLogement,
        nom: formData.nom || '',
        adresse: formData.adresse || '',
        code_postal: formData.code_postal,
        ville: formData.ville,
        surface: formData.surface,
        nb_pieces: formData.nb_pieces,
        date_acquisition: formData.date_acquisition,
        prix_acquisition: formData.prix_acquisition,
        valeur_estimee: formData.valeur_estimee,
      }
      
      const updatedLogements = logements.map(l => 
        l.id === editingLogement.id ? updatedLogement : l
      )
      saveLogements(updatedLogements)
      
      setFormData({
        nom: '',
        adresse: '',
        code_postal: '',
        ville: '',
        surface: undefined,
        nb_pieces: undefined,
        date_acquisition: '',
        prix_acquisition: undefined,
        valeur_estimee: undefined,
      })
      setEditingLogement(null)
      setShowForm(false)
    }
  }

  const handleCancelEdit = () => {
    setFormData({
      nom: '',
      adresse: '',
      code_postal: '',
      ville: '',
      surface: undefined,
      nb_pieces: undefined,
      date_acquisition: '',
      prix_acquisition: undefined,
      valeur_estimee: undefined,
    })
    setEditingLogement(null)
    setShowForm(false)
  }

  const handleDeleteLogement = (id: string) => {
    const updatedLogements = logements.filter((l) => l.id !== id)
    saveLogements(updatedLogements)
  }

  if (loading) {
    return (
      <PageContainer title="Mes Logements">
        <div className="flex items-center justify-center py-12">
          <Loader2 className="w-8 h-8 animate-spin text-primary-600" />
        </div>
      </PageContainer>
    )
  }

  return (
    <PageContainer title="Mes Logements">
      <div className="mb-6">
        <button
          onClick={() => setShowForm(!showForm)}
          className="flex items-center gap-2 bg-primary-600 hover:bg-primary-700 text-white font-medium py-2 px-4 rounded-lg transition-colors"
        >
          <Plus className="w-4 h-4" />
          Ajouter un logement
        </button>
      </div>

      {showForm && (
        <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-6 mb-6">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            {editingLogement ? 'Modifier le Logement' : 'Nouveau Logement'}
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Nom du logement *
              </label>
              <input
                type="text"
                value={formData.nom || ''}
                onChange={(e) => setFormData({ ...formData, nom: e.target.value })}
                className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500"
                placeholder="Maison Toulouse"
                required
              />
            </div>

            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Adresse
              </label>
              <input
                type="text"
                value={formData.adresse || ''}
                onChange={(e) => setFormData({ ...formData, adresse: e.target.value })}
                className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500"
                placeholder="Numéro et rue"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Code Postal
              </label>
              <input
                type="text"
                value={formData.code_postal || ''}
                onChange={(e) => setFormData({ ...formData, code_postal: e.target.value })}
                className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500"
                placeholder="75001"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Ville
              </label>
              <input
                type="text"
                value={formData.ville || ''}
                onChange={(e) => setFormData({ ...formData, ville: e.target.value })}
                className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500"
                placeholder="Paris"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Surface (m²)
              </label>
              <input
                type="number"
                value={formData.surface || ''}
                onChange={(e) => setFormData({ ...formData, surface: e.target.value ? parseFloat(e.target.value) : undefined })}
                className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500"
                placeholder="45"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Nombre de pièces
              </label>
              <input
                type="number"
                value={formData.nb_pieces || ''}
                onChange={(e) => setFormData({ ...formData, nb_pieces: e.target.value ? parseInt(e.target.value) : undefined })}
                className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500"
                placeholder="2"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Date d'acquisition
              </label>
              <input
                type="date"
                value={formData.date_acquisition || ''}
                onChange={(e) =>
                  setFormData({ ...formData, date_acquisition: e.target.value })
                }
                className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Prix d'acquisition (€)
              </label>
              <input
                type="number"
                value={formData.prix_acquisition || ''}
                onChange={(e) => setFormData({ ...formData, prix_acquisition: e.target.value ? parseFloat(e.target.value) : undefined })}
                className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500"
                placeholder="150000"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Valeur estimée (€)
              </label>
              <input
                type="number"
                step="0.01"
                value={formData.valeur_estimee || ''}
                onChange={(e) => setFormData({ ...formData, valeur_estimee: e.target.value ? parseFloat(e.target.value) : undefined })}
                className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500"
                placeholder="180000"
              />
            </div>
          </div>

          <div className="flex gap-2">
            <button
              onClick={editingLogement ? handleUpdateLogement : handleAddLogement}
              disabled={saving}
              className="flex items-center gap-2 bg-primary-600 hover:bg-primary-700 disabled:opacity-50 text-white font-medium py-2 px-4 rounded-lg transition-colors"
            >
              {saving ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Enregistrement...
                </>
              ) : (
                <>
                  <Save className="w-4 h-4" />
                  {editingLogement ? 'Mettre à jour' : 'Enregistrer'}
                </>
              )}
            </button>
            <button
              onClick={handleCancelEdit}
              className="bg-gray-300 dark:bg-gray-600 hover:bg-gray-400 dark:hover:bg-gray-500 text-gray-900 dark:text-white font-medium py-2 px-4 rounded-lg transition-colors"
            >
              Annuler
            </button>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {logements.length === 0 ? (
          <div className="col-span-full text-center py-12 text-gray-500 dark:text-gray-400">
            Aucun logement enregistré. Cliquez sur "Ajouter un logement" pour commencer.
          </div>
        ) : (
          logements.map((logement) => (
            <div
              key={logement.id}
              className="bg-white dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-lg p-6 hover:shadow-lg transition-shadow"
            >
              <div className="flex justify-between items-start mb-4 gap-2">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white flex-1 min-w-0">
                  {logement.nom}
                </h3>
                <div className="flex items-center gap-2 flex-shrink-0">
                  <button
                    onClick={() => handleEditLogement(logement)}
                    className="text-blue-600 hover:text-blue-700 dark:text-blue-400"
                    title="Modifier"
                  >
                    <Pencil className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => handleDeleteLogement(logement.id)}
                    className="text-red-600 hover:text-red-700 dark:text-red-400"
                    title="Supprimer"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
              <div className="space-y-2 text-sm">
                {logement.adresse && (
                  <p className="text-gray-600 dark:text-gray-400">
                    <span className="font-medium">Adresse:</span> {logement.adresse}
                  </p>
                )}
                {logement.code_postal && logement.ville && (
                  <p className="text-gray-600 dark:text-gray-400">
                    {logement.code_postal} {logement.ville}
                  </p>
                )}
                {logement.surface && (
                  <p className="text-gray-600 dark:text-gray-400">
                    <span className="font-medium">Surface:</span> {logement.surface} m²
                  </p>
                )}
                {logement.nb_pieces && (
                  <p className="text-gray-600 dark:text-gray-400">
                    <span className="font-medium">Pièces:</span> {logement.nb_pieces}
                  </p>
                )}
                {logement.date_acquisition && (
                  <p className="text-gray-600 dark:text-gray-400">
                    <span className="font-medium">Acquisition:</span>{' '}
                    {new Date(logement.date_acquisition).toLocaleDateString('fr-FR')}
                  </p>
                )}
                {logement.prix_acquisition && (
                  <p className="text-gray-600 dark:text-gray-400">
                    <span className="font-medium">Prix:</span>{' '}
                    {logement.prix_acquisition.toLocaleString('fr-FR')} €
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
