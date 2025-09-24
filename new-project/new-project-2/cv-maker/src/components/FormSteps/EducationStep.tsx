import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { useCV } from '@/contexts/CVContext';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/common/Card';
import { Input } from '@/components/common/Input';
import { Label } from '@/components/common/Label';
import { Button } from '@/components/common/Button';
import { GraduationCap, Plus, Trash2, ArrowLeft, ArrowRight, Calendar } from 'lucide-react';

const educationSchema = z.object({
  institution: z.string().min(1, 'Institution name is required'),
  degree: z.string().min(1, 'Degree is required'),
  field: z.string().min(1, 'Field of study is required'),
  startDate: z.string().min(1, 'Start date is required'),
  endDate: z.string().min(1, 'End date is required'),
  gpa: z.string().optional(),
  honors: z.string().optional(),
});

type EducationFormData = z.infer<typeof educationSchema>;

export const EducationStep: React.FC = () => {
  const { state, dispatch, generateId } = useCV();
  const [isAdding, setIsAdding] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<EducationFormData>({
    resolver: zodResolver(educationSchema),
  });

  const onSubmit = (data: EducationFormData) => {
    const education = {
      ...data,
      id: editingId || generateId(),
      gpa: data.gpa || undefined,
      honors: data.honors || undefined,
    };

    if (editingId) {
      dispatch({ type: 'UPDATE_EDUCATION', payload: { id: editingId, data: education } });
    } else {
      dispatch({ type: 'ADD_EDUCATION', payload: education });
    }

    reset();
    setIsAdding(false);
    setEditingId(null);
  };

  const handleEdit = (education: typeof state.cvData.education[0]) => {
    reset({
      institution: education.institution,
      degree: education.degree,
      field: education.field,
      startDate: education.startDate,
      endDate: education.endDate,
      gpa: education.gpa || '',
      honors: education.honors || '',
    });
    setEditingId(education.id);
    setIsAdding(true);
  };

  const handleDelete = (id: string) => {
    dispatch({ type: 'DELETE_EDUCATION', payload: id });
  };

  const handleCancel = () => {
    reset();
    setIsAdding(false);
    setEditingId(null);
  };

  const handlePrevious = () => {
    dispatch({ type: 'SET_CURRENT_STEP', payload: 'experience' });
  };

  const handleNext = () => {
    dispatch({ type: 'SET_CURRENT_STEP', payload: 'skills' });
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <GraduationCap className="h-5 w-5" />
            Education
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
                Add Education
              </Button>

              {state.cvData.education.map((education) => (
                <Card key={education.id} className="p-4">
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <h3 className="font-semibold text-lg">{education.degree} in {education.field}</h3>
                      <p className="text-gray-600">{education.institution}</p>
                      <div className="flex items-center gap-2 text-sm text-gray-500 mt-1">
                        <Calendar className="h-4 w-4" />
                        {new Date(education.startDate).toLocaleDateString()} -{' '}
                        {new Date(education.endDate).toLocaleDateString()}
                      </div>
                      {education.gpa && (
                        <p className="text-sm text-gray-600 mt-1">GPA: {education.gpa}</p>
                      )}
                      {education.honors && (
                        <p className="text-sm text-gray-600 mt-1">{education.honors}</p>
                      )}
                    </div>
                    <div className="flex gap-2">
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handleEdit(education)}
                      >
                        Edit
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handleDelete(education.id)}
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                </Card>
              ))}

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
                  <Label htmlFor="institution">Institution *</Label>
                  <Input
                    id="institution"
                    {...register('institution')}
                    placeholder="University of Technology"
                    variant={errors.institution ? 'error' : 'default'}
                  />
                  {errors.institution && (
                    <p className="text-sm text-red-500">{errors.institution.message}</p>
                  )}
                </div>

                <div className="space-y-2">
                  <Label htmlFor="degree">Degree *</Label>
                  <Input
                    id="degree"
                    {...register('degree')}
                    placeholder="Bachelor of Science"
                    variant={errors.degree ? 'error' : 'default'}
                  />
                  {errors.degree && (
                    <p className="text-sm text-red-500">{errors.degree.message}</p>
                  )}
                </div>

                <div className="space-y-2">
                  <Label htmlFor="field">Field of Study *</Label>
                  <Input
                    id="field"
                    {...register('field')}
                    placeholder="Computer Science"
                    variant={errors.field ? 'error' : 'default'}
                  />
                  {errors.field && (
                    <p className="text-sm text-red-500">{errors.field.message}</p>
                  )}
                </div>

                <div className="space-y-2">
                  <Label htmlFor="gpa">GPA (Optional)</Label>
                  <Input
                    id="gpa"
                    {...register('gpa')}
                    placeholder="3.8"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="startDate">Start Date *</Label>
                  <Input
                    id="startDate"
                    type="date"
                    {...register('startDate')}
                    variant={errors.startDate ? 'error' : 'default'}
                  />
                  {errors.startDate && (
                    <p className="text-sm text-red-500">{errors.startDate.message}</p>
                  )}
                </div>

                <div className="space-y-2">
                  <Label htmlFor="endDate">End Date *</Label>
                  <Input
                    id="endDate"
                    type="date"
                    {...register('endDate')}
                    variant={errors.endDate ? 'error' : 'default'}
                  />
                  {errors.endDate && (
                    <p className="text-sm text-red-500">{errors.endDate.message}</p>
                  )}
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="honors">Honors/Awards (Optional)</Label>
                <Input
                  id="honors"
                  {...register('honors')}
                  placeholder="Magna Cum Laude, Dean's List, etc."
                />
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
                  {editingId ? 'Update Education' : 'Add Education'}
                </Button>
              </div>
            </form>
          )}
        </CardContent>
      </Card>
    </div>
  );
};