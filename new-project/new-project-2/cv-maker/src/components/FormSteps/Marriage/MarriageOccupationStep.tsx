import React from 'react';
import { useCV } from '../../../contexts/CVContext';
import { Input } from '../../common/Input';
import { Label } from '../../common/Label';
import { Select } from '../../common/Select';
import { Button } from '../../common/Button';
import { MarriageOccupation } from '../../../types/marriage';

export const MarriageOccupationStep: React.FC = () => {
  const { state, dispatch } = useCV();
  const [occupationList, setOccupationList] = React.useState<MarriageOccupation[]>([]);
  const [formData, setFormData] = React.useState<Omit<MarriageOccupation, 'id'>>({
    employmentType: 'employed',
    occupation: '',
    company: '',
    designation: '',
    industry: '',
    annualIncome: '',
    workExperience: '',
    workLocation: '',
    shift: 'day'
  });

  const [editingId, setEditingId] = React.useState<string | null>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (editingId) {
      // Update existing occupation
      dispatch({
        type: 'UPDATE_MARRIAGE_OCCUPATION',
        payload: { id: editingId, data: formData }
      });
      setEditingId(null);
    } else {
      // Add new occupation
      const newOccupation: MarriageOccupation = {
        ...formData,
        id: Date.now().toString()
      };
      dispatch({
        type: 'ADD_MARRIAGE_OCCUPATION',
        payload: newOccupation
      });
    }

    // Reset form
    setFormData({
      employmentType: 'employed',
      occupation: '',
      company: '',
      designation: '',
      industry: '',
      annualIncome: '',
      workExperience: '',
      workLocation: '',
      shift: 'day'
    });
  };

  const handleEdit = (occupation: MarriageOccupation) => {
    setFormData({
      employmentType: occupation.employmentType,
      occupation: occupation.occupation,
      company: occupation.company || '',
      designation: occupation.designation || '',
      industry: occupation.industry,
      annualIncome: occupation.annualIncome,
      workExperience: occupation.workExperience || '',
      workLocation: occupation.workLocation,
      shift: occupation.shift
    });
    setEditingId(occupation.id);
  };

  const handleDelete = (id: string) => {
    dispatch({ type: 'DELETE_MARRIAGE_OCCUPATION', payload: id });
    if (editingId === id) {
      setEditingId(null);
      setFormData({
        employmentType: 'employed',
        occupation: '',
        company: '',
        designation: '',
        industry: '',
        annualIncome: '',
        workExperience: '',
        workLocation: '',
        shift: 'day'
      });
    }
  };

  const handleInputChange = (field: string, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  return (
    <div className="max-w-4xl mx-auto">
      <h2 className="text-2xl font-bold text-gray-900 mb-6">Occupation Information</h2>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Occupation Form */}
        <div className="bg-white p-6 rounded-lg border border-gray-200">
          <h3 className="text-lg font-semibold mb-4">
            {editingId ? 'Edit Occupation' : 'Add Occupation'}
          </h3>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <Label htmlFor="employmentType">Employment Type *</Label>
              <Select
                id="employmentType"
                value={formData.employmentType}
                onChange={(e) => handleInputChange('employmentType', e.target.value)}
              >
                <option value="employed">Employed</option>
                <option value="self_employed">Self Employed</option>
                <option value="business">Business</option>
                <option value="student">Student</option>
                <option value="unemployed">Unemployed</option>
                <option value="homemaker">Homemaker</option>
              </Select>
            </div>

            <div>
              <Label htmlFor="occupation">Occupation/Profession *</Label>
              <Input
                id="occupation"
                value={formData.occupation}
                onChange={(e) => handleInputChange('occupation', e.target.value)}
                placeholder="e.g., Software Engineer, Doctor, Teacher, etc."
              />
            </div>

            {formData.employmentType === 'employed' && (
              <>
                <div>
                  <Label htmlFor="company">Company/Organization</Label>
                  <Input
                    id="company"
                    value={formData.company}
                    onChange={(e) => handleInputChange('company', e.target.value)}
                    placeholder="Company name"
                  />
                </div>

                <div>
                  <Label htmlFor="designation">Designation/Position</Label>
                  <Input
                    id="designation"
                    value={formData.designation}
                    onChange={(e) => handleInputChange('designation', e.target.value)}
                    placeholder="Job title/position"
                  />
                </div>
              </>
            )}

            <div>
              <Label htmlFor="industry">Industry *</Label>
              <Input
                id="industry"
                value={formData.industry}
                onChange={(e) => handleInputChange('industry', e.target.value)}
                placeholder="e.g., IT, Healthcare, Education, etc."
              />
            </div>

            <div>
              <Label htmlFor="annualIncome">Annual Income *</Label>
              <Input
                id="annualIncome"
                value={formData.annualIncome}
                onChange={(e) => handleInputChange('annualIncome', e.target.value)}
                placeholder="e.g., 6-8 LPA, 10+ LPA, etc."
              />
            </div>

            <div>
              <Label htmlFor="workExperience">Work Experience</Label>
              <Input
                id="workExperience"
                value={formData.workExperience}
                onChange={(e) => handleInputChange('workExperience', e.target.value)}
                placeholder="e.g., 5 years, 2-3 years, etc."
              />
            </div>

            <div>
              <Label htmlFor="workLocation">Work Location *</Label>
              <Input
                id="workLocation"
                value={formData.workLocation}
                onChange={(e) => handleInputChange('workLocation', e.target.value)}
                placeholder="City, State"
              />
            </div>

            {formData.employmentType === 'employed' && (
              <div>
                <Label htmlFor="shift">Work Shift</Label>
                <Select
                  id="shift"
                  value={formData.shift}
                  onChange={(e) => handleInputChange('shift', e.target.value)}
                >
                  <option value="day">Day Shift</option>
                  <option value="night">Night Shift</option>
                  <option value="rotating">Rotating Shift</option>
                  <option value="remote">Remote</option>
                </Select>
              </div>
            )}

            <div className="flex justify-end space-x-4">
              <Button type="button" variant="outline" onClick={() => dispatch({ type: 'PREVIOUS_STEP' })}>
                Back
              </Button>
              <Button type="submit">
                {editingId ? 'Update Occupation' : 'Add Occupation'}
              </Button>
              <Button type="button" onClick={() => dispatch({ type: 'NEXT_STEP' })}>
                Next: Lifestyle
              </Button>
            </div>
          </form>
        </div>

        {/* Occupation List */}
        <div className="bg-white p-6 rounded-lg border border-gray-200">
          <h3 className="text-lg font-semibold mb-4">Occupation History</h3>

          {state.marriageData.occupation.length === 0 ? (
            <p className="text-gray-500 text-center py-8">No occupation details added yet</p>
          ) : (
            <div className="space-y-4">
              {state.marriageData.occupation.map((occupation) => (
                <div key={occupation.id} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex justify-between items-start">
                    <div>
                      <h4 className="font-semibold text-gray-900">{occupation.occupation}</h4>
                      {occupation.company && (
                        <p className="text-gray-600">{occupation.company}</p>
                      )}
                      {occupation.designation && (
                        <p className="text-gray-600">{occupation.designation}</p>
                      )}
                      <p className="text-sm text-gray-500">
                        {occupation.industry} • {occupation.employmentType}
                      </p>
                      <p className="text-sm text-gray-500">
                        Income: {occupation.annualIncome}
                      </p>
                      {occupation.workExperience && (
                        <p className="text-sm text-gray-500">
                          Experience: {occupation.workExperience}
                        </p>
                      )}
                      <p className="text-sm text-gray-500">
                        Location: {occupation.workLocation} • {occupation.shift} shift
                      </p>
                    </div>
                    <div className="flex space-x-2">
                      <Button
                        type="button"
                        variant="outline"
                        size="sm"
                        onClick={() => handleEdit(occupation)}
                      >
                        Edit
                      </Button>
                      <Button
                        type="button"
                        variant="outline"
                        size="sm"
                        onClick={() => handleDelete(occupation.id)}
                      >
                        Delete
                      </Button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};