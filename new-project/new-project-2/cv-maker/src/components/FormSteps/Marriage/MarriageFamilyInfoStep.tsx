import React from 'react';
import { useCV } from '../../../contexts/CVContext';
import { Input } from '../../common/Input';
import { Label } from '../../common/Label';
import { Select, SelectTrigger, SelectValue, SelectContent, SelectItem } from '../../common/Select';
import { Button } from '../../common/Button';

export const MarriageFamilyInfoStep: React.FC = () => {
  const { state, dispatch } = useCV();
  const [formData, setFormData] = React.useState({
    familyType: 'nuclear' as 'joint' | 'nuclear',
    familyStatus: 'middle_class' as const,
    familyValues: 'moderate' as const,
    fatherName: '',
    fatherOccupation: '',
    fatherStatus: 'alive' as 'alive' | 'deceased',
    motherName: '',
    motherOccupation: '',
    motherStatus: 'alive' as 'alive' | 'deceased',
    brothers: 0,
    marriedBrothers: 0,
    sisters: 0,
    marriedSisters: 0,
    familyLocation: '',
    familyOrigin: '',
    maternalUncle: '',
    parentalProperty: ''
  });

  const [errors, setErrors] = React.useState<Record<string, string>>({});
  const [isSubmitting, setIsSubmitting] = React.useState(false);

  // Debug logging
  React.useEffect(() => {
    console.log('🔍 [FamilyInfo] Component mounted');
    console.log('🔍 [FamilyInfo] Current step:', state.currentStep);
    console.log('🔍 [FamilyInfo] Existing family data:', state.marriageData?.familyInfo);

    // Load existing data if available
    if (state.marriageData?.familyInfo) {
      const existingData = state.marriageData.familyInfo;
      console.log('🔍 [FamilyInfo] Loading existing data:', existingData);
      setFormData(prev => ({
        ...prev,
        ...existingData
      }));
    }
  }, [state.marriageData?.familyInfo, state.currentStep]);

  const handleInputChange = (field: string, value: string | number) => {
    console.log(`🔍 [FamilyInfo] Updating ${field}:`, value);
    setFormData(prev => ({ ...prev, [field]: value }));

    // Clear error when user starts typing
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }));
    }
  };

  const validateForm = (): boolean => {
    console.log('🔍 [FamilyInfo] Starting validation...');
    const newErrors: Record<string, string> = {};

    // Only critical validations - prevent impossible data but allow users to proceed
    // Validation for brothers/sisters logic (prevent impossible data)
    if (formData.marriedBrothers > formData.brothers) {
      newErrors.marriedBrothers = 'Married brothers cannot exceed total brothers';
    }
    if (formData.marriedSisters > formData.sisters) {
      newErrors.marriedSisters = 'Married sisters cannot exceed total sisters';
    }

    // Note: Removed parent occupation validation to allow users to proceed
    // All fields are now optional to prevent navigation blocking

    console.log('🔍 [FamilyInfo] Validation results:', newErrors);
    setErrors(newErrors);

    const isValid = Object.keys(newErrors).length === 0;
    console.log('🔍 [FamilyInfo] Form valid:', isValid);

    return isValid;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    console.log('🚀 [FamilyInfo] === FORM SUBMISSION STARTED ===');
    console.log('🚀 [FamilyInfo] Form data:', formData);

    if (isSubmitting) {
      console.log('🚀 [FamilyInfo] Already submitting, ignoring...');
      return;
    }

    setIsSubmitting(true);

    try {
      // Validate form
      const isValid = validateForm();
      console.log('🚀 [FamilyInfo] Validation result:', isValid);

      if (!isValid) {
        console.log('🚀 [FamilyInfo] Validation failed, stopping navigation');
        setIsSubmitting(false);
        return;
      }

      console.log('🚀 [FamilyInfo] Validation passed, updating context...');

      // Update marriage data
      dispatch({
        type: 'UPDATE_MARRIAGE_DATA',
        payload: { familyInfo: formData }
      });

      console.log('🚀 [FamilyInfo] Context updated, navigating to next step...');

      // Add a small delay to ensure state updates
      await new Promise(resolve => setTimeout(resolve, 100));

      // Navigate to next step
      dispatch({ type: 'NEXT_STEP' });

      console.log('🚀 [FamilyInfo] NEXT_STEP dispatched! Should now go to education step.');

    } catch (error) {
      console.error('❌ [FamilyInfo] Error during submission:', error);
      setErrors({ form: `Navigation error: ${error instanceof Error ? error.message : 'Unknown error'}` });
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleBack = () => {
    console.log('🔙 [FamilyInfo] Going back to previous step');
    dispatch({ type: 'PREVIOUS_STEP' });
  };

  return (
    <div className="max-w-4xl mx-auto">
      <h2 className="text-2xl font-bold text-gray-900 mb-6">Family Information</h2>

      {/* Debug Info Panel */}
      <div className="mb-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
        <h3 className="text-sm font-semibold text-blue-900 mb-2">🔍 Debug Information</h3>
        <div className="text-xs text-blue-800 space-y-1">
          <p>Current Step: {state.currentStep}</p>
          <p>Form Valid: {Object.keys(errors).length === 0 ? '✅ Yes' : '❌ No'}</p>
          <p>Brothers/Sisters Logic: {(formData.marriedBrothers <= formData.brothers && formData.marriedSisters <= formData.sisters) ? '✅ Valid' : '❌ Invalid'}</p>
          <p>Is Submitting: {isSubmitting ? '✅ Yes' : '❌ No'}</p>
          <p>💡 All fields are now optional - click "Next" to proceed</p>
        </div>
      </div>

      {/* Form Level Error */}
      {errors.form && (
        <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-md">
          <p className="text-sm text-red-800">{errors.form}</p>
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Family Type */}
          <div>
            <Label htmlFor="familyType">Family Type *</Label>
            <Select value={formData.familyType} onValueChange={(value) => handleInputChange('familyType', value)}>
              <SelectTrigger>
                <SelectValue placeholder="Select family type" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="joint">Joint Family</SelectItem>
                <SelectItem value="nuclear">Nuclear Family</SelectItem>
              </SelectContent>
            </Select>
            {errors.familyType && (
              <p className="mt-1 text-sm text-red-600">{errors.familyType}</p>
            )}
          </div>

          {/* Family Status */}
          <div>
            <Label htmlFor="familyStatus">Family Status *</Label>
            <Select value={formData.familyStatus} onValueChange={(value) => handleInputChange('familyStatus', value)}>
              <SelectTrigger>
                <SelectValue placeholder="Select family status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="upper_class">Upper Class</SelectItem>
                <SelectItem value="middle_class">Middle Class</SelectItem>
                <SelectItem value="lower_middle_class">Lower Middle Class</SelectItem>
              </SelectContent>
            </Select>
            {errors.familyStatus && (
              <p className="mt-1 text-sm text-red-600">{errors.familyStatus}</p>
            )}
          </div>

          {/* Family Values */}
          <div>
            <Label htmlFor="familyValues">Family Values *</Label>
            <Select value={formData.familyValues} onValueChange={(value) => handleInputChange('familyValues', value)}>
              <SelectTrigger>
                <SelectValue placeholder="Select family values" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="traditional">Traditional</SelectItem>
                <SelectItem value="moderate">Moderate</SelectItem>
                <SelectItem value="liberal">Liberal</SelectItem>
              </SelectContent>
            </Select>
            {errors.familyValues && (
              <p className="mt-1 text-sm text-red-600">{errors.familyValues}</p>
            )}
          </div>

          {/* Father's Name */}
          <div>
            <Label htmlFor="fatherName">Father's Name</Label>
            <Input
              id="fatherName"
              value={formData.fatherName}
              onChange={(e) => handleInputChange('fatherName', e.target.value)}
              placeholder="Father's full name (optional)"
              className={errors.fatherName ? 'border-red-500' : ''}
            />
            {errors.fatherName && (
              <p className="mt-1 text-sm text-red-600">{errors.fatherName}</p>
            )}
          </div>

          {/* Father's Occupation */}
          <div>
            <Label htmlFor="fatherOccupation">Father's Occupation</Label>
            <Input
              id="fatherOccupation"
              value={formData.fatherOccupation}
              onChange={(e) => handleInputChange('fatherOccupation', e.target.value)}
              placeholder="e.g., Businessman, Engineer, Teacher (optional)"
            />
            {errors.fatherOccupation && (
              <p className="mt-1 text-sm text-red-600">{errors.fatherOccupation}</p>
            )}
          </div>

          {/* Father's Status */}
          <div>
            <Label htmlFor="fatherStatus">Father's Status *</Label>
            <Select value={formData.fatherStatus} onValueChange={(value) => handleInputChange('fatherStatus', value)}>
              <SelectTrigger>
                <SelectValue placeholder="Select father's status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="alive">Alive</SelectItem>
                <SelectItem value="deceased">Deceased</SelectItem>
              </SelectContent>
            </Select>
            {errors.fatherStatus && (
              <p className="mt-1 text-sm text-red-600">{errors.fatherStatus}</p>
            )}
          </div>

          {/* Mother's Name */}
          <div>
            <Label htmlFor="motherName">Mother's Name</Label>
            <Input
              id="motherName"
              value={formData.motherName}
              onChange={(e) => handleInputChange('motherName', e.target.value)}
              placeholder="Mother's full name (optional)"
              className={errors.motherName ? 'border-red-500' : ''}
            />
            {errors.motherName && (
              <p className="mt-1 text-sm text-red-600">{errors.motherName}</p>
            )}
          </div>

          {/* Mother's Occupation */}
          <div>
            <Label htmlFor="motherOccupation">Mother's Occupation</Label>
            <Input
              id="motherOccupation"
              value={formData.motherOccupation}
              onChange={(e) => handleInputChange('motherOccupation', e.target.value)}
              placeholder="e.g., Homemaker, Teacher, Doctor (optional)"
            />
            {errors.motherOccupation && (
              <p className="mt-1 text-sm text-red-600">{errors.motherOccupation}</p>
            )}
          </div>

          {/* Mother's Status */}
          <div>
            <Label htmlFor="motherStatus">Mother's Status *</Label>
            <Select value={formData.motherStatus} onValueChange={(value) => handleInputChange('motherStatus', value)}>
              <SelectTrigger>
                <SelectValue placeholder="Select mother's status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="alive">Alive</SelectItem>
                <SelectItem value="deceased">Deceased</SelectItem>
              </SelectContent>
            </Select>
            {errors.motherStatus && (
              <p className="mt-1 text-sm text-red-600">{errors.motherStatus}</p>
            )}
          </div>

          {/* Brothers */}
          <div>
            <Label htmlFor="brothers">Number of Brothers</Label>
            <Input
              id="brothers"
              type="number"
              value={formData.brothers}
              onChange={(e) => handleInputChange('brothers', parseInt(e.target.value) || 0)}
              placeholder="0"
              min="0"
            />
          </div>

          {/* Married Brothers */}
          <div>
            <Label htmlFor="marriedBrothers">Married Brothers</Label>
            <Input
              id="marriedBrothers"
              type="number"
              value={formData.marriedBrothers}
              onChange={(e) => handleInputChange('marriedBrothers', parseInt(e.target.value) || 0)}
              placeholder="0"
              min="0"
              max={formData.brothers}
              className={errors.marriedBrothers ? 'border-red-500' : ''}
            />
            {errors.marriedBrothers && (
              <p className="mt-1 text-sm text-red-600">{errors.marriedBrothers}</p>
            )}
          </div>

          {/* Sisters */}
          <div>
            <Label htmlFor="sisters">Number of Sisters</Label>
            <Input
              id="sisters"
              type="number"
              value={formData.sisters}
              onChange={(e) => handleInputChange('sisters', parseInt(e.target.value) || 0)}
              placeholder="0"
              min="0"
            />
          </div>

          {/* Married Sisters */}
          <div>
            <Label htmlFor="marriedSisters">Married Sisters</Label>
            <Input
              id="marriedSisters"
              type="number"
              value={formData.marriedSisters}
              onChange={(e) => handleInputChange('marriedSisters', parseInt(e.target.value) || 0)}
              placeholder="0"
              min="0"
              max={formData.sisters}
              className={errors.marriedSisters ? 'border-red-500' : ''}
            />
            {errors.marriedSisters && (
              <p className="mt-1 text-sm text-red-600">{errors.marriedSisters}</p>
            )}
          </div>

          {/* Family Location */}
          <div>
            <Label htmlFor="familyLocation">Family Location</Label>
            <Input
              id="familyLocation"
              value={formData.familyLocation}
              onChange={(e) => handleInputChange('familyLocation', e.target.value)}
              placeholder="City, State, Country (optional)"
              className={errors.familyLocation ? 'border-red-500' : ''}
            />
            {errors.familyLocation && (
              <p className="mt-1 text-sm text-red-600">{errors.familyLocation}</p>
            )}
          </div>

          {/* Family Origin */}
          <div>
            <Label htmlFor="familyOrigin">Family Origin</Label>
            <Input
              id="familyOrigin"
              value={formData.familyOrigin}
              onChange={(e) => handleInputChange('familyOrigin', e.target.value)}
              placeholder="Native place or ancestral origin (optional)"
              className={errors.familyOrigin ? 'border-red-500' : ''}
            />
            {errors.familyOrigin && (
              <p className="mt-1 text-sm text-red-600">{errors.familyOrigin}</p>
            )}
          </div>

          {/* Maternal Uncle (Optional) */}
          <div>
            <Label htmlFor="maternalUncle">Maternal Uncle (Optional)</Label>
            <Input
              id="maternalUncle"
              value={formData.maternalUncle}
              onChange={(e) => handleInputChange('maternalUncle', e.target.value)}
              placeholder="Name and details"
            />
          </div>

          {/* Parental Property (Optional) */}
          <div>
            <Label htmlFor="parentalProperty">Parental Property (Optional)</Label>
            <Input
              id="parentalProperty"
              value={formData.parentalProperty}
              onChange={(e) => handleInputChange('parentalProperty', e.target.value)}
              placeholder="e.g., Own house, Agricultural land, etc."
            />
          </div>
        </div>

        {/* Navigation Buttons */}
        <div className="flex justify-between space-x-4 pt-6 border-t">
          <Button
            type="button"
            variant="outline"
            onClick={handleBack}
            disabled={isSubmitting}
          >
            ← Back to Contact
          </Button>

          <Button
            type="submit"
            disabled={isSubmitting}
            className="min-w-[150px]"
          >
            {isSubmitting ? (
              <span className="flex items-center">
                <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Processing...
              </span>
            ) : (
              'Next: Education →'
            )}
          </Button>
        </div>
      </form>
    </div>
  );
};