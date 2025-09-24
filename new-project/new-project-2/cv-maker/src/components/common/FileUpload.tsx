import React, { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, X, FileImage, FileText } from 'lucide-react';

interface FileUploadProps {
  onFileSelect: (file: File, previewUrl: string) => void;
  onRemove?: () => void;
  currentFile?: string | null;
  accept?: {
    [key: string]: string[];
  };
  maxSize?: number;
  multiple?: boolean;
  className?: string;
  label?: string;
  description?: string;
  preview?: boolean;
  showRemove?: boolean;
}

export const FileUpload: React.FC<FileUploadProps> = ({
  onFileSelect,
  onRemove,
  currentFile,
  accept = {
    'image/*': ['.jpeg', '.jpg', '.png', '.gif', '.bmp', '.webp'],
    'application/pdf': ['.pdf']
  },
  maxSize = 10 * 1024 * 1024, // 10MB
  multiple = false,
  className = '',
  label = 'Upload File',
  description = 'Drag & drop your file here or click to browse',
  preview = true,
  showRemove = true
}) => {
  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      const file = acceptedFiles[0];

      // Create preview URL
      const previewUrl = file.type.startsWith('image/')
        ? URL.createObjectURL(file)
        : `data:${file.type};base64,${file.name}`;

      onFileSelect(file, previewUrl);
    }
  }, [onFileSelect]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept,
    maxSize,
    multiple,
    disabled: !!currentFile
  });

  const getFileIcon = (fileName: string) => {
    const extension = fileName.split('.').pop()?.toLowerCase();
    if (['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp'].includes(extension || '')) {
      return <FileImage className="w-6 h-6 text-blue-500" />;
    }
    return <FileText className="w-6 h-6 text-gray-500" />;
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className={`w-full ${className}`}>
      {currentFile ? (
        <div className="relative group">
          {preview && currentFile.startsWith('blob:') || currentFile.startsWith('data:') ? (
            // Image preview
            <div className="relative">
              <img
                src={currentFile}
                alt="Preview"
                className="w-full h-48 object-cover rounded-lg border border-gray-200"
              />
              <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-20 transition-all duration-200 rounded-lg" />
            </div>
          ) : (
            // File preview
            <div className="flex items-center space-x-3 p-4 border border-gray-200 rounded-lg bg-gray-50">
              {getFileIcon(currentFile)}
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-900 truncate">
                  {currentFile}
                </p>
                <p className="text-xs text-gray-500">
                  File uploaded
                </p>
              </div>
            </div>
          )}

          {showRemove && (
            <button
              type="button"
              onClick={onRemove}
              className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full p-1 shadow-lg hover:bg-red-600 transition-colors"
            >
              <X className="w-4 h-4" />
            </button>
          )}
        </div>
      ) : (
        <div
          {...getRootProps()}
          className={`border-2 border-dashed border-gray-300 rounded-lg p-6 text-center cursor-pointer transition-colors hover:border-blue-400 hover:bg-blue-50 ${
            isDragActive ? 'border-blue-400 bg-blue-50' : ''
          }`}
        >
          <input {...getInputProps()} />
          <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <p className="text-lg font-medium text-gray-700 mb-2">{label}</p>
          <p className="text-sm text-gray-500 mb-4">{description}</p>
          <div className="space-y-2 text-xs text-gray-400">
            <p>Accepted formats: {Object.values(accept).flat().join(', ')}</p>
            <p>Maximum size: {formatFileSize(maxSize)}</p>
          </div>
          <button
            type="button"
            className="mt-4 px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 transition-colors"
          >
            Choose File
          </button>
        </div>
      )}
    </div>
  );
};