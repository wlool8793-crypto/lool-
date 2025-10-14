import React from 'react';
import { WifiOff, RefreshCw, Home } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const Offline: React.FC = () => {
  const navigate = useNavigate();

  const handleRetry = () => {
    window.location.reload();
  };

  const handleGoHome = () => {
    navigate('/');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 to-purple-50 flex items-center justify-center p-4">
      <div className="max-w-md w-full bg-white rounded-2xl shadow-xl p-8 text-center">
        {/* Offline Icon */}
        <div className="mb-6 flex justify-center">
          <div className="bg-red-100 rounded-full p-6">
            <WifiOff className="w-16 h-16 text-red-600" />
          </div>
        </div>

        {/* Title */}
        <h1 className="text-3xl font-bold text-gray-900 mb-3">
          You're Offline
        </h1>

        {/* Description */}
        <p className="text-gray-600 mb-8 leading-relaxed">
          It looks like you've lost your internet connection. Some features may not be available until you're back online.
        </p>

        {/* Info Box */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-8 text-left">
          <h3 className="font-semibold text-blue-900 mb-2 flex items-center">
            <span className="mr-2">💡</span>
            What you can still do:
          </h3>
          <ul className="text-blue-800 text-sm space-y-1">
            <li>• View previously loaded meals</li>
            <li>• Browse cached meal history</li>
            <li>• Updates will sync when back online</li>
          </ul>
        </div>

        {/* Action Buttons */}
        <div className="space-y-3">
          <button
            onClick={handleRetry}
            className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-3 px-6 rounded-lg transition-colors flex items-center justify-center space-x-2"
          >
            <RefreshCw className="w-5 h-5" />
            <span>Try Again</span>
          </button>

          <button
            onClick={handleGoHome}
            className="w-full bg-gray-100 hover:bg-gray-200 text-gray-700 font-semibold py-3 px-6 rounded-lg transition-colors flex items-center justify-center space-x-2"
          >
            <Home className="w-5 h-5" />
            <span>Go to Home</span>
          </button>
        </div>

        {/* Tips */}
        <div className="mt-8 pt-6 border-t border-gray-200">
          <p className="text-sm text-gray-500">
            Make sure your device is connected to Wi-Fi or mobile data
          </p>
        </div>
      </div>
    </div>
  );
};

export default Offline;
