import React from 'react';
import { useForm, useFieldArray } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { useCV } from '@/contexts/CVContext';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/common/Card';
import { Input } from '@/components/common/Input';
import { Label } from '@/components/common/Label';
import { Button } from '@/components/common/Button';
import { Textarea } from '@/components/common/Textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/common/Select';
import { Badge } from '@/components/common/Badge';
import {
  Heart,
  Calendar,
  MapPin,
  Clock,
  Plus,
  Trash2,
  ChevronUp,
  ChevronDown,
  Award,
  Users
} from 'lucide-react';
import { volunteerExperienceSchema, type VolunteerExperienceFormData } from '@/validations';

const VolunteerExperienceForm: React.FC<{
  experience: VolunteerExperienceFormData;
  onUpdate: (data: Partial<VolunteerExperienceFormData>) => void;
  onRemove: () => void;
  canRemove: boolean;
}> = ({ experience, onUpdate, onRemove, canRemove }) => {
  const [isExpanded, setIsExpanded] = React.useState(true);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setIsExpanded(!isExpanded);
  };

  return (
    <Card className="mb-4">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Heart className="h-5 w-5 text-red-500" />
            <CardTitle className="text-lg">
              {experience.organization || 'New Volunteer Experience'}
            </CardTitle>
            {experience.current && (
              <Badge variant="secondary">Current</Badge>
            )}
          </div>
          <div className="flex items-center gap-2">
            <Button
              type="button"
              variant="ghost"
              size="sm"
              onClick={handleSubmit}
            >
              {isExpanded ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
            </Button>
            {canRemove && (
              <Button
                type="button"
                variant="ghost"
                size="sm"
                onClick={onRemove}
                className="text-red-500 hover:text-red-700"
              >
                <Trash2 className="h-4 w-4" />
              </Button>
            )}
          </div>
        </div>
      </CardHeader>

      {isExpanded && (
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor={`organization-${experience.id}`}>Organization *</Label>
              <Input
                id={`organization-${experience.id}`}
                value={experience.organization}
                onChange={(e) => onUpdate({ organization: e.target.value })}
                placeholder="Red Cross, UNICEF, etc."
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor={`position-${experience.id}`}>Position/Role *</Label>
              <Input
                id={`position-${experience.id}`}
                value={experience.position}
                onChange={(e) => onUpdate({ position: e.target.value })}
                placeholder="Volunteer, Coordinator, etc."
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor={`startDate-${experience.id}`}>Start Date *</Label>
              <Input
                id={`startDate-${experience.id}`}
                type="month"
                value={experience.startDate}
                onChange={(e) => onUpdate({ startDate: e.target.value })}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor={`endDate-${experience.id}`}>End Date {!experience.current && '*'}</Label>
              <Input
                id={`endDate-${experience.id}`}
                type="month"
                value={experience.endDate}
                onChange={(e) => onUpdate({ endDate: e.target.value })}
                disabled={experience.current}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor={`cause-${experience.id}`}>Cause/Area *</Label>
              <Input
                id={`cause-${experience.id}`}
                value={experience.cause}
                onChange={(e) => onUpdate({ cause: e.target.value })}
                placeholder="Education, Environment, Healthcare, etc."
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor={`hoursPerWeek-${experience.id}`}>Hours per Week</Label>
              <Input
                id={`hoursPerWeek-${experience.id}`}
                type="number"
                min="1"
                max="80"
                value={experience.hoursPerWeek || ''}
                onChange={(e) => onUpdate({ hoursPerWeek: parseInt(e.target.value) || undefined })}
                placeholder="10"
              />
            </div>

            <div className="space-y-2 md:col-span-2">
              <Label htmlFor={`location-${experience.id}`}>Location *</Label>
              <Input
                id={`location-${experience.id}`}
                value={experience.location}
                onChange={(e) => onUpdate({ location: e.target.value })}
                placeholder="City, State/Country"
              />
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor={`description-${experience.id}`}>Description *</Label>
            <Textarea
              id={`description-${experience.id}`}
              value={experience.description}
              onChange={(e) => onUpdate({ description: e.target.value })}
              placeholder="Describe your volunteer work and responsibilities..."
              rows={3}
            />
          </div>

          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              id={`current-${experience.id}`}
              checked={experience.current}
              onChange={(e) => {
                onUpdate({ current: e.target.checked });
                if (e.target.checked) {
                  onUpdate({ endDate: '' });
                }
              }}
              className="h-4 w-4 rounded border-gray-300"
            />
            <Label htmlFor={`current-${experience.id}`}>I currently volunteer here</Label>
          </div>

          <DynamicFieldArray
            title="Key Achievements"
            items={experience.achievements}
            onAdd={(item) => onUpdate({
              achievements: [...experience.achievements, item]
            })}
            onUpdate={(index, item) => {
              const newAchievements = [...experience.achievements];
              newAchievements[index] = item;
              onUpdate({ achievements: newAchievements });
            }}
            onRemove={(index) => {
              const newAchievements = experience.achievements.filter((_, i) => i !== index);
              onUpdate({ achievements: newAchievements });
            }}
            placeholder="Describe a key achievement or impact..."
            icon={<Award className="h-4 w-4" />}
          />
        </CardContent>
      )}
    </Card>
  );
};

const DynamicFieldArray: React.FC<{
  title: string;
  items: string[];
  onAdd: (item: string) => void;
  onUpdate: (index: number, item: string) => void;
  onRemove: (index: number) => void;
  placeholder: string;
  icon?: React.ReactNode;
}> = ({ title, items, onAdd, onUpdate, onRemove, placeholder, icon }) => {
  const [newItem, setNewItem] = React.useState('');

  const handleAdd = () => {
    if (newItem.trim()) {
      onAdd(newItem.trim());
      setNewItem('');
    }
  };

  return (
    <div className="space-y-2">
      <Label className="text-sm font-medium">{title}</Label>
      <div className="space-y-2">
        {items.map((item, index) => (
          <div key={index} className="flex gap-2">
            <Input
              value={item}
              onChange={(e) => onUpdate(index, e.target.value)}
              placeholder={placeholder}
              className="flex-1"
            />
            <Button
              type="button"
              variant="ghost"
              size="sm"
              onClick={() => onRemove(index)}
              className="text-red-500 hover:text-red-700"
            >
              <Trash2 className="h-4 w-4" />
            </Button>
          </div>
        ))}

        <div className="flex gap-2">
          <Input
            value={newItem}
            onChange={(e) => setNewItem(e.target.value)}
            placeholder={placeholder}
            onKeyPress={(e) => e.key === 'Enter' && handleAdd()}
            className="flex-1"
          />
          <Button
            type="button"
            variant="outline"
            size="sm"
            onClick={handleAdd}
          >
            <Plus className="h-4 w-4 mr-1" />
            Add
          </Button>
        </div>
      </div>
    </div>
  );
};

export const VolunteerStep: React.FC = () => {
  const { state, dispatch, generateId } = useCV();
  const {
    control,
    handleSubmit,
    formState: { errors },
    watch,
  } = useForm({
    defaultValues: {
      volunteerExperience: state.cvData.volunteerExperience,
    },
    resolver: zodResolver(z.object({ volunteerExperience: z.array(volunteerExperienceSchema) })),
  });

  const { fields, append, remove } = useFieldArray({
    control,
    name: 'volunteerExperience',
  });

  const onSubmit = (data: { volunteerExperience: VolunteerExperienceFormData[] }) => {
    data.volunteerExperience.forEach(exp => {
      const existingIndex = state.cvData.volunteerExperience.findIndex(e => e.id === exp.id);
      if (existingIndex >= 0) {
        dispatch({ type: 'UPDATE_VOLUNTEER_EXPERIENCE', payload: { id: exp.id, data: exp } });
      } else {
        dispatch({ type: 'ADD_VOLUNTEER_EXPERIENCE', payload: { ...exp, id: generateId() } });
      }
    });

    // Remove deleted experiences
    state.cvData.volunteerExperience.forEach(existing => {
      if (!data.volunteerExperience.find(exp => exp.id === existing.id)) {
        dispatch({ type: 'DELETE_VOLUNTEER_EXPERIENCE', payload: existing.id });
      }
    });

    dispatch({ type: 'SET_CURRENT_STEP', payload: 'awards' });
  };

  const handlePrevious = () => {
    dispatch({ type: 'SET_CURRENT_STEP', payload: 'languages' });
  };

  const addNewExperience = () => {
    append({
      id: generateId(),
      organization: '',
      position: '',
      startDate: '',
      endDate: '',
      current: false,
      description: '',
      achievements: [],
      cause: '',
      hoursPerWeek: undefined,
      location: '',
    });
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Heart className="h-6 w-6 text-red-500" />
            Volunteer Experience
          </CardTitle>
          <p className="text-gray-600">
            Showcase your volunteer work and community involvement
          </p>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            {fields.map((field, index) => (
              <VolunteerExperienceForm
                key={field.id}
                experience={watch(`volunteerExperience.${index}`)}
                onUpdate={(data) => {
                  const currentExperience = watch(`volunteerExperience.${index}`);
                  const updatedExperience = { ...currentExperience, ...data };
                  // Update form array
                  const newValue = [...watch('volunteerExperience')];
                  newValue[index] = updatedExperience;
                  // This will trigger re-render
                }}
                onRemove={() => remove(index)}
                canRemove={fields.length > 1}
              />
            ))}

            <div className="flex gap-4">
              <Button
                type="button"
                variant="outline"
                onClick={addNewExperience}
                className="flex items-center gap-2"
              >
                <Plus className="h-4 w-4" />
                Add Volunteer Experience
              </Button>
            </div>

            <div className="flex justify-between pt-6 border-t">
              <Button type="button" variant="outline" onClick={handlePrevious}>
                Previous
              </Button>
              <Button type="submit">
                Next: Awards & Achievements
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
};