import React from 'react';
import { useCV } from '../../../contexts/CVContext';
import { Label } from '../../common/Label';
import { Button } from '../../common/Button';
import { marriageAboutSchema } from '../../../validations/marriageSchemas';

export const MarriageAboutStep: React.FC = () => {
  const { state, dispatch } = useCV();
  const [formData, setFormData] = React.useState({
    aboutMe: '',
    expectations: '',
  });

  const [errors, setErrors] = React.useState<Record<string, string>>({});

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    try {
      marriageAboutSchema.parse(formData);
      dispatch({
        type: 'UPDATE_MARRIAGE_DATA',
        payload: {
          aboutMe: formData.aboutMe,
          expectations: formData.expectations
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

  const handleInputChange = (field: string, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }));
    }
  };

  return (
    <div className="max-w-2xl mx-auto">
      <h2 className="text-2xl font-bold text-gray-900 mb-6">About Me & Expectations</h2>
      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="space-y-6">
          <div>
            <Label htmlFor="aboutMe">About Me *</Label>
            <div className="mt-1">
              <textarea
                id="aboutMe"
                value={formData.aboutMe}
                onChange={(e) => handleInputChange('aboutMe', e.target.value)}
                placeholder="Tell us about yourself, your personality, values, interests, and what makes you unique..."
                className="w-full p-4 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                rows={8}
                minLength={10}
                maxLength={2000}
              />
              <div className="mt-1 text-sm text-gray-500">
                {formData.aboutMe.length}/2000 characters (minimum 10 characters)
              </div>
              {errors.aboutMe && (
                <p className="mt-1 text-sm text-red-600">{errors.aboutMe}</p>
              )}
            </div>
          </div>

          <div>
            <Label htmlFor="expectations">What I'm Looking For *</Label>
            <div className="mt-1">
              <textarea
                id="expectations"
                value={formData.expectations}
                onChange={(e) => handleInputChange('expectations', e.target.value)}
                placeholder="Describe what you're looking for in a partner, your expectations from marriage, family values, and long-term goals..."
                className="w-full p-4 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                rows={8}
                minLength={10}
                maxLength={2000}
              />
              <div className="mt-1 text-sm text-gray-500">
                {formData.expectations.length}/2000 characters (minimum 10 characters)
              </div>
              {errors.expectations && (
                <p className="mt-1 text-sm text-red-600">{errors.expectations}</p>
              )}
            </div>
          </div>

          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h3 className="text-lg font-semibold text-blue-900 mb-2">Tips for Writing a Great Profile</h3>
            <ul className="text-sm text-blue-800 space-y-1">
              <li>• Be honest and authentic in your description</li>
              <li>• Highlight your positive qualities and achievements</li>
              <li>• Share your hobbies, interests, and passions</li>
              <li>• Be specific about what you're looking for in a partner</li>
              <li>• Mention your family values and cultural background</li>
              <li>• Keep your language positive and respectful</li>
              <li>• Check for spelling and grammar mistakes</li>
            </ul>
          </div>
        </div>

        <div className="flex justify-end space-x-4">
          <Button type="button" variant="outline" onClick={() => dispatch({ type: 'PREVIOUS_STEP' })}>
            Back
          </Button>
          <Button type="submit">
            Next: Preview
          </Button>
        </div>
      </form>
    </div>
  );
};