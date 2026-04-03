import React from 'react';

const StatsCards = ({ stats }) => {
  if (!stats) return null;

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {/* Établissements */}
      <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-gray-600">Établissements</p>
            <p className="text-3xl font-bold text-gray-900 mt-2">
              {stats.total_etablissements?.toLocaleString()}
            </p>
          </div>
          <div className="w-12 h-12 bg-indigo-100 rounded-full flex items-center justify-center">
            <span className="text-2xl">🏫</span>
          </div>
        </div>
      </div>

      {/* Enseignants */}
      <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-gray-600">Enseignants</p>
            <p className="text-3xl font-bold text-gray-900 mt-2">
              {stats.total_enseignants?.toLocaleString()}
            </p>
          </div>
          <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center overflow-hidden p-2">
            <img 
              src="/images/african_teacher.png" 
              alt="Enseignants" 
              className="w-full h-full object-contain"
            />
          </div>
        </div>
      </div>

      {/* Élèves */}
      <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-gray-600">Élèves</p>
            <p className="text-3xl font-bold text-gray-900 mt-2">
              {stats.total_eleves?.toLocaleString()}
            </p>
          </div>
          <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center overflow-hidden p-2">
            <img 
              src="/images/african_students.png" 
              alt="Élèves" 
              className="w-full h-full object-contain"
            />
          </div>
        </div>
        <div className="mt-4 text-xs text-gray-500">
          <span className="mr-3">Primaire: {stats.total_eleves_primaire?.toLocaleString()}</span>
          <span>Secondaire: {stats.total_eleves_secondaire?.toLocaleString()}</span>
        </div>
      </div>

      {/* Classes */}
      <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-gray-600">Classes</p>
            <p className="text-3xl font-bold text-gray-900 mt-2">
              {stats.total_classes?.toLocaleString()}
            </p>
          </div>
          <div className="w-12 h-12 bg-yellow-100 rounded-full flex items-center justify-center">
            <span className="text-2xl">📚</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default StatsCards;
