import React from 'react';
import api from '../../../services/api';
import toast from 'react-hot-toast';

const EnseignantManagement = ({ enseignants }) => {
  const handleExport = async () => {
    try {
            const response = await api.get(`/exports/enseignants`, {
        responseType: 'blob'
      });

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `educonnect_enseignants_${new Date().toISOString().slice(0, 10)}.xlsx`);
      document.body.appendChild(link);
      link.click();
      link.remove();

      toast.success('Export Excel téléchargé avec succès !');
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Erreur lors de l\'export');
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-900">Liste des Enseignants</h2>
        <button
          onClick={handleExport}
          className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition flex items-center space-x-2"
        >
          <span>📊</span>
          <span>Exporter Excel</span>
        </button>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Matricule</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Matières</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Prof. Principal</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {enseignants.map((ens) => (
              <tr key={ens.id} className="hover:bg-gray-50">
                <td className="px-6 py-4 text-sm font-medium text-gray-900">{ens.matricule}</td>
                <td className="px-6 py-4 text-sm text-gray-500">{ens.matieres.join(', ')}</td>
                <td className="px-6 py-4 text-sm text-gray-500">{ens.est_professeur_principal ? 'Oui' : 'Non'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default EnseignantManagement;
