import { useEffect, useState } from 'react'
import { AlertCircle, CheckCircle2, Send, TrendingDown, TrendingUp } from 'lucide-react'
import { lmnpApi, ValidationRecapData } from '../services/lmnpApi'
import { useFiscalYear } from '../contexts/FiscalYearContext'

export default function ValidationRecapPage() {
  const { fiscalYear } = useFiscalYear()
  const [recap, setRecap] = useState<ValidationRecapData | null>(null)
  const [loading, setLoading] = useState(true)
  const [transmitting, setTransmitting] = useState(false)
  const [error, setError] = useState<string>('')
  const [successMessage, setSuccessMessage] = useState<string>('')

  useEffect(() => {
    loadRecap()
  }, [fiscalYear])

  const loadRecap = async () => {
    try {
      setLoading(true)
      setError('')
      const data = await lmnpApi.getValidationRecap(fiscalYear)
      setRecap(data)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Erreur lors du chargement')
      console.error('Erreur chargement recap:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleTransmettre = async () => {
    if (!recap?.is_valid) return
    
    try {
      setTransmitting(true)
      setError('')
      await lmnpApi.transmettreDeclaration(fiscalYear)
      setSuccessMessage('Déclaration transmise avec succès !')
      await loadRecap() // Recharger pour mettre à jour le statut
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Erreur lors de la transmission')
      console.error('Erreur transmission:', err)
    } finally {
      setTransmitting(false)
    }
  }

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-gray-500">Chargement...</div>
      </div>
    )
  }

  if (!recap || !recap.statistiques) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-red-500">Aucune donnée disponible</div>
      </div>
    )
  }

  const { statut_declaration, is_valid, validations, statistiques } = recap

  // Déterminer le message et la couleur du bandeau selon le statut
  let statusMessage = ''
  let statusColor = ''
  let statusIcon = null

  if (statut_declaration === 'en_saisie') {
    statusMessage = 'Déclaration en cours de saisie. Veuillez transmettre votre déclaration une fois complétée.'
    statusColor = 'bg-blue-50 border-blue-200 text-blue-800'
    statusIcon = <AlertCircle className="w-5 h-5" />
  } else if (statut_declaration === 'transmise') {
    statusMessage = 'Déclaration transmise aux agents LMNP. En attente de validation.'
    statusColor = 'bg-orange-50 border-orange-200 text-orange-800'
    statusIcon = <Send className="w-5 h-5" />
  } else if (statut_declaration === 'validee') {
    statusMessage = 'Déclaration validée par l\'administration fiscale.'
    statusColor = 'bg-green-50 border-green-200 text-green-800'
    statusIcon = <CheckCircle2 className="w-5 h-5" />
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-900">Validation et Récapitulatif</h1>
      </div>

      {/* Bandeau de statut */}
      <div className={`p-4 border rounded-lg flex items-center gap-3 ${statusColor}`}>
        {statusIcon}
        <p className="font-medium">{statusMessage}</p>
      </div>

      {/* Message de succès */}
      {successMessage && (
        <div className="p-4 bg-green-50 border border-green-200 text-green-800 rounded-lg">
          {successMessage}
        </div>
      )}

      {/* Message d'erreur */}
      {error && (
        <div className="p-4 bg-red-50 border border-red-200 text-red-800 rounded-lg">
          {error}
        </div>
      )}

      {/* Statistiques */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Statistiques</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="p-4 bg-gray-50 rounded-lg">
            <div className="text-sm text-gray-600">Logements</div>
            <div className="text-2xl font-bold text-gray-900">{statistiques.nb_logements}</div>
          </div>
          <div className="p-4 bg-gray-50 rounded-lg">
            <div className="text-sm text-gray-600">Recettes</div>
            <div className="text-2xl font-bold text-gray-900">{statistiques.nb_recettes}</div>
          </div>
          <div className="p-4 bg-gray-50 rounded-lg">
            <div className="text-sm text-gray-600">Dépenses</div>
            <div className="text-2xl font-bold text-gray-900">{statistiques.nb_depenses}</div>
          </div>
          <div className="p-4 bg-gray-50 rounded-lg">
            <div className="text-sm text-gray-600">Emprunts</div>
            <div className="text-2xl font-bold text-gray-900">{statistiques.nb_emprunts}</div>
          </div>
        </div>
      </div>

      {/* Totaux */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Totaux</h2>
        <div className="space-y-3">
          <div className="flex justify-between items-center py-2 border-b">
            <span className="text-gray-700">Total des recettes</span>
            <span className="text-lg font-semibold text-green-600">
              {statistiques.total_recettes.toFixed(2)} €
            </span>
          </div>
          <div className="flex justify-between items-center py-2 border-b">
            <span className="text-gray-700">Total des dépenses</span>
            <span className="text-lg font-semibold text-red-600">
              {statistiques.total_depenses.toFixed(2)} €
            </span>
          </div>
          <div className="flex justify-between items-center py-3 bg-gray-50 px-4 rounded-lg">
            <span className="text-gray-900 font-semibold">Résultat</span>
            <span 
              className={`text-xl font-bold flex items-center gap-2 ${
                statistiques.resultat >= 0 ? 'text-green-600' : 'text-red-600'
              }`}
            >
              {statistiques.resultat >= 0 ? (
                <TrendingUp className="w-5 h-5" />
              ) : (
                <TrendingDown className="w-5 h-5" />
              )}
              {statistiques.resultat.toFixed(2)} €
            </span>
          </div>
        </div>
      </div>

      {/* Validations - Afficher seulement si pas valide */}
      {!is_valid && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center gap-2">
            <AlertCircle className="w-5 h-5 text-red-500" />
            Éléments manquants
          </h2>
          <ul className="space-y-2">
            {!validations.has_logement && (
              <li className="flex items-center gap-2 text-red-600">
                <span className="w-2 h-2 bg-red-600 rounded-full"></span>
                Vous devez saisir au moins un logement
              </li>
            )}
            {!validations.has_usage && (
              <li className="flex items-center gap-2 text-red-600">
                <span className="w-2 h-2 bg-red-600 rounded-full"></span>
                Vous devez saisir au moins un usage
              </li>
            )}
            {!validations.has_recettes && (
              <li className="flex items-center gap-2 text-red-600">
                <span className="w-2 h-2 bg-red-600 rounded-full"></span>
                Vous devez saisir au moins une recette
              </li>
            )}
            {!validations.has_depenses && (
              <li className="flex items-center gap-2 text-red-600">
                <span className="w-2 h-2 bg-red-600 rounded-full"></span>
                Vous devez saisir au moins une dépense
              </li>
            )}
            {!validations.has_statut_fiscal && (
              <li className="flex items-center gap-2 text-red-600">
                <span className="w-2 h-2 bg-red-600 rounded-full"></span>
                Vous devez remplir le statut fiscal
              </li>
            )}
          </ul>
        </div>
      )}

      {/* Bouton de transmission - Afficher seulement si en_saisie */}
      {statut_declaration === 'en_saisie' && (
        <div className="bg-white rounded-lg shadow p-6">
          <button
            onClick={handleTransmettre}
            disabled={!is_valid || transmitting}
            className={`w-full py-3 px-4 rounded-lg font-semibold flex items-center justify-center gap-2 ${
              is_valid && !transmitting
                ? 'bg-blue-600 text-white hover:bg-blue-700'
                : 'bg-gray-300 text-gray-500 cursor-not-allowed'
            }`}
          >
            <Send className="w-5 h-5" />
            {transmitting ? 'Transmission en cours...' : 'Transmettre ma déclaration'}
          </button>
          {!is_valid && (
            <p className="mt-3 text-sm text-gray-600 text-center">
              Veuillez compléter tous les éléments requis avant de transmettre votre déclaration
            </p>
          )}
        </div>
      )}
    </div>
  )
}
