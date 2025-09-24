import React from 'react';
import { useCV } from '../../../contexts/CVContext';
import { Input } from '../../common/Input';
import { Label } from '../../common/Label';
import { Select, SelectTrigger, SelectValue, SelectContent, SelectItem } from '../../common/Select';
import { Button } from '../../common/Button';
import { marriagePartnerPreferenceSchema } from '../../../validations/marriageSchemas';

export const MarriagePartnerPreferenceStep: React.FC = () => {
  const { state, dispatch } = useCV();
  const [formData, setFormData] = React.useState({
    ageRange: { min: 18, max: 35 },
    heightRange: { min: "5'0\"", max: "6'0\"" },
    maritalStatus: ['never_married'],
    religion: [''],
    education: [''],
    occupation: [''],
    location: [''],
    motherTongue: [''],
    diet: 'vegetarian' as const,
    smoking: 'never' as const,
    drinking: 'never' as const,
    additionalPreferences: '',
  });

  const [errors, setErrors] = React.useState<Record<string, string>>({});

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    try {
      marriagePartnerPreferenceSchema.parse(formData);
      dispatch({
        type: 'UPDATE_MARRIAGE_DATA',
        payload: { partnerPreference: formData }
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

  const handleRangeChange = (field: 'ageRange' | 'heightRange', key: 'min' | 'max', value: string | number) => {
    setFormData(prev => ({
      ...prev,
      [field]: { ...prev[field], [key]: value }
    }));
  };

  const handleArrayChange = (field: string, value: string) => {
    const array = formData[field as keyof typeof formData] as string[];
    const index = array.indexOf(value);
    if (index > -1) {
      array.splice(index, 1);
    } else {
      if (array.length < (field === 'location' ? 20 : 10)) {
        array.push(value);
      }
    }
    setFormData(prev => ({ ...prev, [field]: [...array] }));
  };

  const renderArrayField = (field: string, label: string, options: string[]) => (
    <div>
      <Label>{label}</Label>
      <div className="flex flex-wrap gap-2 mt-2">
        {options.map(option => (
          <label key={option} className="flex items-center">
            <input
              type="checkbox"
              checked={(formData[field as keyof typeof formData] as string[]).includes(option)}
              onChange={() => handleArrayChange(field, option)}
              className="mr-2"
            />
            {option}
          </label>
        ))}
      </div>
    </div>
  );

  const renderArrayInput = (field: string, label: string) => (
    <div>
      <Label>{label}</Label>
      <div className="space-y-2 mt-2">
        {(formData[field as keyof typeof formData] as string[]).map((item, index) => (
          <div key={index} className="flex gap-2">
            <Input
              value={item}
              onChange={(e) => {
                const newArray = [...(formData[field as keyof typeof formData] as string[])];
                newArray[index] = e.target.value;
                setFormData(prev => ({ ...prev, [field]: newArray }));
              }}
              placeholder={`Enter ${label.toLowerCase()}`}
            />
            <Button
              type="button"
              variant="outline"
              onClick={() => {
                const newArray = [...(formData[field as keyof typeof formData] as string[])];
                newArray.splice(index, 1);
                if (newArray.length === 0) {
                  newArray.push('');
                }
                setFormData(prev => ({ ...prev, [field]: newArray }));
              }}
              className="px-3"
            >
              ×
            </Button>
          </div>
        ))}
        <Button
          type="button"
          variant="outline"
          onClick={() => {
            const newArray = [...(formData[field as keyof typeof formData] as string[])];
            if (newArray.length < 10) {
              newArray.push('');
              setFormData(prev => ({ ...prev, [field]: newArray }));
            }
          }}
          className="mt-2"
        >
          Add {label}
        </Button>
      </div>
    </div>
  );

  return (
    <div className="max-w-2xl mx-auto">
      <h2 className="text-2xl font-bold text-gray-900 mb-6">Partner Preference</h2>
      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <Label>Age Range *</Label>
            <div className="flex gap-2 items-center">
              <Input
                type="number"
                value={formData.ageRange.min}
                onChange={(e) => handleRangeChange('ageRange', 'min', parseInt(e.target.value) || 18)}
                placeholder="Min"
                min="18"
                max="80"
              />
              <span>to</span>
              <Input
                type="number"
                value={formData.ageRange.max}
                onChange={(e) => handleRangeChange('ageRange', 'max', parseInt(e.target.value) || 35)}
                placeholder="Max"
                min="18"
                max="80"
              />
            </div>
          </div>

          <div>
            <Label>Height Range *</Label>
            <div className="flex gap-2 items-center">
              <Input
                value={formData.heightRange.min}
                onChange={(e) => handleRangeChange('heightRange', 'min', e.target.value)}
                placeholder="5'0&quot;"
              />
              <span>to</span>
              <Input
                value={formData.heightRange.max}
                onChange={(e) => handleRangeChange('heightRange', 'max', e.target.value)}
                placeholder="6'0&quot;"
              />
            </div>
          </div>

          <div>
            <Label>Marital Status *</Label>
            <div className="space-y-2 mt-2">
              {['never_married', 'divorced', 'widowed'].map(status => (
                <label key={status} className="flex items-center">
                  <input
                    type="checkbox"
                    checked={formData.maritalStatus.includes(status)}
                    onChange={() => handleArrayChange('maritalStatus', status)}
                    className="mr-2"
                  />
                  {status === 'never_married' ? 'Never Married' : status === 'divorced' ? 'Divorced' : 'Widowed'}
                </label>
              ))}
            </div>
          </div>

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
            <Label htmlFor="smoking">Smoking Preference *</Label>
            <Select value={formData.smoking} onValueChange={(value) => handleInputChange('smoking', value)}>
              <SelectTrigger>
                <SelectValue placeholder="Select Smoking Preference" />
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
            <Label htmlFor="drinking">Drinking Preference *</Label>
            <Select value={formData.drinking} onValueChange={(value) => handleInputChange('drinking', value)}>
              <SelectTrigger>
                <SelectValue placeholder="Select Drinking Preference" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="never">Never</SelectItem>
                <SelectItem value="occasionally">Occasionally</SelectItem>
                <SelectItem value="regularly">Regularly</SelectItem>
                <SelectItem value="quit">Quit</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="md:col-span-2">
            {renderArrayInput('religion', 'Religion')}
          </div>

          <div className="md:col-span-2">
            {renderArrayInput('education', 'Education')}
          </div>

          <div className="md:col-span-2">
            {renderArrayInput('occupation', 'Occupation')}
          </div>

          <div className="md:col-span-2">
            {renderArrayInput('location', 'Location')}
          </div>

          <div className="md:col-span-2">
            {renderArrayInput('motherTongue', 'Mother Tongue')}
          </div>

          <div className="md:col-span-2">
            <Label htmlFor="additionalPreferences">Additional Preferences</Label>
            <textarea
              id="additionalPreferences"
              value={formData.additionalPreferences}
              onChange={(e) => handleInputChange('additionalPreferences', e.target.value)}
              placeholder="Any other preferences you'd like to mention..."
              className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              rows={4}
              maxLength={1000}
            />
          </div>
        </div>

        <div className="flex justify-end space-x-4">
          <Button type="button" variant="outline" onClick={() => dispatch({ type: 'PREVIOUS_STEP' })}>
            Back
          </Button>
          <Button type="submit">
            Next: Horoscope Information
          </Button>
        </div>
      </form>
    </div>
  );
};