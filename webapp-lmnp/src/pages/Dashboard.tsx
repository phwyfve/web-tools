import { TrendingDown, Euro, Building, FileText } from 'lucide-react'
import PageContainer from '../components/PageContainer'

export default function Dashboard() {
  const stats = [
    { label: 'Revenus Annuels', value: '45 000 €', change: '+12%', icon: Euro, positive: true },
    { label: 'Dépenses', value: '18 500 €', change: '-5%', icon: TrendingDown, positive: true },
    { label: 'Logements', value: '3', change: '0', icon: Building, positive: true },
    { label: 'Documents', value: '24', change: '+3', icon: FileText, positive: true },
  ]

  return (
    <PageContainer title="Tableau de bord">
      {/* Statistics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {stats.map((stat) => (
          <div
            key={stat.label}
            className="bg-gradient-to-br from-primary-50 to-blue-50 dark:from-gray-700 dark:to-gray-600 rounded-lg p-6"
          >
            <div className="flex items-center justify-between mb-4">
              <stat.icon className="w-8 h-8 text-primary-600 dark:text-primary-400" />
              <span
                className={`text-sm font-medium ${
                  stat.positive ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'
                }`}
              >
                {stat.change}
              </span>
            </div>
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">{stat.label}</p>
            <p className="text-2xl font-bold text-gray-900 dark:text-white">{stat.value}</p>
          </div>
        ))}
      </div>

      {/* Quick Overview */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-6">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Activité Récente
          </h2>
          <div className="space-y-3">
            <div className="flex items-start gap-3 text-sm">
              <div className="w-2 h-2 bg-green-500 rounded-full mt-2"></div>
              <div>
                <p className="text-gray-900 dark:text-white font-medium">Nouveau loyer reçu</p>
                <p className="text-gray-600 dark:text-gray-400">Appartement 101 - 1 200 €</p>
                <p className="text-xs text-gray-500 dark:text-gray-500 mt-1">Il y a 2 heures</p>
              </div>
            </div>
            <div className="flex items-start gap-3 text-sm">
              <div className="w-2 h-2 bg-blue-500 rounded-full mt-2"></div>
              <div>
                <p className="text-gray-900 dark:text-white font-medium">Dépense ajoutée</p>
                <p className="text-gray-600 dark:text-gray-400">Réparation chauffage - 350 €</p>
                <p className="text-xs text-gray-500 dark:text-gray-500 mt-1">Hier</p>
              </div>
            </div>
            <div className="flex items-start gap-3 text-sm">
              <div className="w-2 h-2 bg-yellow-500 rounded-full mt-2"></div>
              <div>
                <p className="text-gray-900 dark:text-white font-medium">Document ajouté</p>
                <p className="text-gray-600 dark:text-gray-400">Facture électricité mars</p>
                <p className="text-xs text-gray-500 dark:text-gray-500 mt-1">Il y a 3 jours</p>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-6">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            À faire
          </h2>
          <div className="space-y-3">
            <div className="flex items-center gap-3 p-3 bg-white dark:bg-gray-800 rounded-lg">
              <input type="checkbox" className="w-4 h-4 rounded text-primary-600" />
              <span className="text-sm text-gray-900 dark:text-white">
                Déclarer les revenus du trimestre
              </span>
            </div>
            <div className="flex items-center gap-3 p-3 bg-white dark:bg-gray-800 rounded-lg">
              <input type="checkbox" className="w-4 h-4 rounded text-primary-600" />
              <span className="text-sm text-gray-900 dark:text-white">
                Mettre à jour les informations SIREN
              </span>
            </div>
            <div className="flex items-center gap-3 p-3 bg-white dark:bg-gray-800 rounded-lg">
              <input type="checkbox" className="w-4 h-4 rounded text-primary-600" />
              <span className="text-sm text-gray-900 dark:text-white">
                Contacter l'OGA pour l'adhésion
              </span>
            </div>
          </div>
        </div>
      </div>
    </PageContainer>
  )
}
