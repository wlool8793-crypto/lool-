import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import {
  FileText,
  Heart,
  Settings,
  Languages,
  HelpCircle,
  Github,
  Twitter,
  Moon,
  Sun
} from 'lucide-react';
import type { DocumentType } from '../../types/common';

interface NavigationBarProps {
  selectedDocument: DocumentType;
  onDocumentChange: (type: DocumentType) => void;
}

export const NavigationBar: React.FC<NavigationBarProps> = ({
  selectedDocument,
  onDocumentChange
}) => {
  const location = useLocation();
  const [isDarkMode, setIsDarkMode] = useState(false);
  const [showMobileMenu, setShowMobileMenu] = useState(false);

  const documentTypes = [
    { id: 'cv' as DocumentType, label: 'CV Maker', icon: FileText, color: 'blue' },
    { id: 'marriage' as DocumentType, label: 'Marriage Biodata', icon: Heart, color: 'pink' }
  ];

  const toggleTheme = () => {
    setIsDarkMode(!isDarkMode);
    // Implementation for theme switching would go here
  };

  const getDocumentIcon = (type: DocumentType) => {
    const docType = documentTypes.find(dt => dt.id === type);
    return docType ? docType.icon : FileText;
  };

  return (
    <nav className="bg-white shadow-sm border-b sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo and Brand */}
          <div className="flex items-center space-x-4">
            <Link to="/" className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
                <FileText className="w-5 h-5 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">CV Maker Pro</h1>
                <p className="text-xs text-gray-500">Professional Documents Made Easy</p>
              </div>
            </Link>
          </div>

          {/* Document Type Selector */}
          <div className="hidden md:flex items-center space-x-1 bg-gray-100 rounded-lg p-1">
            {documentTypes.map((type) => {
              const Icon = type.icon;
              const isSelected = selectedDocument === type.id;
              const colorClass = type.color === 'blue' ? 'blue' : 'pink';

              return (
                <button
                  key={type.id}
                  onClick={() => onDocumentChange(type.id)}
                  className={`flex items-center space-x-2 px-4 py-2 rounded-md text-sm font-medium transition-all duration-200 ${
                    isSelected
                      ? `bg-white text-${colorClass}-600 shadow-sm`
                      : `text-gray-600 hover:text-gray-900 hover:bg-white hover:bg-opacity-50`
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  <span>{type.label}</span>
                </button>
              );
            })}
          </div>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center space-x-4">
            <button
              onClick={toggleTheme}
              className="p-2 text-gray-600 hover:text-gray-900 rounded-lg hover:bg-gray-100 transition-colors"
            >
              {isDarkMode ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
            </button>

            <Link
              to="/settings"
              className="p-2 text-gray-600 hover:text-gray-900 rounded-lg hover:bg-gray-100 transition-colors"
            >
              <Settings className="w-5 h-5" />
            </Link>

            <Link
              to="/help"
              className="p-2 text-gray-600 hover:text-gray-900 rounded-lg hover:bg-gray-100 transition-colors"
            >
              <HelpCircle className="w-5 h-5" />
            </Link>

            <div className="flex items-center space-x-2">
              <a
                href="https://github.com"
                target="_blank"
                rel="noopener noreferrer"
                className="p-2 text-gray-600 hover:text-gray-900 rounded-lg hover:bg-gray-100 transition-colors"
              >
                <Github className="w-5 h-5" />
              </a>
              <a
                href="https://twitter.com"
                target="_blank"
                rel="noopener noreferrer"
                className="p-2 text-gray-600 hover:text-gray-900 rounded-lg hover:bg-gray-100 transition-colors"
              >
                <Twitter className="w-5 h-5" />
              </a>
            </div>
          </div>

          {/* Mobile menu button */}
          <div className="md:hidden flex items-center space-x-2">
            <button
              onClick={toggleTheme}
              className="p-2 text-gray-600 hover:text-gray-900 rounded-lg hover:bg-gray-100 transition-colors"
            >
              {isDarkMode ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
            </button>
            <button
              onClick={() => setShowMobileMenu(!showMobileMenu)}
              className="p-2 text-gray-600 hover:text-gray-900 rounded-lg hover:bg-gray-100 transition-colors"
            >
              <svg
                className="w-6 h-6"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                {showMobileMenu ? (
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M6 18L18 6M6 6l12 12"
                  />
                ) : (
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M4 6h16M4 12h16M4 18h16"
                  />
                )}
              </svg>
            </button>
          </div>
        </div>
      </div>

      {/* Mobile menu */}
      {showMobileMenu && (
        <div className="md:hidden border-t bg-white">
          <div className="px-4 py-3 space-y-3">
            <div className="space-y-2">
              <p className="text-xs font-semibold text-gray-500 uppercase">Select Document Type</p>
              {documentTypes.map((type) => {
                const Icon = type.icon;
                const isSelected = selectedDocument === type.id;

                return (
                  <button
                    key={type.id}
                    onClick={() => {
                      onDocumentChange(type.id);
                      setShowMobileMenu(false);
                    }}
                    className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg text-left transition-colors ${
                      isSelected
                        ? 'bg-blue-50 text-blue-600 border border-blue-200'
                        : 'text-gray-700 hover:bg-gray-50'
                    }`}
                  >
                    <Icon className="w-5 h-5" />
                    <span className="font-medium">{type.label}</span>
                  </button>
                );
              })}
            </div>

            <div className="border-t pt-3 space-y-2">
              <Link
                to="/settings"
                onClick={() => setShowMobileMenu(false)}
                className="flex items-center space-x-3 px-4 py-3 text-gray-700 hover:bg-gray-50 rounded-lg transition-colors"
              >
                <Settings className="w-5 h-5" />
                <span>Settings</span>
              </Link>
              <Link
                to="/help"
                onClick={() => setShowMobileMenu(false)}
                className="flex items-center space-x-3 px-4 py-3 text-gray-700 hover:bg-gray-50 rounded-lg transition-colors"
              >
                <HelpCircle className="w-5 h-5" />
                <span>Help & Support</span>
              </Link>
            </div>
          </div>
        </div>
      )}
    </nav>
  );
};