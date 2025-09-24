import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { useCV } from '@/contexts/CVContext';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/common/Card';
import { Input } from '@/components/common/Input';
import { Label } from '@/components/common/Label';
import { Button } from '@/components/common/Button';
import { Briefcase, Plus, Trash2, ArrowLeft, ArrowRight, Calendar } from 'lucide-react';

const experienceSchema = z.object({
  company: z.string().min(1, 'Company name is required'),
  position: z.string().min(1, 'Position is required'),
  startDate: z.string().min(1, 'Start date is required'),
  endDate: z.string().min(1, 'End date is required'),
  current: z.boolean(),
  description: z.string().min(1, 'Description is required'),
  achievements: z.array(z.string()),
});

type ExperienceFormData = z.infer<typeof experienceSchema>;

export const ExperienceStep: React.FC = () => {
  const { state, dispatch, generateId } = useCV();
  const [isAdding, setIsAdding] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
    watch,
    setValue,
  } = useForm<ExperienceFormData>({
    resolver: zodResolver(experienceSchema),
    defaultValues: {
      achievements: [''],
      current: false,
    },
  });

  const isCurrent = watch('current');

  const onSubmit = (data: ExperienceFormData) => {
    const experience = {
      ...data,
      id: editingId || generateId(),
      achievements: data.achievements.filter(achievement => achievement.trim() !== ''),
    };

    if (editingId) {
      dispatch({ type: 'UPDATE_WORK_EXPERIENCE', payload: { id: editingId, data: experience } });
    } else {
      dispatch({ type: 'ADD_WORK_EXPERIENCE', payload: experience });
    }

    reset();
    setIsAdding(false);
    setEditingId(null);
  };

  const handleEdit = (experience: typeof state.cvData.workExperience[0]) => {
    setValue('company', experience.company);
    setValue('position', experience.position);
    setValue('startDate', experience.startDate);
    setValue('endDate', experience.endDate);
    setValue('current', experience.current);
    setValue('description', experience.description);
    setValue('achievements', experience.achievements.length > 0 ? experience.achievements : ['']);
    setEditingId(experience.id);
    setIsAdding(true);
  };

  const handleDelete = (id: string) => {
    dispatch({ type: 'DELETE_WORK_EXPERIENCE', payload: id });
  };

  const handleCancel = () => {
    reset();
    setIsAdding(false);
    setEditingId(null);
  };

  const addAchievement = () => {
    const currentAchievements = watch('achievements') || [];
    setValue('achievements', [...currentAchievements, '']);
  };

  const removeAchievement = (index: number) => {
    const currentAchievements = watch('achievements') || [];
    setValue('achievements', currentAchievements.filter((_, i) => i !== index));
  };

  const updateAchievement = (index: number, value: string) => {
    const currentAchievements = watch('achievements') || [];
    const newAchievements = [...currentAchievements];
    newAchievements[index] = value;
    setValue('achievements', newAchievements);
  };

  const handlePrevious = () => {
    dispatch({ type: 'SET_CURRENT_STEP', payload: 'summary' });
  };

  const handleNext = () => {
    dispatch({ type: 'SET_CURRENT_STEP', payload: 'education' });
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Briefcase className="h-5 w-5" />
            Work Experience
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
                Add Work Experience
              </Button>

              {state.cvData.workExperience.map((experience) => (
                <Card key={experience.id} className="p-4">
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <h3 className="font-semibold text-lg">{experience.position}</h3>
                      <p className="text-gray-600">{experience.company}</p>
                      <div className="flex items-center gap-2 text-sm text-gray-500 mt-1">
                        <Calendar className="h-4 w-4" />
                        {new Date(experience.startDate).toLocaleDateString()} -{' '}
                        {experience.current ? 'Present' : new Date(experience.endDate).toLocaleDateString()}
                      </div>
                      <p className="text-gray-700 mt-2 text-sm">{experience.description}</p>
                      {experience.achievements.length > 0 && (
                        <ul className="list-disc list-inside mt-2 text-sm text-gray-600">
                          {experience.achievements.map((achievement, index) => (
                            <li key={index}>{achievement}</li>
                          ))}
                        </ul>
                      )}
                    </div>
                    <div className="flex gap-2">
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handleEdit(experience)}
                      >
                        Edit
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handleDelete(experience.id)}
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
                  <Label htmlFor="company">Company *</Label>
                  <Input
                    id="company"
                    {...register('company')}
                    placeholder="Tech Corp Inc."
                    variant={errors.company ? 'error' : 'default'}
                  />
                  {errors.company && (
                    <p className="text-sm text-red-500">{errors.company.message}</p>
                  )}
                </div>

                <div className="space-y-2">
                  <Label htmlFor="position">Position *</Label>
                  <Input
                    id="position"
                    {...register('position')}
                    placeholder="Software Engineer"
                    variant={errors.position ? 'error' : 'default'}
                  />
                  {errors.position && (
                    <p className="text-sm text-red-500">{errors.position.message}</p>
                  )}
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
                    disabled={isCurrent}
                    variant={errors.endDate ? 'error' : 'default'}
                  />
                  {errors.endDate && (
                    <p className="text-sm text-red-500">{errors.endDate.message}</p>
                  )}
                </div>
              </div>

              <div className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  id="current"
                  {...register('current')}
                  onChange={(e) => {
                    setValue('current', e.target.checked);
                    if (e.target.checked) {
                      setValue('endDate', '');
                    }
                  }}
                  className="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                />
                <Label htmlFor="current">I currently work here</Label>
              </div>

              <div className="space-y-2">
                <Label htmlFor="description">Job Description *</Label>
                <textarea
                  id="description"
                  {...register('description')}
                  placeholder="Describe your role and responsibilities..."
                  className={`flex min-h-[80px] w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-sm ring-offset-white placeholder:text-gray-500 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 ${
                    errors.description ? 'border-red-500 focus-visible:ring-red-500' : ''
                  }`}
                  rows={3}
                />
                {errors.description && (
                  <p className="text-sm text-red-500">{errors.description.message}</p>
                )}
              </div>

              <div className="space-y-2">
                <div className="flex justify-between items-center">
                  <Label>Key Achievements</Label>
                  <Button
                    type="button"
                    size="sm"
                    variant="outline"
                    onClick={addAchievement}
                  >
                    <Plus className="h-4 w-4 mr-1" />
                    Add
                  </Button>
                </div>
                {watch('achievements')?.map((achievement, index) => (
                  <div key={index} className="flex gap-2">
                    <Input
                      placeholder="Describe a key achievement..."
                      value={achievement}
                      onChange={(e) => updateAchievement(index, e.target.value)}
                    />
                    {watch('achievements')?.length > 1 && (
                      <Button
                        type="button"
                        size="sm"
                        variant="outline"
                        onClick={() => removeAchievement(index)}
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    )}
                  </div>
                ))}
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
                  {editingId ? 'Update Experience' : 'Add Experience'}
                </Button>
              </div>
            </form>
          )}
        </CardContent>
      </Card>
    </div>
  );
};