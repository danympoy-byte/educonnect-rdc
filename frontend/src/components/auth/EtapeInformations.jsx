import React, { useState } from 'react';
import { Eye, EyeOff } from 'lucide-react';

const EtapeInformations = ({ formEtape1, setFormEtape1, onSubmit }) => {
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  return (
    <form onSubmit={onSubmit} className="space-y-6" data-testid="form-etape-1">
      <h3 className="text-xl font-bold text-gray-900 mb-4">Étape 1 : Informations personnelles et professionnelles</h3>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Nom *</label>
          <input type="text" value={formEtape1.nom} onChange={(e) => setFormEtape1({ ...formEtape1, nom: e.target.value })}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg" required data-testid="input-nom" />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Postnom</label>
          <input type="text" value={formEtape1.postnom} onChange={(e) => setFormEtape1({ ...formEtape1, postnom: e.target.value })}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg" data-testid="input-postnom" />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Prénom *</label>
          <input type="text" value={formEtape1.prenom} onChange={(e) => setFormEtape1({ ...formEtape1, prenom: e.target.value })}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg" required data-testid="input-prenom" />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Sexe *</label>
          <select value={formEtape1.sexe} onChange={(e) => setFormEtape1({ ...formEtape1, sexe: e.target.value })}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg" required data-testid="select-sexe">
            <option value="masculin">Masculin</option><option value="feminin">Féminin</option>
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">État civil *</label>
          <select value={formEtape1.etat_civil} onChange={(e) => setFormEtape1({ ...formEtape1, etat_civil: e.target.value })}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg" required data-testid="select-etat-civil">
            <option value="celibataire">Célibataire</option><option value="marie">Marié(e)</option>
            <option value="divorce">Divorcé(e)</option><option value="veuf">Veuf/Veuve</option>
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Date de naissance *</label>
          <input type="date" value={formEtape1.date_naissance} onChange={(e) => setFormEtape1({ ...formEtape1, date_naissance: e.target.value })}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg" required data-testid="input-date-naissance" />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Lieu de naissance *</label>
          <input type="text" value={formEtape1.lieu_naissance} onChange={(e) => setFormEtape1({ ...formEtape1, lieu_naissance: e.target.value })}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg" required placeholder="Ex: Kinshasa" data-testid="input-lieu-naissance" />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Téléphone *</label>
          <input type="tel" value={formEtape1.telephone} onChange={(e) => setFormEtape1({ ...formEtape1, telephone: e.target.value })}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg" required placeholder="+243 XXX XXX XXX" data-testid="input-telephone" />
        </div>
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Adresse *</label>
        <textarea value={formEtape1.adresse} onChange={(e) => setFormEtape1({ ...formEtape1, adresse: e.target.value })}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg" rows="2" required placeholder="Adresse complète" data-testid="input-adresse" />
      </div>
      <div className="border-t pt-6 grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Mot de passe *</label>
          <div className="relative">
            <input type={showPassword ? "text" : "password"} value={formEtape1.password}
              onChange={(e) => setFormEtape1({ ...formEtape1, password: e.target.value })}
              className="w-full px-4 py-2 pr-12 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none"
              required minLength="6" placeholder="Min. 6 caractères" data-testid="input-password" />
            <button type="button" onClick={() => setShowPassword(!showPassword)}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-700 transition"
              aria-label={showPassword ? "Masquer" : "Afficher"}>
              {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
            </button>
          </div>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Confirmer mot de passe *</label>
          <div className="relative">
            <input type={showConfirmPassword ? "text" : "password"} value={formEtape1.confirm_password}
              onChange={(e) => setFormEtape1({ ...formEtape1, confirm_password: e.target.value })}
              className="w-full px-4 py-2 pr-12 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none"
              required minLength="6" placeholder="Confirmez votre mot de passe" data-testid="input-confirm-password" />
            <button type="button" onClick={() => setShowConfirmPassword(!showConfirmPassword)}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-700 transition"
              aria-label={showConfirmPassword ? "Masquer" : "Afficher"}>
              {showConfirmPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
            </button>
          </div>
        </div>
      </div>
      <div className="flex justify-end pt-4">
        <button type="submit" className="px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 font-medium" data-testid="btn-etape1-suivant">
          Suivant
        </button>
      </div>
    </form>
  );
};

export default EtapeInformations;
