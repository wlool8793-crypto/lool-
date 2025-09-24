import React from 'react';
import { useCV } from '../../../contexts/CVContext';
import { Label } from '../../common/Label';
import { Button } from '../../common/Button';
import { FileUpload } from '../../common/FileUpload';
import { marriagePhotosSchema } from '../../../validations/marriageSchemas';

interface UploadedFile {
  file: File;
  previewUrl: string;
  uploadDate: string;
}

export const MarriagePhotosStep: React.FC = () => {
  const { state, dispatch } = useCV();
  const [uploadedFiles, setUploadedFiles] = React.useState<{
    profile: UploadedFile | null;
    additional: UploadedFile[];
    idProof: UploadedFile | null;
    certificates: UploadedFile[];
  }>({
    profile: null,
    additional: [],
    idProof: null,
    certificates: []
  });

  const [errors, setErrors] = React.useState<Record<string, string>>({});

  const handleFileSelect = (field: string, file: File, previewUrl: string, index?: number) => {
    const uploadedFile: UploadedFile = {
      file,
      previewUrl,
      uploadDate: new Date().toISOString()
    };

    if (field === 'profile') {
      setUploadedFiles(prev => ({ ...prev, profile: uploadedFile }));
    } else if (field === 'idProof') {
      setUploadedFiles(prev => ({ ...prev, idProof: uploadedFile }));
    } else if (field === 'additional' && index !== undefined) {
      setUploadedFiles(prev => ({
        ...prev,
        additional: prev.additional.map((item, i) => i === index ? uploadedFile : item)
      }));
    } else if (field === 'certificates' && index !== undefined) {
      setUploadedFiles(prev => ({
        ...prev,
        certificates: prev.certificates.map((item, i) => i === index ? uploadedFile : item)
      }));
    }

    // Clear error when file is uploaded
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }));
    }
  };

  const handleFileRemove = (field: string, index?: number) => {
    if (field === 'profile') {
      setUploadedFiles(prev => ({ ...prev, profile: null }));
    } else if (field === 'idProof') {
      setUploadedFiles(prev => ({ ...prev, idProof: null }));
    } else if (field === 'additional' && index !== undefined) {
      setUploadedFiles(prev => ({
        ...prev,
        additional: prev.additional.filter((_, i) => i !== index)
      }));
    } else if (field === 'certificates' && index !== undefined) {
      setUploadedFiles(prev => ({
        ...prev,
        certificates: prev.certificates.filter((_, i) => i !== index)
      }));
    }
  };

  const addAdditionalPhoto = () => {
    if (uploadedFiles.additional.length < 10) {
      setUploadedFiles(prev => ({
        ...prev,
        additional: [...prev.additional, null as any]
      }));
    }
  };

  const addCertificate = () => {
    if (uploadedFiles.certificates.length < 10) {
      setUploadedFiles(prev => ({
        ...prev,
        certificates: [...prev.certificates, null as any]
      }));
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    // Validate at least one photo is uploaded
    if (!uploadedFiles.profile && uploadedFiles.additional.length === 0) {
      setErrors({ form: 'Please upload at least one photo' });
      return;
    }

    try {
      // Convert uploaded files to format expected by schema
      const formData = {
        profile: uploadedFiles.profile?.previewUrl || '',
        additional: uploadedFiles.additional.map(f => f?.previewUrl || '').filter(Boolean),
        idProof: uploadedFiles.idProof?.previewUrl || '',
        certificates: uploadedFiles.certificates.map(f => f?.previewUrl || '').filter(Boolean)
      };

      marriagePhotosSchema.parse(formData);

      dispatch({
        type: 'UPDATE_MARRIAGE_DATA',
        payload: {
          photos: formData,
          uploadedFiles: uploadedFiles // Store full file data for future use
        }
      });

      dispatch({ type: 'NEXT_STEP' });
    } catch (error) {
      if (error && typeof error === 'object' && 'errors' in error) {
        const fieldErrors: Record<string, string> = {};
        const zodError = error as any;
        if (zodError.errors && Array.isArray(zodError.errors)) {
          zodError.errors.forEach((err: any) => {
            if (err.path && err.path.length > 0) {
              fieldErrors[err.path.join('.')] = err.message;
            }
          });
        }
        setErrors(fieldErrors);
      } else {
        setErrors({ form: 'Please check all fields and try again' });
      }
    }
  };

  return (
    <div className="max-w-2xl mx-auto">
      <h2 className="text-2xl font-bold text-gray-900 mb-6">Photos & Documents</h2>

      {errors.form && (
        <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-md">
          <p className="text-sm text-red-800">{errors.form}</p>
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="grid grid-cols-1 gap-6">
          {/* Profile Photo */}
          <div>
            <Label>Profile Photo *</Label>
            <div className="mt-2">
              <FileUpload
                onFileSelect={(file, previewUrl) => handleFileSelect('profile', file, previewUrl)}
                onRemove={() => handleFileRemove('profile')}
                currentFile={uploadedFiles.profile?.previewUrl}
                accept={{
                  'image/*': ['.jpeg', '.jpg', '.png', '.gif', '.bmp', '.webp']
                }}
                maxSize={5 * 1024 * 1024} // 5MB
                label="Upload Profile Photo"
                description="Choose a clear, recent photo of yourself"
                className="w-64"
              />
            </div>
          </div>

          {/* Additional Photos */}
          <div>
            <Label>Additional Photos (up to 10)</Label>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mt-2">
              {uploadedFiles.additional.map((file, index) => (
                <div key={index}>
                  <FileUpload
                    onFileSelect={(file, previewUrl) => handleFileSelect('additional', file, previewUrl, index)}
                    onRemove={() => handleFileRemove('additional', index)}
                    currentFile={file?.previewUrl}
                    accept={{
                      'image/*': ['.jpeg', '.jpg', '.png', '.gif', '.bmp', '.webp']
                    }}
                    maxSize={5 * 1024 * 1024}
                    label={`Photo ${index + 1}`}
                    description="Additional photo"
                    showRemove={!!file}
                  />
                </div>
              ))}
              {uploadedFiles.additional.length < 10 && (
                <div className="flex items-center justify-center">
                  <Button
                    type="button"
                    variant="outline"
                    onClick={addAdditionalPhoto}
                    className="h-full min-h-[200px] w-full"
                  >
                    Add Photo +
                  </Button>
                </div>
              )}
            </div>
          </div>

          {/* ID Proof */}
          <div>
            <Label>ID Proof (Optional)</Label>
            <div className="mt-2">
              <FileUpload
                onFileSelect={(file, previewUrl) => handleFileSelect('idProof', file, previewUrl)}
                onRemove={() => handleFileRemove('idProof')}
                currentFile={uploadedFiles.idProof?.previewUrl}
                accept={{
                  'image/*': ['.jpeg', '.jpg', '.png', '.gif', '.bmp', '.webp'],
                  'application/pdf': ['.pdf']
                }}
                maxSize={10 * 1024 * 1024} // 10MB
                label="Upload ID Proof"
                description="Aadhaar Card, Passport, Driver's License, etc."
                className="w-80"
              />
            </div>
          </div>

          {/* Certificates */}
          <div>
            <Label>Certificates (up to 10)</Label>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-2">
              {uploadedFiles.certificates.map((file, index) => (
                <div key={index}>
                  <FileUpload
                    onFileSelect={(file, previewUrl) => handleFileSelect('certificates', file, previewUrl, index)}
                    onRemove={() => handleFileRemove('certificates', index)}
                    currentFile={file?.previewUrl}
                    accept={{
                      'image/*': ['.jpeg', '.jpg', '.png', '.gif', '.bmp', '.webp'],
                      'application/pdf': ['.pdf']
                    }}
                    maxSize={10 * 1024 * 1024}
                    label={`Certificate ${index + 1}`}
                    description="Educational or professional certificates"
                    showRemove={!!file}
                  />
                </div>
              ))}
              {uploadedFiles.certificates.length < 10 && (
                <div className="flex items-center justify-center">
                  <Button
                    type="button"
                    variant="outline"
                    onClick={addCertificate}
                    className="h-full min-h-[200px] w-full"
                  >
                    Add Certificate +
                  </Button>
                </div>
              )}
            </div>
          </div>
        </div>

        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h4 className="font-semibold text-blue-900 mb-2">Upload Guidelines</h4>
          <ul className="text-sm text-blue-800 space-y-1">
            <li>• Photos should be clear, recent, and appropriate</li>
            <li>• Maximum file size: 5MB for photos, 10MB for documents</li>
            <li>• Supported formats: JPEG, PNG, GIF, PDF</li>
            <li>• At least one photo is required</li>
            <li>• Files are stored locally in your browser</li>
          </ul>
        </div>

        <div className="flex justify-end space-x-4">
          <Button type="button" variant="outline" onClick={() => dispatch({ type: 'PREVIOUS_STEP' })}>
            ← Back
          </Button>
          <Button type="submit">
            Next: About Me →
          </Button>
        </div>
      </form>
    </div>
  );
};