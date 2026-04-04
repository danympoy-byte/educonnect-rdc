import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { AuthProvider, useAuth } from '@/context/AuthContext';
import Login from '@/components/auth/Login';
import InscriptionMultiEtapes from '@/components/auth/InscriptionMultiEtapes';
import VerificationDINACOPE from '@/components/VerificationDINACOPE';
import CompletionProfil from '@/pages/Dashboard/CompletionProfil';
import Profil from '@/pages/Dashboard/Profil';
import {
  Layout,
  Overview,
  Documents,
  Rapports,
  Provinces,
  Enseignants,
  Eleves,
  Etablissements,
  Classes,
  Presences,
  Paie,
  CarteScolaire,
  Tests,
  APIExterne,
  DINACOPE,
  Mutations,
  ControlesPlanning,
  Viabilite,
  PlanClassement,
  EntitesExternes,
  ListesDistribution
} from '@/pages/Dashboard';
import Evaluations from '@/pages/Dashboard/Evaluations';
import PartageDonnees from '@/pages/Dashboard/PartageDonnees';
import APIKeys from '@/pages/Dashboard/APIKeys';
import '@/App.css';

// Protected Route Component
const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-indigo-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Chargement...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return children;
};

// Public Route Component (redirect to dashboard if already logged in)
const PublicRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-indigo-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Chargement...</p>
        </div>
      </div>
    );
  }

  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />;
  }

  return children;
};

function AppRoutes() {
  return (
    <Routes>
      {/* Public Routes */}
      <Route
        path="/login"
        element={
          <PublicRoute>
            <Login />
          </PublicRoute>
        }
      />

      {/* Inscription Multi-Étapes */}
      <Route
        path="/inscription"
        element={
          <PublicRoute>
            <InscriptionMultiEtapes />
          </PublicRoute>
        }
      />

      {/* Protected Dashboard Routes - Nested */}
      <Route
        path="/dashboard"
        element={
          <ProtectedRoute>
            <Layout />
          </ProtectedRoute>
        }
      >
        <Route index element={<Overview />} />
        <Route path="documents" element={<Documents />} />
        <Route path="rapports" element={<Rapports />} />
        <Route path="provinces" element={<Provinces />} />
        <Route path="enseignants" element={<Enseignants />} />
        <Route path="eleves" element={<Eleves />} />
        <Route path="etablissements" element={<Etablissements />} />
        <Route path="classes" element={<Classes />} />
        <Route path="presences" element={<Presences />} />
        <Route path="paie" element={<Paie />} />
        <Route path="carte-scolaire" element={<CarteScolaire />} />
        <Route path="tests" element={<Tests />} />
        <Route path="api-keys" element={<APIKeys />} />
        <Route path="api-externe" element={<APIExterne />} />
        <Route path="dinacope" element={<DINACOPE />} />
        <Route path="mutations" element={<Mutations />} />
        <Route path="controles-planning" element={<ControlesPlanning />} />
        <Route path="viabilite" element={<Viabilite />} />
        <Route path="plan-classement" element={<PlanClassement />} />
        <Route path="entites-externes" element={<EntitesExternes />} />
        <Route path="listes-distribution" element={<ListesDistribution />} />
        <Route path="evaluations" element={<Evaluations />} />
        <Route path="partage-donnees" element={<PartageDonnees />} />
        <Route path="profil" element={<Profil />} />
        <Route path="completion-profil" element={<CompletionProfil />} />
      </Route>

      {/* Public Route - Vérification DINACOPE */}
      <Route path="/verification-dinacope/:token" element={<VerificationDINACOPE />} />

      {/* Default Route */}
      <Route path="/" element={<Navigate to="/dashboard" replace />} />
      
      {/* 404 - Redirect to dashboard */}
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  );
}

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <div className="App">
          <Toaster
            position="top-right"
            toastOptions={{
              duration: 4000,
              style: {
                background: '#363636',
                color: '#fff',
              },
              success: {
                duration: 3000,
                iconTheme: {
                  primary: '#10B981',
                  secondary: '#fff',
                },
              },
              error: {
                duration: 4000,
                iconTheme: {
                  primary: '#EF4444',
                  secondary: '#fff',
                },
              },
            }}
          />
          <AppRoutes />
        </div>
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
