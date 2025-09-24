import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { useCV } from '@/contexts/CVContext';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/common/Card';
import { Input } from '@/components/common/Input';
import { Label } from '@/components/common/Label';
import { Button } from '@/components/common/Button';
import { Languages, Plus, Trash2, ArrowLeft, ArrowRight } from 'lucide-react';

const languageSchema = z.object({
  name: z.string().min(1, 'Language name is required'),
  proficiency: z.enum(['native', 'fluent', 'conversational', 'basic']),
  certification: z.string().optional(),
});

type LanguageFormData = z.infer<typeof languageSchema>;

const proficiencyLevels = [
  { value: 'native', label: 'Native' },
  { value: 'fluent', label: 'Fluent' },
  { value: 'conversational', label: 'Conversational' },
  { value: 'basic', label: 'Basic' },
];

const getProficiencyColor = (proficiency: string) => {
  switch (proficiency) {
    case 'native':
      return 'bg-green-100 text-green-800';
    case 'fluent':
      return 'bg-blue-100 text-blue-800';
    case 'conversational':
      return 'bg-yellow-100 text-yellow-800';
    case 'basic':
      return 'bg-gray-100 text-gray-800';
    default:
      return 'bg-gray-100 text-gray-800';
  }
};

export const LanguagesStep: React.FC = () => {
  const { state, dispatch, generateId } = useCV();
  const [isAdding, setIsAdding] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<LanguageFormData>({
    resolver: zodResolver(languageSchema),
    defaultValues: {
      proficiency: 'conversational',
    },
  });

  const onSubmit = (data: LanguageFormData) => {
    const language = {
      ...data,
      id: editingId || generateId(),
      certification: data.certification || undefined,
    };

    if (editingId) {
      dispatch({ type: 'UPDATE_LANGUAGE', payload: { id: editingId, data: language } });
    } else {
      dispatch({ type: 'ADD_LANGUAGE', payload: language });
    }

    reset();
    setIsAdding(false);
    setEditingId(null);
  };

  const handleEdit = (language: typeof state.cvData.languages[0]) => {
    reset({
      name: language.name,
      proficiency: language.proficiency,
      certification: language.certification || '',
    });
    setEditingId(language.id);
    setIsAdding(true);
  };

  const handleDelete = (id: string) => {
    dispatch({ type: 'DELETE_LANGUAGE', payload: id });
  };

  const handleCancel = () => {
    reset();
    setIsAdding(false);
    setEditingId(null);
  };

  const handlePrevious = () => {
    dispatch({ type: 'SET_CURRENT_STEP', payload: 'certifications' });
  };

  const handleNext = () => {
    dispatch({ type: 'SET_CURRENT_STEP', payload: 'preview' });
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Languages className="h-5 w-5" />
            Languages
          </CardTitle>
        </CardHeader>
        <CardContent>
          {!isAdding ? (
            <div className="space-y-6">
              <Button
                onClick={() => setIsAdding(true)}
                className="w-full"
                variant="outline"
              >
                <Plus className="h-4 w-4 mr-2" />
                Add Language
              </Button>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {state.cvData.languages.map((language) => (
                  <Card key={language.id} className="p-4">
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <h3 className="font-semibold text-lg">{language.name}</h3>
                        <div className="flex items-center gap-2 mt-2">
                          <span className={`px-2 py-1 rounded text-xs ${getProficiencyColor(language.proficiency)}`}>
                            {language.proficiency}
                          </span>
                        </div>
                        {language.certification && (
                          <p className="text-sm text-gray-600 mt-2">{language.certification}</p>
                        )}
                      </div>
                      <div className="flex gap-1">
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleEdit(language)}
                        >
                          Edit
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleDelete(language.id)}
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  </Card>
                ))}
              </div>

              {state.cvData.languages.length === 0 && (
                <div className="text-center py-8 text-gray-500">
                  <Languages className="h-12 w-12 mx-auto mb-4 opacity-50" />
                  <p>No languages added yet. Click "Add Language" to get started.</p>
                </div>
              )}

              <div className="flex justify-between pt-4">
                <Button type="button" variant="outline" onClick={handlePrevious}>
                  <ArrowLeft className="h-4 w-4 mr-2" />
                  Previous
                </Button>
                <Button type="button" onClick={handleNext}>
                  Preview CV
                  <ArrowRight className="h-4 w-4 ml-2" />
                </Button>
              </div>
            </div>
          ) : (
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="name">Language *</Label>
                  <Input
                    id="name"
                    {...register('name')}
                    placeholder="English, Spanish, French, etc."
                    variant={errors.name ? 'error' : 'default'}
                  />
                  {errors.name && (
                    <p className="text-sm text-red-500">{errors.name.message}</p>
                  )}
                </div>

                <div className="space-y-2">
                  <Label htmlFor="proficiency">Proficiency Level *</Label>
                  <select
                    id="proficiency"
                    {...register('proficiency')}
                    className="flex h-10 w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-sm ring-offset-white placeholder:text-gray-500 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                  >
                    {proficiencyLevels.map((level) => (
                      <option key={level.value} value={level.value}>
                        {level.label}
                      </option>
                    ))}
                  </select>
                  {errors.proficiency && (
                    <p className="text-sm text-red-500">{errors.proficiency.message}</p>
                  )}
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="certification">Certification (Optional)</Label>
                <Input
                  id="certification"
                  {...register('certification')}
                  placeholder="TOEFL 110, DELE B2, DELF B2, etc."
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
                  {editingId ? 'Update Language' : 'Add Language'}
                </Button>
              </div>
            </form>
          )}
        </CardContent>
      </Card>
    </div>
  );
};