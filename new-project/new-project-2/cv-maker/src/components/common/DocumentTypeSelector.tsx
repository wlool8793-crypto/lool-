import React from 'react';
import { Card } from '../ui/card';
import { Button } from '../ui/button';
import { FileText, Heart } from 'lucide-react';

interface DocumentTypeSelectorProps {
  onSelect: (type: 'cv' | 'marriage') => void;
}

export const DocumentTypeSelector: React.FC<DocumentTypeSelectorProps> = ({ onSelect }) => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="max-w-4xl w-full">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Welcome to CV Maker Pro
          </h1>
          <p className="text-xl text-gray-600">
            Create Professional CVs or Marriage Biodata with our comprehensive platform
          </p>
        </div>

        <div className="grid md:grid-cols-2 gap-8">
          {/* Professional CV Card */}
          <Card className="p-8 hover:shadow-xl transition-all duration-300 border-2 border-transparent hover:border-blue-200">
            <div className="text-center">
              <div className="w-20 h-20 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-6">
                <FileText className="w-10 h-10 text-blue-600" />
              </div>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">Professional CV</h2>
              <p className="text-gray-600 mb-6">
                Create a professional resume for job applications and career development
              </p>
              <div className="text-left space-y-3 mb-8">
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                  <span className="text-sm text-gray-600">9-step guided creation process</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                  <span className="text-sm text-gray-600">5 professional templates</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                  <span className="text-sm text-gray-600">Real-time preview</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                  <span className="text-sm text-gray-600">PDF export functionality</span>
                </div>
              </div>
              <Button
                onClick={() => onSelect('cv')}
                className="w-full bg-blue-600 hover:bg-blue-700 text-white py-3"
              >
                Create Professional CV
              </Button>
            </div>
          </Card>

          {/* Marriage Biodata Card */}
          <Card className="p-8 hover:shadow-xl transition-all duration-300 border-2 border-transparent hover:border-pink-200">
            <div className="text-center">
              <div className="w-20 h-20 bg-pink-100 rounded-full flex items-center justify-center mx-auto mb-6">
                <Heart className="w-10 h-10 text-pink-600" />
              </div>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">Marriage Biodata</h2>
              <p className="text-gray-600 mb-6">
                Create comprehensive marriage biodata with cultural and traditional elements
              </p>
              <div className="text-left space-y-3 mb-8">
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-pink-500 rounded-full"></div>
                  <span className="text-sm text-gray-600">11-step comprehensive creation</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-pink-500 rounded-full"></div>
                  <span className="text-sm text-gray-600">4 cultural templates</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-pink-500 rounded-full"></div>
                  <span className="text-sm text-gray-600">Family & religious information</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-pink-500 rounded-full"></div>
                  <span className="text-sm text-gray-600">Horoscope integration</span>
                </div>
              </div>
              <Button
                onClick={() => onSelect('marriage')}
                className="w-full bg-pink-600 hover:bg-pink-700 text-white py-3"
              >
                Create Marriage Biodata
              </Button>
            </div>
          </Card>
        </div>

        <div className="text-center mt-12">
          <p className="text-sm text-gray-500">
            Choose the document type that best suits your needs
          </p>
        </div>
      </div>
    </div>
  );
};