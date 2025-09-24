import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { useCV } from '@/contexts/CVContext';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/common/Card';
import { Input } from '@/components/common/Input';
import { Label } from '@/components/common/Label';
import { Button } from '@/components/common/Button';
import { Award, Plus, Trash2, ArrowLeft, ArrowRight, Calendar } from 'lucide-react';

const certificationSchema = z.object({
  name: z.string().min(1, 'Certification name is required'),
  issuer: z.string().min(1, 'Issuer is required'),
  issueDate: z.string().min(1, 'Issue date is required'),
  expiryDate: z.string().optional(),
  credentialId: z.string().optional(),
  url: z.string().url('Invalid URL').optional().or(z.literal('')),
});

type CertificationFormData = z.infer<typeof certificationSchema>;

export const CertificationsStep: React.FC = () => {
  const { state, dispatch, generateId } = useCV();
  const [isAdding, setIsAdding] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
    setValue,
    watch,
  } = useForm<CertificationFormData>({
    resolver: zodResolver(certificationSchema),
  });

  const onSubmit = (data: CertificationFormData) => {
    const certification = {
      ...data,
      id: editingId || generateId(),
      expiryDate: data.expiryDate || undefined,
      credentialId: data.credentialId || undefined,
      url: data.url || undefined,
    };

    if (editingId) {
      dispatch({ type: 'UPDATE_CERTIFICATION', payload: { id: editingId, data: certification } });
    } else {
      dispatch({ type: 'ADD_CERTIFICATION', payload: certification });
    }

    reset();
    setIsAdding(false);
    setEditingId(null);
  };

  const handleEdit = (certification: typeof state.cvData.certifications[0]) => {
    setValue('name', certification.name);
    setValue('issuer', certification.issuer);
    setValue('issueDate', certification.issueDate);
    setValue('expiryDate', certification.expiryDate || '');
    setValue('credentialId', certification.credentialId || '');
    setValue('url', certification.url || '');
    setEditingId(certification.id);
    setIsAdding(true);
  };

  const handleDelete = (id: string) => {
    dispatch({ type: 'DELETE_CERTIFICATION', payload: id });
  };

  const handleCancel = () => {
    reset();
    setIsAdding(false);
    setEditingId(null);
  };

  const handlePrevious = () => {
    dispatch({ type: 'SET_CURRENT_STEP', payload: 'projects' });
  };

  const handleNext = () => {
    dispatch({ type: 'SET_CURRENT_STEP', payload: 'languages' });
  };

  const isExpired = (expiryDate: string) => {
    return new Date(expiryDate) < new Date();
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Award className="h-5 w-5" />
            Certifications
          </CardTitle>
        </CardHeader>
        <CardContent>
          {!isAdding ? (
            <div className="space-y-4">
              <Button
                onClick={() => setIsAdding(true)}
                className="w-full"
                variant="outline"
              >
                <Plus className="h-4 w-4 mr-2" />
                Add Certification
              </Button>

              {state.cvData.certifications.map((certification) => (
                <Card key={certification.id} className="p-4">
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <h3 className="font-semibold text-lg">{certification.name}</h3>
                      <p className="text-gray-600">{certification.issuer}</p>
                      <div className="flex items-center gap-2 text-sm text-gray-500 mt-1">
                        <Calendar className="h-4 w-4" />
                        Issued: {new Date(certification.issueDate).toLocaleDateString()}
                        {certification.expiryDate && (
                          <span className={isExpired(certification.expiryDate) ? 'text-red-600' : ''}>
                            • Expires: {new Date(certification.expiryDate).toLocaleDateString()}
                            {isExpired(certification.expiryDate) && ' (Expired)'}
                          </span>
                        )}
                      </div>
                      {certification.credentialId && (
                        <p className="text-sm text-gray-600 mt-1">
                          Credential ID: {certification.credentialId}
                        </p>
                      )}
                      {certification.url && (
                        <a
                          href={certification.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-blue-600 hover:text-blue-800 text-sm mt-1 inline-block"
                        >
                          View Credential
                        </a>
                      )}
                    </div>
                    <div className="flex gap-2">
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handleEdit(certification)}
                      >
                        Edit
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handleDelete(certification.id)}
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                </Card>
              ))}

              {state.cvData.certifications.length === 0 && (
                <div className="text-center py-8 text-gray-500">
                  <Award className="h-12 w-12 mx-auto mb-4 opacity-50" />
                  <p>No certifications added yet. Click "Add Certification" to get started.</p>
                </div>
              )}

              <div className="flex justify-between pt-4">
                <Button type="button" variant="outline" onClick={handlePrevious}>
                  <ArrowLeft className="h-4 w-4 mr-2" />
                  Previous
                </Button>
                <Button type="button" onClick={handleNext}>
                  Next Step
                  <ArrowRight className="h-4 w-4 ml-2" />
                </Button>
              </div>
            </div>
          ) : (
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="name">Certification Name *</Label>
                  <Input
                    id="name"
                    {...register('name')}
                    placeholder="AWS Certified Developer Associate"
                    variant={errors.name ? 'error' : 'default'}
                  />
                  {errors.name && (
                    <p className="text-sm text-red-500">{errors.name.message}</p>
                  )}
                </div>

                <div className="space-y-2">
                  <Label htmlFor="issuer">Issuer *</Label>
                  <Input
                    id="issuer"
                    {...register('issuer')}
                    placeholder="Amazon Web Services"
                    variant={errors.issuer ? 'error' : 'default'}
                  />
                  {errors.issuer && (
                    <p className="text-sm text-red-500">{errors.issuer.message}</p>
                  )}
                </div>

                <div className="space-y-2">
                  <Label htmlFor="issueDate">Issue Date *</Label>
                  <Input
                    id="issueDate"
                    type="date"
                    {...register('issueDate')}
                    variant={errors.issueDate ? 'error' : 'default'}
                  />
                  {errors.issueDate && (
                    <p className="text-sm text-red-500">{errors.issueDate.message}</p>
                  )}
                </div>

                <div className="space-y-2">
                  <Label htmlFor="expiryDate">Expiry Date (Optional)</Label>
                  <Input
                    id="expiryDate"
                    type="date"
                    {...register('expiryDate')}
                    min={watch('issueDate')}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="credentialId">Credential ID (Optional)</Label>
                  <Input
                    id="credentialId"
                    {...register('credentialId')}
                    placeholder="AWS-ASA-12345678"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="url">Credential URL (Optional)</Label>
                  <Input
                    id="url"
                    {...register('url')}
                    placeholder="https://aws.amazon.com/certification/cert-id"
                  />
                  {errors.url && (
                    <p className="text-sm text-red-500">{errors.url.message}</p>
                  )}
                </div>
              </div>

              <div className="flex justify-between pt-4">
                <div className="flex gap-2">
                  <Button type="button" variant="outline" onClick={handleCancel}>
                    Cancel
                  </Button>
                  <Button type="button" variant="outline" onClick={handlePrevious}>
                    <ArrowLeft className="h-4 w-4 mr-2" />
                    Previous
                  </Button>
                </div>
                <Button type="submit">
                  {editingId ? 'Update Certification' : 'Add Certification'}
                </Button>
              </div>
            </form>
          )}
        </CardContent>
      </Card>
    </div>
  );
};