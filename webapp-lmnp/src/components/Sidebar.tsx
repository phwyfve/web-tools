import { NavLink } from 'react-router-dom'
import { 
  LayoutDashboard, 
  Building, 
  Home, 
  Zap, 
  Euro, 
  Receipt, 
  CreditCard, 
  FileText, 
  Settings,
  HelpCircle,
  Building2
} from 'lucide-react'

const menuItems = [
  { path: '/dashboard', label: 'Tableau de bord', icon: LayoutDashboard },
  { path: '/siren', label: 'SIREN', icon: Building },
  { path: '/logements', label: 'Logements', icon: Home },
  { path: '/usage', label: 'Usage du logement', icon: Zap },
  { path: '/recettes', label: 'Recettes', icon: Euro },
  { path: '/depenses', label: 'Dépenses', icon: Receipt },
  { path: '/emprunts', label: 'Emprunts', icon: CreditCard },
  { path: '/oga', label: 'OGA', icon: FileText },
  { path: '/statut-fiscal', label: 'Statut fiscal et social', icon: Settings },
]

export default function Sidebar() {
  return (
    <aside className="w-64 bg-white dark:bg-gray-800 shadow-lg flex flex-col">
      {/* Logo */}
      <div className="p-6 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center gap-3">
          <div className="bg-primary-600 p-2 rounded-lg">
            <Building2 className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-gray-900 dark:text-white">LMNP</h1>
            <p className="text-xs text-gray-600 dark:text-gray-400">Manager</p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto py-6 px-3">
        <ul className="space-y-1">
          {menuItems.map((item) => (
            <li key={item.path}>
              <NavLink
                to={item.path}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                    isActive
                      ? 'bg-primary-50 dark:bg-primary-900/20 text-primary-700 dark:text-primary-400 font-medium'
                      : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
                  }`
                }
              >
                <item.icon className="w-5 h-5 flex-shrink-0" />
                <span className="text-sm">{item.label}</span>
              </NavLink>
            </li>
          ))}
        </ul>
      </nav>

      {/* Footer aide */}
      <div className="p-4 border-t border-gray-200 dark:border-gray-700">
        <button className="flex items-center gap-3 px-4 py-3 w-full text-left rounded-lg text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors">
          <HelpCircle className="w-5 h-5 flex-shrink-0" />
          <span className="text-sm">Aide & FAQ</span>
        </button>
      </div>
    </aside>
  )
}
