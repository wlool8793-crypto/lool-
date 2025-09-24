import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Users, Heart, MapPin, BookOpen, Utensils, Church, Star, Settings } from 'lucide-react';
import { Button } from '../ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Input } from '../ui/Input';
import { cn } from '../lib/utils';

interface CommunityData {
  religion: string;
  caste: string;
  subCaste: string;
  sect: string;
  motherTongue: string;
  culturalPractices: string[];
  religiousLevel: string;
  dietaryPreferences: string;
  familyBackground: string;
  communityLocation: string;
  traditionalValues: string[];
  festivalPreferences: string[];
  dressPreferences: string;
}

interface CommunityFeaturesProps {
  data: Partial<CommunityData>;
  onChange: (data: CommunityData) => void;
  className?: string;
}

const religions = [
  'Hinduism', 'Islam', 'Christianity', 'Sikhism', 'Buddhism', 'Jainism', 'Zoroastrianism', 'Other'
];

const hinduSects = [
  'Vaishnavism', 'Shaivism', 'Shaktism', 'Smartism', 'Arya Samaj', 'Brahmo Samaj', 'Other'
];

const muslimSects = [
  'Sunni', 'Shia', 'Sufi', 'Ahmadiyya', 'Other'
];

const christianDenominations = [
  'Catholic', 'Protestant', 'Orthodox', 'Anglican', 'Pentecostal', 'Other'
];

const sikhSects = [
  'Khalsa', 'Namdhari', 'Nirankari', 'Other'
];

const dietaryOptions = [
  'Vegetarian', 'Non-Vegetarian', 'Eggetarian', 'Vegan', 'Jain Vegetarian', 'Halal', 'Kosher'
];

const culturalPractices = [
  'Daily Prayers', 'Temple/Mosque/Church Visits', 'Fasting', 'Religious Festivals',
  'Yoga/Meditation', 'Charity/Donations', 'Community Service', 'Religious Education'
];

const traditionalValues = [
  'Family-oriented', 'Career-oriented', 'Education-focused', 'Traditional',
  'Modern/Progressive', 'Spiritual', 'Community-minded', 'Balanced'
];

const festivals = [
  'Diwali', 'Holi', 'Eid', 'Christmas', 'Gurupurab', 'Navratri', 'Durga Puja',
  'Ramadan', 'Easter', 'Pongal', 'Baisakhi', 'Other'
];

const dressStyles = [
  'Traditional', 'Modern', 'Mix of Both', 'Cultural Occasions Only', 'Conservative', 'Liberal'
];

export const CommunityFeatures: React.FC<CommunityFeaturesProps> = ({
  data,
  onChange,
  className = ''
}) => {
  const { t } = useTranslation();
  const [selectedSects, setSelectedSects] = useState<string[]>([]);
  const [selectedPractices, setSelectedPractices] = useState<string[]>([]);
  const [selectedValues, setSelectedValues] = useState<string[]>([]);
  const [selectedFestivals, setSelectedFestivals] = useState<string[]>([]);

  const handleReligionChange = (religion: string) => {
    setSelectedSects([]);
    onChange({
      ...data,
      religion,
      sect: ''
    });
  };

  const toggleSelection = (value: string, selected: string[], setSelected: React.Dispatch<React.SetStateAction<string[]>>) => {
    setSelected(prev =>
      prev.includes(value)
        ? prev.filter(item => item !== value)
        : [...prev, value]
    );
  };

  const getAvailableSects = () => {
    switch (data.religion) {
      case 'Hinduism': return hinduSects;
      case 'Islam': return muslimSects;
      case 'Christianity': return christianDenominations;
      case 'Sikhism': return sikhSects;
      default: return [];
    }
  };

  return (
    <div className={cn('space-y-6', className)}>
      {/* Religious Information */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Church className="h-5 w-5" />
            Religious & Community Information
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1">
                Religion
              </label>
              <select
                value={data.religion || ''}
                onChange={(e) => handleReligionChange(e.target.value)}
                className="w-full p-2 border border-gray-300 rounded-md focus:ring-primary focus:border-primary"
              >
                <option value="">Select Religion</option>
                {religions.map((religion) => (
                  <option key={religion} value={religion}>{religion}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">
                Sect/Denomination
              </label>
              <select
                value={data.sect || ''}
                onChange={(e) => onChange({ ...data, sect: e.target.value })}
                className="w-full p-2 border border-gray-300 rounded-md focus:ring-primary focus:border-primary"
                disabled={!data.religion}
              >
                <option value="">Select Sect</option>
                {getAvailableSects().map((sect) => (
                  <option key={sect} value={sect}>{sect}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">
                Caste
              </label>
              <Input
                type="text"
                value={data.caste || ''}
                onChange={(e) => onChange({ ...data, caste: e.target.value })}
                placeholder="Enter caste (optional)"
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">
                Sub-caste
              </label>
              <Input
                type="text"
                value={data.subCaste || ''}
                onChange={(e) => onChange({ ...data, subCaste: e.target.value })}
                placeholder="Enter sub-caste (optional)"
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Cultural Practices */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BookOpen className="h-5 w-5" />
            Cultural Practices
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {culturalPractices.map((practice) => (
              <label
                key={practice}
                className={cn(
                  'flex items-center p-3 border-2 rounded-lg cursor-pointer transition-all',
                  selectedPractices.includes(practice)
                    ? 'border-primary bg-primary/10'
                    : 'border-gray-200 hover:border-gray-300'
                )}
              >
                <input
                  type="checkbox"
                  checked={selectedPractices.includes(practice)}
                  onChange={() => toggleSelection(practice, selectedPractices, setSelectedPractices)}
                  className="mr-2"
                />
                <span className="text-sm">{practice}</span>
              </label>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Dietary Preferences */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Utensils className="h-5 w-5" />
            Dietary Preferences
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {dietaryOptions.map((option) => (
              <label
                key={option}
                className={cn(
                  'flex items-center p-3 border-2 rounded-lg cursor-pointer transition-all',
                  data.dietaryPreferences === option
                    ? 'border-primary bg-primary/10'
                    : 'border-gray-200 hover:border-gray-300'
                )}
              >
                <input
                  type="radio"
                  name="dietaryPreferences"
                  checked={data.dietaryPreferences === option}
                  onChange={() => onChange({ ...data, dietaryPreferences: option })}
                  className="mr-2"
                />
                <span className="text-sm">{option}</span>
              </label>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Traditional Values */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Heart className="h-5 w-5" />
            Traditional Values
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {traditionalValues.map((value) => (
              <label
                key={value}
                className={cn(
                  'flex items-center p-3 border-2 rounded-lg cursor-pointer transition-all',
                  selectedValues.includes(value)
                    ? 'border-primary bg-primary/10'
                    : 'border-gray-200 hover:border-gray-300'
                )}
              >
                <input
                  type="checkbox"
                  checked={selectedValues.includes(value)}
                  onChange={() => toggleSelection(value, selectedValues, setSelectedValues)}
                  className="mr-2"
                />
                <span className="text-sm">{value}</span>
              </label>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Festival Preferences */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Star className="h-5 w-5" />
            Festival Preferences
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {festivals.map((festival) => (
              <label
                key={festival}
                className={cn(
                  'flex items-center p-3 border-2 rounded-lg cursor-pointer transition-all',
                  selectedFestivals.includes(festival)
                    ? 'border-primary bg-primary/10'
                    : 'border-gray-200 hover:border-gray-300'
                )}
              >
                <input
                  type="checkbox"
                  checked={selectedFestivals.includes(festival)}
                  onChange={() => toggleSelection(festival, selectedFestivals, setSelectedFestivals)}
                  className="mr-2"
                />
                <span className="text-sm">{festival}</span>
              </label>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Dress Preferences */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Settings className="h-5 w-5" />
            Dress Style Preferences
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
            {dressStyles.map((style) => (
              <label
                key={style}
                className={cn(
                  'flex items-center p-3 border-2 rounded-lg cursor-pointer transition-all',
                  data.dressPreferences === style
                    ? 'border-primary bg-primary/10'
                    : 'border-gray-200 hover:border-gray-300'
                )}
              >
                <input
                  type="radio"
                  name="dressPreferences"
                  checked={data.dressPreferences === style}
                  onChange={() => onChange({ ...data, dressPreferences: style })}
                  className="mr-2"
                />
                <span className="text-sm">{style}</span>
              </label>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Community Location */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <MapPin className="h-5 w-5" />
            Community Background
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1">
              Community Location
            </label>
            <Input
              type="text"
              value={data.communityLocation || ''}
              onChange={(e) => onChange({ ...data, communityLocation: e.target.value })}
              placeholder="City, State, Country where your community is primarily located"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">
              Mother Tongue
            </label>
            <Input
              type="text"
              value={data.motherTongue || ''}
              onChange={(e) => onChange({ ...data, motherTongue: e.target.value })}
              placeholder="Your mother tongue/native language"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">
              Religious Practice Level
            </label>
            <select
              value={data.religiousLevel || ''}
              onChange={(e) => onChange({ ...data, religiousLevel: e.target.value })}
              className="w-full p-2 border border-gray-300 rounded-md focus:ring-primary focus:border-primary"
            >
              <option value="">Select Level</option>
              <option value="Very Religious">Very Religious</option>
              <option value="Moderately Religious">Moderately Religious</option>
              <option value="Occasionally Religious">Occasionally Religious</option>
              <option value="Not Very Religious">Not Very Religious</option>
              <option value="Spiritual but not Religious">Spiritual but not Religious</option>
            </select>
          </div>
        </CardContent>
      </Card>

      {/* Family Background */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Users className="h-5 w-5" />
            Family Background
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div>
            <label className="block text-sm font-medium mb-1">
              Family Background Description
            </label>
            <textarea
              value={data.familyBackground || ''}
              onChange={(e) => onChange({ ...data, familyBackground: e.target.value })}
              rows={4}
              className="w-full p-2 border border-gray-300 rounded-md focus:ring-primary focus:border-primary"
              placeholder="Describe your family background, values, traditions, and upbringing..."
            />
          </div>
        </CardContent>
      </Card>
    </div>
  );
};