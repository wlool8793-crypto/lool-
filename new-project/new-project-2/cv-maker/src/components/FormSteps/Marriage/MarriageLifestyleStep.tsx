import React from 'react';
import { useCV } from '../../../contexts/CVContext';
import { Input } from '../../common/Input';
import { Label } from '../../common/Label';
import { Select, SelectTrigger, SelectValue, SelectContent, SelectItem } from '../../common/Select';
import { Button } from '../../common/Button';
import { marriageLifestyleSchema } from '../../../validations/marriageSchemas';

export const MarriageLifestyleStep: React.FC = () => {
  const { state, dispatch } = useCV();
  const [formData, setFormData] = React.useState({
    diet: 'vegetarian' as const,
    smoking: 'never' as const,
    drinking: 'never' as const,
    hobbies: [''],
    interests: [''],
    sports: [''],
    music: [''],
    movies: [''],
    books: [''],
    travel: [''],
    cuisine: [''],
    dressStyle: 'modern' as const,
  });

  const [errors, setErrors] = React.useState<Record<string, string>>({});

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    try {
      marriageLifestyleSchema.parse(formData);
      dispatch({
        type: 'UPDATE_MARRIAGE_DATA',
        payload: { lifestyle: formData }
      });
      dispatch({ type: 'NEXT_STEP' });
    } catch (error) {
      if (error && typeof error === 'object' && 'errors' in error) {
        const fieldErrors: Record<string, string> = {};
        const zodError = error as any;
        if (zodError.errors && Array.isArray(zodError.errors)) {
          zodError.errors.forEach((err: any) => {
            if (err.path && err.path.length > 0) {
              fieldErrors[err.path[0]] = err.message;
            }
          });
        }
        setErrors(fieldErrors);
      } else {
        setErrors({ form: 'Please check all fields and try again' });
      }
    }
  };

  const handleInputChange = (field: string, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }));
    }
  };

  const handleArrayChange = (field: string, index: number, value: string) => {
    const newArray = [...formData[field as keyof typeof formData]] as string[];
    newArray[index] = value;
    setFormData(prev => ({ ...prev, [field]: newArray }));
  };

  const addArrayItem = (field: string) => {
    const newArray = [...formData[field as keyof typeof formData]] as string[];
    if (newArray.length < 20) {
      newArray.push('');
      setFormData(prev => ({ ...prev, [field]: newArray }));
    }
  };

  const removeArrayItem = (field: string, index: number) => {
    const newArray = [...formData[field as keyof typeof formData]] as string[];
    newArray.splice(index, 1);
    if (newArray.length === 0) {
      newArray.push('');
    }
    setFormData(prev => ({ ...prev, [field]: newArray }));
  };

  const renderArrayField = (field: string, label: string, placeholder: string) => (
    <div>
      <Label>{label}</Label>
      {formData[field as keyof typeof formData].map((item: string, index: number) => (
        <div key={index} className="flex gap-2 mb-2">
          <Input
            value={item}
            onChange={(e) => handleArrayChange(field, index, e.target.value)}
            placeholder={placeholder}
          />
          {formData[field as keyof typeof formData].length > 1 && (
            <Button
              type="button"
              variant="outline"
              onClick={() => removeArrayItem(field, index)}
              className="px-3"
            >
              ×
            </Button>
          )}
        </div>
      ))}
      {formData[field as keyof typeof formData].length < 20 && (
        <Button
          type="button"
          variant="outline"
          onClick={() => addArrayItem(field)}
          className="mt-2"
        >
          Add {label}
        </Button>
      )}
    </div>
  );

  return (
    <div className="max-w-2xl mx-auto">
      <h2 className="text-2xl font-bold text-gray-900 mb-6">Lifestyle & Interests</h2>
      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <Label htmlFor="diet">Diet Preference *</Label>
            <Select value={formData.diet} onValueChange={(value) => handleInputChange('diet', value)}>
              <SelectTrigger>
                <SelectValue placeholder="Select Diet Preference" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="vegetarian">Vegetarian</SelectItem>
                <SelectItem value="non_vegetarian">Non-Vegetarian</SelectItem>
                <SelectItem value="eggetarian">Eggetarian</SelectItem>
                <SelectItem value="vegan">Vegan</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div>
            <Label htmlFor="smoking">Smoking Habit *</Label>
            <Select value={formData.smoking} onValueChange={(value) => handleInputChange('smoking', value)}>
              <SelectTrigger>
                <SelectValue placeholder="Select Smoking Habit" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="never">Never</SelectItem>
                <SelectItem value="occasionally">Occasionally</SelectItem>
                <SelectItem value="regularly">Regularly</SelectItem>
                <SelectItem value="quit">Quit</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div>
            <Label htmlFor="drinking">Drinking Habit *</Label>
            <Select value={formData.drinking} onValueChange={(value) => handleInputChange('drinking', value)}>
              <SelectTrigger>
                <SelectValue placeholder="Select Drinking Habit" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="never">Never</SelectItem>
                <SelectItem value="occasionally">Occasionally</SelectItem>
                <SelectItem value="regularly">Regularly</SelectItem>
                <SelectItem value="quit">Quit</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div>
            <Label htmlFor="dressStyle">Dress Style *</Label>
            <Select value={formData.dressStyle} onValueChange={(value) => handleInputChange('dressStyle', value)}>
              <SelectTrigger>
                <SelectValue placeholder="Select Dress Style" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="traditional">Traditional</SelectItem>
                <SelectItem value="western">Western</SelectItem>
                <SelectItem value="modern">Modern</SelectItem>
                <SelectItem value="casual">Casual</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="md:col-span-2">
            {renderArrayField('hobbies', 'Hobbies', 'e.g., Reading, Cooking')}
          </div>

          <div className="md:col-span-2">
            {renderArrayField('interests', 'Interests', 'e.g., Technology, Art')}
          </div>

          <div className="md:col-span-2">
            {renderArrayField('sports', 'Sports', 'e.g., Cricket, Football')}
          </div>

          <div className="md:col-span-2">
            {renderArrayField('music', 'Music Preferences', 'e.g., Classical, Pop')}
          </div>

          <div className="md:col-span-2">
            {renderArrayField('movies', 'Movie Genres', 'e.g., Action, Drama')}
          </div>

          <div className="md:col-span-2">
            {renderArrayField('books', 'Book Genres', 'e.g., Fiction, Non-fiction')}
          </div>

          <div className="md:col-span-2">
            {renderArrayField('travel', 'Travel Destinations', 'e.g., Europe, Asia')}
          </div>

          <div className="md:col-span-2">
            {renderArrayField('cuisine', 'Cuisine Preferences', 'e.g., Italian, Chinese')}
          </div>
        </div>

        <div className="flex justify-end space-x-4">
          <Button type="button" variant="outline" onClick={() => dispatch({ type: 'PREVIOUS_STEP' })}>
            Back
          </Button>
          <Button type="submit">
            Next: Partner Preference
          </Button>
        </div>
      </form>
    </div>
  );
};