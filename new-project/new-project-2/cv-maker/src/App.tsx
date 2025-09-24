import { useState } from 'react';
import { BrowserRouter as Router } from 'react-router-dom';
import { CVProvider } from './contexts/CVContext';
import { ToastProvider } from './contexts/ToastContext';
import { LanguageProvider } from './contexts/LanguageContext';
import { NavigationBar } from './components/common/NavigationBar';
import { DocumentRoutes } from './components/common/DocumentRoutes';
import { GlobalErrorBoundary } from './components/common/GlobalErrorBoundary';
import { LoadingScreen } from './components/common/LoadingScreen';
import type { DocumentType } from './types/common';

function AppContent() {
  const [selectedDocument, setSelectedDocument] = useState<DocumentType>('cv');
  const [isLoading, setIsLoading] = useState(false);

  const handleDocumentChange = (type: DocumentType) => {
    setIsLoading(true);
    setTimeout(() => {
      setSelectedDocument(type);
      setIsLoading(false);
    }, 300);
  };

  if (isLoading) {
    return <LoadingScreen message={`Loading ${selectedDocument === 'cv' ? 'CV' : 'Marriage Biodata'} Module...`} />;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <NavigationBar selectedDocument={selectedDocument} onDocumentChange={handleDocumentChange} />

      <main className="min-h-[calc(100vh-8rem)]">
        <DocumentRoutes selectedDocument={selectedDocument} />
      </main>

      <footer className="bg-white border-t">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8">
          <div className="text-center text-gray-600">
            <p className="text-sm">
              Built with React, TypeScript, and Tailwind CSS
            </p>
            <p className="text-xs mt-2">
              Your data is stored locally in your browser and never sent to any server.
            </p>
            <p className="text-xs mt-1 text-blue-600">
              Privacy-focused • Offline-friendly • Free forever
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}

function App() {
  return (
    <Router>
      <GlobalErrorBoundary>
        <ToastProvider>
          <LanguageProvider>
            <CVProvider>
              <AppContent />
            </CVProvider>
          </LanguageProvider>
        </ToastProvider>
      </GlobalErrorBoundary>
    </Router>
  );
}

export default App;
