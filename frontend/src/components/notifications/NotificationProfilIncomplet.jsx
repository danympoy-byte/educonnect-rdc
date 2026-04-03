import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import inscriptionService from '../../services/inscription.service';

const NotificationProfilIncomplet = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [notification, setNotification] = useState(null);
  const [show, setShow] = useState(false);

  useEffect(() => {
    if (user?.id) {
      loadNotification();
    }
  }, [user]);

  const loadNotification = async () => {
    try {
      const data = await inscriptionService.getNotificationProfil(user.id);
      if (data.afficher_notification) {
        setNotification(data);
        setShow(true);
      }
    } catch (error) {
    }
  };

  const handleClose = () => {
    setShow(false);
  };

  const handleCompleterProfil = () => {
    navigate('/dashboard/profil');
  };

  if (!show || !notification) {
    return null;
  }

  return (
    <div className="fixed top-20 right-4 max-w-md z-50 animate-slide-in-right">
      <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 rounded-lg shadow-lg">
        <div className="flex items-start">
          <div className="flex-shrink-0">
            <svg className="h-5 w-5 text-yellow-400" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
            </svg>
          </div>
          <div className="ml-3 flex-1">
            <h3 className="text-sm font-medium text-yellow-800">
              Profil incomplet
            </h3>
            <div className="mt-2 text-sm text-yellow-700">
              <p>{notification.message}</p>
              <ul className="list-disc list-inside mt-2 space-y-1">
                {notification.elements_manquants.map((element, index) => (
                  <li key={index} className="capitalize">{element}</li>
                ))}
              </ul>
            </div>
            <div className="mt-4 flex space-x-3">
              <button
                onClick={handleCompleterProfil}
                className="text-sm font-medium text-yellow-800 hover:text-yellow-900 underline"
              >
                Compléter maintenant
              </button>
              <button
                onClick={handleClose}
                className="text-sm font-medium text-yellow-600 hover:text-yellow-700"
              >
                Plus tard
              </button>
            </div>
          </div>
          <div className="ml-3 flex-shrink-0">
            <button
              onClick={handleClose}
              className="inline-flex text-yellow-400 hover:text-yellow-500"
            >
              <span className="sr-only">Fermer</span>
              <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default NotificationProfilIncomplet;
