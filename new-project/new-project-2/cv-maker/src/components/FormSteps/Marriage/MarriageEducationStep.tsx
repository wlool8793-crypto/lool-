import React from 'react';
import { useCV } from '../../../contexts/CVContext';
import { Input } from '../../common/Input';
import { Label } from '../../common/Label';
import { Select } from '../../common/Select';
import { Button } from '../../common/Button';
import { MarriageEducation } from '../../../types/marriage';

export const MarriageEducationStep: React.FC = () => {
  const { state, dispatch } = useCV();
  const [educationList, setEducationList] = React.useState<MarriageEducation[]>([]);
  const [formData, setFormData] = React.useState<Omit<MarriageEducation, 'id'>>({
    level: 'bachelors',
    degree: '',
    institution: '',
    board: '',
    year: '',
    percentage: '',
    grade: '',
    specialization: ''
  });

  const [editingId, setEditingId] = React.useState<string | null>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (editingId) {
      // Update existing education
      dispatch({
        type: 'UPDATE_MARRIAGE_EDUCATION',
        payload: { id: editingId, data: formData }
      });
      setEditingId(null);
    } else {
      // Add new education
      const newEducation: MarriageEducation = {
        ...formData,
        id: Date.now().toString()
      };
      dispatch({
        type: 'ADD_MARRIAGE_EDUCATION',
        payload: newEducation
      });
    }

    // Reset form
    setFormData({
      level: 'bachelors',
      degree: '',
      institution: '',
      board: '',
      year: '',
      percentage: '',
      grade: '',
      specialization: ''
    });
  };

  const handleEdit = (education: MarriageEducation) => {
    setFormData({
      level: education.level,
      degree: education.degree,
      institution: education.institution,
      board: education.board || '',
      year: education.year,
      percentage: education.percentage || '',
      grade: education.grade || '',
      specialization: education.specialization || ''
    });
    setEditingId(education.id);
  };

  const handleDelete = (id: string) => {
    dispatch({ type: 'DELETE_MARRIAGE_EDUCATION', payload: id });
    if (editingId === id) {
      setEditingId(null);
      setFormData({
        level: 'bachelors',
        degree: '',
        institution: '',
        board: '',
        year: '',
        percentage: '',
        grade: '',
        specialization: ''
      });
    }
  };

  const handleInputChange = (field: string, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  return (
    <div className="max-w-4xl mx-auto">
      <h2 className="text-2xl font-bold text-gray-900 mb-6">Education Information</h2>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Education Form */}
        <div className="bg-white p-6 rounded-lg border border-gray-200">
          <h3 className="text-lg font-semibold mb-4">
            {editingId ? 'Edit Education' : 'Add Education'}
          </h3>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <Label htmlFor="level">Education Level *</Label>
              <Select
                id="level"
                value={formData.level}
                onChange={(e) => handleInputChange('level', e.target.value)}
              >
                <option value="primary">Primary</option>
                <option value="secondary">Secondary</option>
                <option value="higher_secondary">Higher Secondary</option>
                <option value="bachelors">Bachelor's Degree</option>
                <option value="masters">Master's Degree</option>
                <option value="phd">PhD</option>
                <option value="other">Other</option>
              </Select>
            </div>

            <div>
              <Label htmlFor="degree">Degree/Certificate *</Label>
              <Input
                id="degree"
                value={formData.degree}
                onChange={(e) => handleInputChange('degree', e.target.value)}
                placeholder="e.g., B.Tech Computer Science, MBA, etc."
              />
            </div>

            <div>
              <Label htmlFor="institution">Institution *</Label>
              <Input
                id="institution"
                value={formData.institution}
                onChange={(e) => handleInputChange('institution', e.target.value)}
                placeholder="School/College/University name"
              />
            </div>

            {(formData.level === 'secondary' || formData.level === 'higher_secondary') && (
              <div>
                <Label htmlFor="board">Board/University</Label>
                <Input
                  id="board"
                  value={formData.board}
                  onChange={(e) => handleInputChange('board', e.target.value)}
                  placeholder="e.g., CBSE, ICSE, State Board, etc."
                />
              </div>
            )}

            <div>
              <Label htmlFor="year">Year of Completion *</Label>
              <Input
                id="year"
                type="number"
                value={formData.year}
                onChange={(e) => handleInputChange('year', e.target.value)}
                placeholder="2023"
                min="1950"
                max="2030"
              />
            </div>

            <div>
              <Label htmlFor="percentage">Percentage/CGPA</Label>
              <Input
                id="percentage"
                value={formData.percentage}
                onChange={(e) => handleInputChange('percentage', e.target.value)}
                placeholder="e.g., 85%, 8.5 CGPA"
              />
            </div>

            <div>
              <Label htmlFor="grade">Grade/Division</Label>
              <Input
                id="grade"
                value={formData.grade}
                onChange={(e) => handleInputChange('grade', e.target.value)}
                placeholder="e.g., First Class, Distinction, A+"
              />
            </div>

            <div>
              <Label htmlFor="specialization">Specialization</Label>
              <Input
                id="specialization"
                value={formData.specialization}
                onChange={(e) => handleInputChange('specialization', e.target.value)}
                placeholder="e.g., Computer Science, Marketing, etc."
              />
            </div>

            <div className="flex justify-end space-x-4">
              <Button type="button" variant="outline" onClick={() => dispatch({ type: 'PREVIOUS_STEP' })}>
                Back
              </Button>
              <Button type="submit">
                {editingId ? 'Update Education' : 'Add Education'}
              </Button>
              <Button type="button" onClick={() => dispatch({ type: 'NEXT_STEP' })}>
                Next: Occupation
              </Button>
            </div>
          </form>
        </div>

        {/* Education List */}
        <div className="bg-white p-6 rounded-lg border border-gray-200">
          <h3 className="text-lg font-semibold mb-4">Education History</h3>

          {state.marriageData.education.length === 0 ? (
            <p className="text-gray-500 text-center py-8">No education added yet</p>
          ) : (
            <div className="space-y-4">
              {state.marriageData.education.map((education) => (
                <div key={education.id} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex justify-between items-start">
                    <div>
                      <h4 className="font-semibold text-gray-900">{education.degree}</h4>
                      <p className="text-gray-600">{education.institution}</p>
                      <p className="text-sm text-gray-500">
                        {education.year} • {education.level}
                      </p>
                      {education.specialization && (
                        <p className="text-sm text-gray-500">
                          Specialization: {education.specialization}
                        </p>
                      )}
                      {education.percentage && (
                        <p className="text-sm text-gray-500">
                          Score: {education.percentage}
                        </p>
                      )}
                    </div>
                    <div className="flex space-x-2">
                      <Button
                        type="button"
                        variant="outline"
                        size="sm"
                        onClick={() => handleEdit(education)}
                      >
                        Edit
                      </Button>
                      <Button
                        type="button"
                        variant="outline"
                        size="sm"
                        onClick={() => handleDelete(education.id)}
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