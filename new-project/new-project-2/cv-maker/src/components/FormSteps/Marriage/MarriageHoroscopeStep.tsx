import React from 'react';
import { useCV } from '../../../contexts/CVContext';
import { Input } from '../../common/Input';
import { Label } from '../../common/Label';
import { Select, SelectTrigger, SelectValue, SelectContent, SelectItem } from '../../common/Select';
import { Button } from '../../common/Button';
import { marriageHoroscopeSchema } from '../../../validations/marriageSchemas';

export const MarriageHoroscopeStep: React.FC = () => {
  const { state, dispatch } = useCV();
  const [formData, setFormData] = React.useState({
    hasHoroscope: false,
    birthTime: '',
    birthPlace: '',
    star: '',
    rashi: '',
    nakshatra: '',
    manglik: 'unknown' as const,
    dosh: [''],
    gotra: '',
    nadi: '',
  });

  const [errors, setErrors] = React.useState<Record<string, string>>({});

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    try {
      marriageHoroscopeSchema.parse(formData);
      dispatch({
        type: 'UPDATE_MARRIAGE_DATA',
        payload: { horoscope: formData }
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

  const handleArrayChange = (field: string, index: number, value: string) => {
    const newArray = [...formData[field as keyof typeof formData]] as string[];
    newArray[index] = value;
    setFormData(prev => ({ ...prev, [field]: newArray }));
  };

  const addArrayItem = (field: string) => {
    const newArray = [...formData[field as keyof typeof formData]] as string[];
    if (newArray.length < 10) {
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

  return (
    <div className="max-w-2xl mx-auto">
      <h2 className="text-2xl font-bold text-gray-900 mb-6">Horoscope Information</h2>
      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <Label htmlFor="hasHoroscope">Horoscope Available</Label>
            <Select
              value={formData.hasHoroscope.toString()}
              onValueChange={(value) => handleInputChange('hasHoroscope', value === 'true')}
            >
              <SelectTrigger>
                <SelectValue placeholder="Select Option" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="false">No Horoscope</SelectItem>
                <SelectItem value="true">Horoscope Available</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div>
            <Label htmlFor="manglik">Manglik Status</Label>
            <Select value={formData.manglik} onValueChange={(value) => handleInputChange('manglik', value)}>
              <SelectTrigger>
                <SelectValue placeholder="Select Manglik Status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="yes">Yes</SelectItem>
                <SelectItem value="no">No</SelectItem>
                <SelectItem value="partial">Partial</SelectItem>
                <SelectItem value="unknown">Unknown</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {formData.hasHoroscope && (
            <>
              <div>
                <Label htmlFor="birthTime">Birth Time</Label>
                <Input
                  id="birthTime"
                  type="time"
                  value={formData.birthTime}
                  onChange={(e) => handleInputChange('birthTime', e.target.value)}
                  placeholder="10:30 AM"
                />
              </div>

              <div>
                <Label htmlFor="birthPlace">Birth Place</Label>
                <Input
                  id="birthPlace"
                  value={formData.birthPlace}
                  onChange={(e) => handleInputChange('birthPlace', e.target.value)}
                  placeholder="City, State, Country"
                />
              </div>

              <div>
                <Label htmlFor="star">Star</Label>
                <Input
                  id="star"
                  value={formData.star}
                  onChange={(e) => handleInputChange('star', e.target.value)}
                  placeholder="e.g., Ashwini, Bharani"
                />
              </div>

              <div>
                <Label htmlFor="rashi">Rashi</Label>
                <Input
                  id="rashi"
                  value={formData.rashi}
                  onChange={(e) => handleInputChange('rashi', e.target.value)}
                  placeholder="e.g., Mesha, Vrishabha"
                />
              </div>

              <div>
                <Label htmlFor="nakshatra">Nakshatra</Label>
                <Input
                  id="nakshatra"
                  value={formData.nakshatra}
                  onChange={(e) => handleInputChange('nakshatra', e.target.value)}
                  placeholder="e.g., Rohini, Krithika"
                />
              </div>

              <div>
                <Label htmlFor="gotra">Gotra</Label>
                <Input
                  id="gotra"
                  value={formData.gotra}
                  onChange={(e) => handleInputChange('gotra', e.target.value)}
                  placeholder="e.g., Kashyap, Bharadwaja"
                />
              </div>

              <div>
                <Label htmlFor="nadi">Nadi</Label>
                <Input
                  id="nadi"
                  value={formData.nadi}
                  onChange={(e) => handleInputChange('nadi', e.target.value)}
                  placeholder="e.g., Aadi, Madhya, Antya"
                />
              </div>

              <div className="md:col-span-2">
                <Label>Dosh Information</Label>
                {formData.dosh.map((item, index) => (
                  <div key={index} className="flex gap-2 mb-2">
                    <Input
                      value={item}
                      onChange={(e) => handleArrayChange('dosh', index, e.target.value)}
                      placeholder="e.g., Manglik, Shani"
                    />
                    {formData.dosh.length > 1 && (
                      <Button
                        type="button"
                        variant="outline"
                        onClick={() => removeArrayItem('dosh', index)}
                        className="px-3"
                      >
                        ×
                      </Button>
                    )}
                  </div>
                ))}
                {formData.dosh.length < 10 && (
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => addArrayItem('dosh')}
                    className="mt-2"
                  >
                    Add Dosh
                  </Button>
                )}
              </div>
            </>
          )}
        </div>

        <div className="flex justify-end space-x-4">
          <Button type="button" variant="outline" onClick={() => dispatch({ type: 'PREVIOUS_STEP' })}>
            Back
          </Button>
          <Button type="submit">
            Next: Photos
          </Button>
        </div>
      </form>
    </div>
  );
};