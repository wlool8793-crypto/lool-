import React, { useState, useEffect } from 'react';
import { Download, X, Smartphone, Monitor } from 'lucide-react';

interface BeforeInstallPromptEvent extends Event {
  prompt: () => Promise<void>;
  userChoice: Promise<{ outcome: 'accepted' | 'dismissed' }>;
}

const InstallPrompt: React.FC = () => {
  const [deferredPrompt, setDeferredPrompt] = useState<BeforeInstallPromptEvent | null>(null);
  const [showPrompt, setShowPrompt] = useState(false);
  const [isIOS, setIsIOS] = useState(false);
  const [isInstalled, setIsInstalled] = useState(false);

  useEffect(() => {
    // Check if app is already installed
    if (window.matchMedia('(display-mode: standalone)').matches) {
      setIsInstalled(true);
      return;
    }

    // Detect iOS
    const iOS = /iPad|iPhone|iPod/.test(navigator.userAgent);
    setIsIOS(iOS);

    // Check if user has dismissed the prompt before
    const dismissed = localStorage.getItem('pwa-install-dismissed');
    const dismissedTime = dismissed ? parseInt(dismissed, 10) : 0;
    const daysSinceDismissed = (Date.now() - dismissedTime) / (1000 * 60 * 60 * 24);

    // Show prompt again after 7 days
    if (daysSinceDismissed > 7) {
      localStorage.removeItem('pwa-install-dismissed');
    }

    // Listen for beforeinstallprompt event
    const handleBeforeInstallPrompt = (e: Event) => {
      e.preventDefault();
      const installEvent = e as BeforeInstallPromptEvent;
      setDeferredPrompt(installEvent);

      // Show prompt after 1 minute of usage (if not dismissed)
      if (!dismissed || daysSinceDismissed > 7) {
        setTimeout(() => {
          setShowPrompt(true);
        }, 60000); // 1 minute
      }
    };

    window.addEventListener('beforeinstallprompt', handleBeforeInstallPrompt);

    // Listen for app installed event
    window.addEventListener('appinstalled', () => {
      setIsInstalled(true);
      setShowPrompt(false);
      console.log('PWA was installed successfully');
    });

    return () => {
      window.removeEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
    };
  }, []);

  const handleInstallClick = async () => {
    if (!deferredPrompt) {
      return;
    }

    // Show the install prompt
    deferredPrompt.prompt();

    // Wait for the user to respond
    const { outcome } = await deferredPrompt.userChoice;

    if (outcome === 'accepted') {
      console.log('User accepted the install prompt');
    } else {
      console.log('User dismissed the install prompt');
    }

    // Clear the deferred prompt
    setDeferredPrompt(null);
    setShowPrompt(false);
  };

  const handleDismiss = () => {
    setShowPrompt(false);
    localStorage.setItem('pwa-install-dismissed', Date.now().toString());
  };

  // Don't show if already installed
  if (isInstalled) {
    return null;
  }

  // iOS install instructions
  if (isIOS && showPrompt) {
    return (
      <div className="fixed bottom-4 left-4 right-4 md:left-auto md:right-4 md:w-96 z-50 animate-slide-up">
        <div className="bg-white rounded-xl shadow-2xl border border-gray-200 overflow-hidden">
          {/* Header */}
          <div className="bg-gradient-to-r from-indigo-600 to-purple-600 px-4 py-3 flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Smartphone className="w-5 h-5 text-white" />
              <h3 className="text-white font-semibold">Install App</h3>
            </div>
            <button
              onClick={handleDismiss}
              className="text-white hover:bg-white/20 rounded-full p-1 transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Content */}
          <div className="p-4">
            <p className="text-gray-700 mb-3 text-sm">
              Install this app on your iPhone:
            </p>
            <ol className="text-sm text-gray-600 space-y-2 list-decimal list-inside">
              <li>Tap the Share button <span className="inline-block">📤</span></li>
              <li>Scroll down and tap "Add to Home Screen" <span className="inline-block">➕</span></li>
              <li>Tap "Add" in the top right corner</li>
            </ol>
          </div>
        </div>
      </div>
    );
  }

  // Standard install prompt
  if (showPrompt && deferredPrompt) {
    return (
      <div className="fixed bottom-4 left-4 right-4 md:left-auto md:right-4 md:w-96 z-50 animate-slide-up">
        <div className="bg-white rounded-xl shadow-2xl border border-gray-200 overflow-hidden">
          {/* Header */}
          <div className="bg-gradient-to-r from-indigo-600 to-purple-600 px-4 py-3 flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Monitor className="w-5 h-5 text-white" />
              <h3 className="text-white font-semibold">Install App</h3>
            </div>
            <button
              onClick={handleDismiss}
              className="text-white hover:bg-white/20 rounded-full p-1 transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Content */}
          <div className="p-4">
            <p className="text-gray-700 mb-4">
              Install Hostel Meal Manager for quick access and offline functionality!
            </p>

            {/* Features */}
            <div className="bg-indigo-50 rounded-lg p-3 mb-4 space-y-1">
              <div className="flex items-start space-x-2 text-sm text-indigo-900">
                <span>✓</span>
                <span>Works offline</span>
              </div>
              <div className="flex items-start space-x-2 text-sm text-indigo-900">
                <span>✓</span>
                <span>Faster loading</span>
              </div>
              <div className="flex items-start space-x-2 text-sm text-indigo-900">
                <span>✓</span>
                <span>Home screen access</span>
              </div>
            </div>

            {/* Actions */}
            <div className="flex space-x-2">
              <button
                onClick={handleInstallClick}
                className="flex-1 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-2 px-4 rounded-lg transition-colors flex items-center justify-center space-x-2"
              >
                <Download className="w-4 h-4" />
                <span>Install</span>
              </button>
              <button
                onClick={handleDismiss}
                className="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
              >
                Later
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return null;
};

export default InstallPrompt;
