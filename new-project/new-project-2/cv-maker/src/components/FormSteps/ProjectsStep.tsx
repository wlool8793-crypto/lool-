import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { useCV } from '@/contexts/CVContext';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/common/Card';
import { Input } from '@/components/common/Input';
import { Label } from '@/components/common/Label';
import { Button } from '@/components/common/Button';
import { FolderOpen, Plus, Trash2, ArrowLeft, ArrowRight, Calendar, ExternalLink } from 'lucide-react';

const projectSchema = z.object({
  title: z.string().min(1, 'Project title is required'),
  description: z.string().min(1, 'Description is required'),
  startDate: z.string().min(1, 'Start date is required'),
  endDate: z.string().optional(),
  url: z.string().url('Invalid URL').optional().or(z.literal('')),
  technologies: z.array(z.string()),
  achievements: z.array(z.string()),
});

type ProjectFormData = z.infer<typeof projectSchema>;

export const ProjectsStep: React.FC = () => {
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
  } = useForm<ProjectFormData>({
    resolver: zodResolver(projectSchema),
    defaultValues: {
      technologies: [''],
      achievements: [''],
    },
  });

  const onSubmit = (data: ProjectFormData) => {
    const project = {
      ...data,
      id: editingId || generateId(),
      technologies: data.technologies.filter(tech => tech.trim() !== ''),
      achievements: data.achievements.filter(achievement => achievement.trim() !== ''),
      url: data.url || undefined,
      endDate: data.endDate || undefined,
    };

    if (editingId) {
      dispatch({ type: 'UPDATE_PROJECT', payload: { id: editingId, data: project } });
    } else {
      dispatch({ type: 'ADD_PROJECT', payload: project });
    }

    reset();
    setIsAdding(false);
    setEditingId(null);
  };

  const handleEdit = (project: typeof state.cvData.projects[0]) => {
    setValue('title', project.title);
    setValue('description', project.description);
    setValue('startDate', project.startDate);
    setValue('endDate', project.endDate || '');
    setValue('url', project.url || '');
    setValue('technologies', project.technologies.length > 0 ? project.technologies : ['']);
    setValue('achievements', project.achievements.length > 0 ? project.achievements : ['']);
    setEditingId(project.id);
    setIsAdding(true);
  };

  const handleDelete = (id: string) => {
    dispatch({ type: 'DELETE_PROJECT', payload: id });
  };

  const handleCancel = () => {
    reset();
    setIsAdding(false);
    setEditingId(null);
  };

  const addTechnology = () => {
    const currentTechs = watch('technologies') || [];
    setValue('technologies', [...currentTechs, '']);
  };

  const removeTechnology = (index: number) => {
    const currentTechs = watch('technologies') || [];
    setValue('technologies', currentTechs.filter((_, i) => i !== index));
  };

  const updateTechnology = (index: number, value: string) => {
    const currentTechs = watch('technologies') || [];
    const newTechs = [...currentTechs];
    newTechs[index] = value;
    setValue('technologies', newTechs);
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
    dispatch({ type: 'SET_CURRENT_STEP', payload: 'skills' });
  };

  const handleNext = () => {
    dispatch({ type: 'SET_CURRENT_STEP', payload: 'certifications' });
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FolderOpen className="h-5 w-5" />
            Projects
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
                Add Project
              </Button>

              {state.cvData.projects.map((project) => (
                <Card key={project.id} className="p-4">
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <h3 className="font-semibold text-lg">{project.title}</h3>
                        {project.url && (
                          <a
                            href={project.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-blue-600 hover:text-blue-800"
                          >
                            <ExternalLink className="h-4 w-4" />
                          </a>
                        )}
                      </div>
                      <p className="text-gray-700 text-sm mb-3">{project.description}</p>
                      <div className="flex items-center gap-2 text-sm text-gray-500 mb-2">
                        <Calendar className="h-4 w-4" />
                        {new Date(project.startDate).toLocaleDateString()}
                        {project.endDate && ` - ${new Date(project.endDate).toLocaleDateString()}`}
                      </div>
                      {project.technologies.length > 0 && (
                        <div className="flex flex-wrap gap-1 mb-2">
                          {project.technologies.map((tech, index) => (
                            <span
                              key={index}
                              className="px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs"
                            >
                              {tech}
                            </span>
                          ))}
                        </div>
                      )}
                      {project.achievements.length > 0 && (
                        <ul className="list-disc list-inside text-sm text-gray-600">
                          {project.achievements.map((achievement, index) => (
                            <li key={index}>{achievement}</li>
                          ))}
                        </ul>
                      )}
                    </div>
                    <div className="flex gap-2">
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handleEdit(project)}
                      >
                        Edit
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handleDelete(project.id)}
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
                  <Label htmlFor="title">Project Title *</Label>
                  <Input
                    id="title"
                    {...register('title')}
                    placeholder="E-commerce Platform"
                    variant={errors.title ? 'error' : 'default'}
                  />
                  {errors.title && (
                    <p className="text-sm text-red-500">{errors.title.message}</p>
                  )}
                </div>

                <div className="space-y-2">
                  <Label htmlFor="url">Project URL (Optional)</Label>
                  <Input
                    id="url"
                    {...register('url')}
                    placeholder="https://github.com/username/project"
                  />
                  {errors.url && (
                    <p className="text-sm text-red-500">{errors.url.message}</p>
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
                  <Label htmlFor="endDate">End Date (Optional)</Label>
                  <Input
                    id="endDate"
                    type="date"
                    {...register('endDate')}
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="description">Project Description *</Label>
                <textarea
                  id="description"
                  {...register('description')}
                  placeholder="Describe what the project does, your role, and the impact..."
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
                  <Label>Technologies Used</Label>
                  <Button
                    type="button"
                    size="sm"
                    variant="outline"
                    onClick={addTechnology}
                  >
                    <Plus className="h-4 w-4 mr-1" />
                    Add
                  </Button>
                </div>
                {watch('technologies')?.map((tech, index) => (
                  <div key={index} className="flex gap-2">
                    <Input
                      placeholder="React, Node.js, MongoDB, etc."
                      value={tech}
                      onChange={(e) => updateTechnology(index, e.target.value)}
                    />
                    {watch('technologies')?.length > 1 && (
                      <Button
                        type="button"
                        size="sm"
                        variant="outline"
                        onClick={() => removeTechnology(index)}
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    )}
                  </div>
                ))}
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
                      placeholder="Describe a key achievement or impact..."
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
                  {editingId ? 'Update Project' : 'Add Project'}
                </Button>
              </div>
            </form>
          )}
        </CardContent>
      </Card>
    </div>
  );
};