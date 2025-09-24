import React from 'react';
import { useCV } from '../../../contexts/CVContext';
import { Input } from '../../common/Input';
import { Label } from '../../common/Label';
import { Select, SelectTrigger, SelectValue, SelectContent, SelectItem } from '../../common/Select';
import { Button } from '../../common/Button';
import { marriagePersonalInfoSchema } from '../../../validations/marriageSchemas';

export const MarriagePersonalInfoStep: React.FC = () => {
  const { state, dispatch } = useCV();
  const [formData, setFormData] = React.useState({
    fullName: '',
    age: 25,
    gender: 'male' as 'male' | 'female',
    dateOfBirth: '',
    birthPlace: '',
    height: '',
    weight: '',
    bloodGroup: '',
    complexion: 'fair' as const,
    bodyType: 'average' as const,
    maritalStatus: 'never_married' as const,
    children: 0,
    disability: '',
    nationality: '',
    religion: '',
    caste: '',
    subCaste: '',
    motherTongue: '',
    languages: [{ name: '', proficiency: 'native' as const, canRead: true, canWrite: true }]
  });

  const [errors, setErrors] = React.useState<Record<string, string>>({});

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    try {
      marriagePersonalInfoSchema.parse(formData);
      dispatch({
        type: 'UPDATE_MARRIAGE_DATA',
        payload: { personalInfo: formData }
      });
      dispatch({ type: 'NEXT_STEP' });
    } catch (error) {
      if (error && typeof error === 'object' && 'errors' in error) {
        // Convert ZodError to field errors
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
        // Generic error
        setErrors({ form: 'Please check all fields and try again' });
      }
    }
  };

  const handleInputChange = (field: string, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    // Clear error when user starts typing
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }));
    }
  };

  return (
    <div className="max-w-2xl mx-auto">
      <h2 className="text-2xl font-bold text-gray-900 mb-6">Personal Information</h2>
      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <Label htmlFor="fullName">Full Name *</Label>
            <Input
              id="fullName"
              value={formData.fullName}
              onChange={(e) => handleInputChange('fullName', e.target.value)}
              placeholder="Enter your full name"
              error={errors.fullName}
            />
          </div>

          <div>
            <Label htmlFor="age">Age *</Label>
            <Input
              id="age"
              type="number"
              value={formData.age}
              onChange={(e) => handleInputChange('age', parseInt(e.target.value) || 0)}
              placeholder="25"
              error={errors.age}
            />
          </div>

          <div>
            <Label htmlFor="gender">Gender *</Label>
            <Select value={formData.gender} onValueChange={(value) => handleInputChange('gender', value)}>
              <SelectTrigger>
                <SelectValue placeholder="Select Gender" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="male">Male</SelectItem>
                <SelectItem value="female">Female</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div>
            <Label htmlFor="dateOfBirth">Date of Birth *</Label>
            <Input
              id="dateOfBirth"
              type="date"
              value={formData.dateOfBirth}
              onChange={(e) => handleInputChange('dateOfBirth', e.target.value)}
              error={errors.dateOfBirth}
            />
          </div>

          <div>
            <Label htmlFor="height">Height *</Label>
            <Input
              id="height"
              value={formData.height}
              onChange={(e) => handleInputChange('height', e.target.value)}
              placeholder="5'10&quot; or 178 cm"
              error={errors.height}
            />
          </div>

          <div>
            <Label htmlFor="weight">Weight *</Label>
            <Input
              id="weight"
              value={formData.weight}
              onChange={(e) => handleInputChange('weight', e.target.value)}
              placeholder="70 kg or 154 lbs"
              error={errors.weight}
            />
          </div>

          <div>
            <Label htmlFor="bloodGroup">Blood Group *</Label>
            <Select value={formData.bloodGroup} onValueChange={(value) => handleInputChange('bloodGroup', value)}>
              <SelectTrigger>
                <SelectValue placeholder="Select Blood Group" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="A+">A+</SelectItem>
                <SelectItem value="A-">A-</SelectItem>
                <SelectItem value="B+">B+</SelectItem>
                <SelectItem value="B-">B-</SelectItem>
                <SelectItem value="AB+">AB+</SelectItem>
                <SelectItem value="AB-">AB-</SelectItem>
                <SelectItem value="O+">O+</SelectItem>
                <SelectItem value="O-">O-</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div>
            <Label htmlFor="complexion">Complexion *</Label>
            <Select value={formData.complexion} onValueChange={(value) => handleInputChange('complexion', value)}>
              <SelectTrigger>
                <SelectValue placeholder="Select Complexion" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="very_fair">Very Fair</SelectItem>
                <SelectItem value="fair">Fair</SelectItem>
                <SelectItem value="wheatish">Wheatish</SelectItem>
                <SelectItem value="olive">Olive</SelectItem>
                <SelectItem value="dark">Dark</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div>
            <Label htmlFor="bodyType">Body Type *</Label>
            <Select value={formData.bodyType} onValueChange={(value) => handleInputChange('bodyType', value)}>
              <SelectTrigger>
                <SelectValue placeholder="Select Body Type" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="slim">Slim</SelectItem>
                <SelectItem value="average">Average</SelectItem>
                <SelectItem value="athletic">Athletic</SelectItem>
                <SelectItem value="heavy">Heavy</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div>
            <Label htmlFor="maritalStatus">Marital Status *</Label>
            <Select value={formData.maritalStatus} onValueChange={(value) => handleInputChange('maritalStatus', value)}>
              <SelectTrigger>
                <SelectValue placeholder="Select Marital Status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="never_married">Never Married</SelectItem>
                <SelectItem value="divorced">Divorced</SelectItem>
                <SelectItem value="widowed">Widowed</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div>
            <Label htmlFor="nationality">Nationality *</Label>
            <Input
              id="nationality"
              value={formData.nationality}
              onChange={(e) => handleInputChange('nationality', e.target.value)}
              placeholder="e.g., Indian, American"
              error={errors.nationality}
            />
          </div>

          <div>
            <Label htmlFor="religion">Religion *</Label>
            <Input
              id="religion"
              value={formData.religion}
              onChange={(e) => handleInputChange('religion', e.target.value)}
              placeholder="e.g., Hindu, Muslim, Christian"
              error={errors.religion}
            />
          </div>

          <div>
            <Label htmlFor="caste">Caste</Label>
            <Input
              id="caste"
              value={formData.caste}
              onChange={(e) => handleInputChange('caste', e.target.value)}
              placeholder="Optional"
            />
          </div>

          <div>
            <Label htmlFor="motherTongue">Mother Tongue *</Label>
            <Input
              id="motherTongue"
              value={formData.motherTongue}
              onChange={(e) => handleInputChange('motherTongue', e.target.value)}
              placeholder="e.g., Hindi, English, Tamil"
              error={errors.motherTongue}
            />
          </div>
        </div>

        <div className="flex justify-end space-x-4">
          <Button type="button" variant="outline" onClick={() => window.history.back()}>
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