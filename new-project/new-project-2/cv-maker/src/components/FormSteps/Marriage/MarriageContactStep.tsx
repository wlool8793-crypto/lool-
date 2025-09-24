import React from 'react';
import { useCV } from '../../../contexts/CVContext';
import { Input } from '../../common/Input';
import { Label } from '../../common/Label';
import { Select, SelectTrigger, SelectValue, SelectContent, SelectItem } from '../../common/Select';
import { Button } from '../../common/Button';
import { marriageContactInfoSchema } from '../../../validations/marriageSchemas';

export const MarriageContactStep: React.FC = () => {
  const { state, dispatch } = useCV();
  const [formData, setFormData] = React.useState({
    email: '',
    phone: '',
    whatsapp: '',
    address: '',
    city: '',
    state: '',
    country: '',
    pinCode: '',
    residenceType: 'own' as const,
  });

  const [errors, setErrors] = React.useState<Record<string, string>>({});

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    try {
      marriageContactInfoSchema.parse(formData);
      dispatch({
        type: 'UPDATE_MARRIAGE_DATA',
        payload: { contactInfo: formData }
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

  return (
    <div className="max-w-2xl mx-auto">
      <h2 className="text-2xl font-bold text-gray-900 mb-6">Contact Information</h2>
      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <Label htmlFor="email">Email Address *</Label>
            <Input
              id="email"
              type="email"
              value={formData.email}
              onChange={(e) => handleInputChange('email', e.target.value)}
              placeholder="your.email@example.com"
              error={errors.email}
            />
          </div>

          <div>
            <Label htmlFor="phone">Phone Number *</Label>
            <Input
              id="phone"
              value={formData.phone}
              onChange={(e) => handleInputChange('phone', e.target.value)}
              placeholder="+1 (555) 123-4567"
              error={errors.phone}
            />
          </div>

          <div>
            <Label htmlFor="whatsapp">WhatsApp Number</Label>
            <Input
              id="whatsapp"
              value={formData.whatsapp}
              onChange={(e) => handleInputChange('whatsapp', e.target.value)}
              placeholder="+1 (555) 123-4567"
            />
          </div>

          <div>
            <Label htmlFor="residenceType">Residence Type *</Label>
            <Select value={formData.residenceType} onValueChange={(value) => handleInputChange('residenceType', value)}>
              <SelectTrigger>
                <SelectValue placeholder="Select Residence Type" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="own">Own</SelectItem>
                <SelectItem value="rented">Rented</SelectItem>
                <SelectItem value="family">Family</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="md:col-span-2">
            <Label htmlFor="address">Address *</Label>
            <Input
              id="address"
              value={formData.address}
              onChange={(e) => handleInputChange('address', e.target.value)}
              placeholder="123 Main Street, Apt 4B"
              error={errors.address}
            />
          </div>

          <div>
            <Label htmlFor="city">City *</Label>
            <Input
              id="city"
              value={formData.city}
              onChange={(e) => handleInputChange('city', e.target.value)}
              placeholder="New York"
              error={errors.city}
            />
          </div>

          <div>
            <Label htmlFor="state">State *</Label>
            <Input
              id="state"
              value={formData.state}
              onChange={(e) => handleInputChange('state', e.target.value)}
              placeholder="NY"
              error={errors.state}
            />
          </div>

          <div>
            <Label htmlFor="country">Country *</Label>
            <Input
              id="country"
              value={formData.country}
              onChange={(e) => handleInputChange('country', e.target.value)}
              placeholder="United States"
              error={errors.country}
            />
          </div>

          <div>
            <Label htmlFor="pinCode">PIN Code *</Label>
            <Input
              id="pinCode"
              value={formData.pinCode}
              onChange={(e) => handleInputChange('pinCode', e.target.value)}
              placeholder="100001"
              error={errors.pinCode}
            />
          </div>
        </div>

        <div className="flex justify-end space-x-4">
          <Button type="button" variant="outline" onClick={() => dispatch({ type: 'PREVIOUS_STEP' })}>
            Back
          </Button>
          <Button type="submit">
            Next: Family Information
          </Button>
        </div>
      </form>
    </div>
  );
};