import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { useCV } from '@/contexts/CVContext';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/common/Card';
import { Input } from '@/components/common/Input';
import { Label } from '@/components/common/Label';
import { Button } from '@/components/common/Button';
import { Wrench, Plus, Trash2, ArrowLeft, ArrowRight } from 'lucide-react';

const skillSchema = z.object({
  name: z.string().min(1, 'Skill name is required'),
  category: z.enum(['technical', 'soft', 'language']),
  level: z.enum(['beginner', 'intermediate', 'advanced', 'expert']),
});

type SkillFormData = z.infer<typeof skillSchema>;

const skillCategories = [
  { value: 'technical', label: 'Technical' },
  { value: 'soft', label: 'Soft Skills' },
  { value: 'language', label: 'Language' },
];

const skillLevels = [
  { value: 'beginner', label: 'Beginner' },
  { value: 'intermediate', label: 'Intermediate' },
  { value: 'advanced', label: 'Advanced' },
  { value: 'expert', label: 'Expert' },
];

export const SkillsStep: React.FC = () => {
  const { state, dispatch, generateId } = useCV();
  const [isAdding, setIsAdding] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<SkillFormData>({
    resolver: zodResolver(skillSchema),
    defaultValues: {
      category: 'technical',
      level: 'intermediate',
    },
  });

  const onSubmit = (data: SkillFormData) => {
    const skill = {
      ...data,
      id: editingId || generateId(),
    };

    if (editingId) {
      dispatch({ type: 'UPDATE_SKILL', payload: { id: editingId, data: skill } });
    } else {
      dispatch({ type: 'ADD_SKILL', payload: skill });
    }

    reset();
    setIsAdding(false);
    setEditingId(null);
  };

  const handleEdit = (skill: typeof state.cvData.skills[0]) => {
    reset({
      name: skill.name,
      category: skill.category,
      level: skill.level,
    });
    setEditingId(skill.id);
    setIsAdding(true);
  };

  const handleDelete = (id: string) => {
    dispatch({ type: 'DELETE_SKILL', payload: id });
  };

  const handleCancel = () => {
    reset();
    setIsAdding(false);
    setEditingId(null);
  };

  const handlePrevious = () => {
    dispatch({ type: 'SET_CURRENT_STEP', payload: 'education' });
  };

  const handleNext = () => {
    dispatch({ type: 'SET_CURRENT_STEP', payload: 'projects' });
  };

  const skillsByCategory = state.cvData.skills.reduce((acc, skill) => {
    if (!acc[skill.category]) {
      acc[skill.category] = [];
    }
    acc[skill.category].push(skill);
    return acc;
  }, {} as Record<string, typeof state.cvData.skills>);

  const getLevelColor = (level: string) => {
    switch (level) {
      case 'beginner':
        return 'bg-green-100 text-green-800';
      case 'intermediate':
        return 'bg-blue-100 text-blue-800';
      case 'advanced':
        return 'bg-purple-100 text-purple-800';
      case 'expert':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Wrench className="h-5 w-5" />
            Skills
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
                Add Skill
              </Button>

              {Object.entries(skillsByCategory).map(([category, skills]) => (
                <div key={category} className="space-y-3">
                  <h3 className="text-lg font-semibold text-gray-800 border-b pb-2">
                    {skillCategories.find(c => c.value === category)?.label || category}
                  </h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                    {skills.map((skill) => (
                      <Card key={skill.id} className="p-3">
                        <div className="flex justify-between items-start">
                          <div className="flex-1">
                            <h4 className="font-medium">{skill.name}</h4>
                            <span className={`mt-1 px-2 py-1 rounded text-xs ${getLevelColor(skill.level)}`}>
                              {skillLevels.find(l => l.value === skill.level)?.label || skill.level}
                            </span>
                          </div>
                          <div className="flex gap-1">
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => handleEdit(skill)}
                            >
                              Edit
                            </Button>
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => handleDelete(skill.id)}
                            >
                              <Trash2 className="h-4 w-4" />
                            </Button>
                          </div>
                        </div>
                      </Card>
                    ))}
                  </div>
                </div>
              ))}

              {state.cvData.skills.length === 0 && (
                <div className="text-center py-8 text-gray-500">
                  <Wrench className="h-12 w-12 mx-auto mb-4 opacity-50" />
                  <p>No skills added yet. Click "Add Skill" to get started.</p>
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
                  <Label htmlFor="name">Skill Name *</Label>
                  <Input
                    id="name"
                    {...register('name')}
                    placeholder="React, JavaScript, Project Management, etc."
                    variant={errors.name ? 'error' : 'default'}
                  />
                  {errors.name && (
                    <p className="text-sm text-red-500">{errors.name.message}</p>
                  )}
                </div>

                <div className="space-y-2">
                  <Label htmlFor="category">Category *</Label>
                  <select
                    id="category"
                    {...register('category')}
                    className={`flex h-10 w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-sm ring-offset-white placeholder:text-gray-500 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 ${
                      errors.category ? 'border-red-500 focus-visible:ring-red-500' : ''
                    }`}
                  >
                    <option value="">Select a category</option>
                    {skillCategories.map((category) => (
                      <option key={category.value} value={category.value}>
                        {category.label}
                      </option>
                    ))}
                  </select>
                  {errors.category && (
                    <p className="text-sm text-red-500">{errors.category.message}</p>
                  )}
                </div>

                <div className="space-y-2">
                  <Label htmlFor="level">Proficiency Level *</Label>
                  <select
                    id="level"
                    {...register('level')}
                    className="flex h-10 w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-sm ring-offset-white placeholder:text-gray-500 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                  >
                    {skillLevels.map((level) => (
                      <option key={level.value} value={level.value}>
                        {level.label}
                      </option>
                    ))}
                  </select>
                  {errors.level && (
                    <p className="text-sm text-red-500">{errors.level.message}</p>
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
                  {editingId ? 'Update Skill' : 'Add Skill'}
                </Button>
              </div>
            </form>
          )}
        </CardContent>
      </Card>
    </div>
  );
};