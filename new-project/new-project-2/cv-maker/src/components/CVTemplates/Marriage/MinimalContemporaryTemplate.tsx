import React from 'react';
import { MarriageBiodata } from '@/types';
import { MapPin, Phone, Mail, Camera } from 'lucide-react';
import { cn } from '@/lib/utils';

interface MinimalContemporaryTemplateProps {
  data: MarriageBiodata;
  className?: string;
}

const MinimalContemporaryTemplate: React.FC<MinimalContemporaryTemplateProps> = ({ data, className }) => {
  const { personalInfo, contactInfo, familyInfo, education, occupation, lifestyle, horoscope, aboutMe, expectations, photos } = data;

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short'
    });
  };

  const getAge = (dateOfBirth: string) => {
    const birthDate = new Date(dateOfBirth);
    const today = new Date();
    let age = today.getFullYear() - birthDate.getFullYear();
    const monthDiff = today.getMonth() - birthDate.getMonth();
    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
      age--;
    }
    return age;
  };

  const getComplexionLabel = (complexion: string) => {
    const labels: Record<string, string> = {
      very_fair: 'Very Fair',
      fair: 'Fair',
      wheatish: 'Wheatish',
      olive: 'Olive',
      dark: 'Dark'
    };
    return labels[complexion] || complexion;
  };

  const getMaritalStatusLabel = (status: string) => {
    const labels: Record<string, string> = {
      never_married: 'Never Married',
      divorced: 'Divorced',
      widowed: 'Widowed'
    };
    return labels[status] || status;
  };

  return (
    <div className={cn(
      'w-full max-w-3xl mx-auto bg-white print:shadow-none',
      'border border-gray-200 rounded-lg',
      className
    )}>
      {/* Clean Minimal Header */}
      <div className="border-b border-gray-200">
        <div className="p-8">
          <div className="flex flex-col md:flex-row items-center md:items-start gap-8">
            {/* Profile Photo */}
            <div className="flex-shrink-0">
              <div className="w-28 h-28 rounded-lg overflow-hidden bg-gray-100 border border-gray-200">
                {photos.profile ? (
                  <img
                    src={photos.profile}
                    alt={personalInfo.fullName}
                    className="w-full h-full object-cover"
                  />
                ) : (
                  <div className="w-full h-full flex items-center justify-center">
                    <Camera className="w-12 h-12 text-gray-400" />
                  </div>
                )}
              </div>
            </div>

            {/* Basic Information */}
            <div className="flex-1 text-center md:text-left">
              <h1 className="text-3xl font-light text-gray-900 mb-2">{personalInfo.fullName}</h1>
              <p className="text-lg text-gray-600 mb-4">
                {getAge(personalInfo.dateOfBirth)} years • {personalInfo.height} • {personalInfo.gender === 'male' ? 'Male' : 'Female'}
              </p>

              <div className="flex flex-wrap justify-center md:justify-start gap-2 mb-4">
                <span className="text-sm bg-gray-100 text-gray-700 px-3 py-1 rounded">
                  {getMaritalStatusLabel(personalInfo.maritalStatus)}
                </span>
                <span className="text-sm bg-gray-100 text-gray-700 px-3 py-1 rounded">
                  {personalInfo.religion}
                </span>
                {personalInfo.caste && (
                  <span className="text-sm bg-gray-100 text-gray-700 px-3 py-1 rounded">
                    {personalInfo.caste}
                  </span>
                )}
              </div>

              <div className="flex flex-wrap justify-center md:justify-start gap-4 text-sm text-gray-600">
                {contactInfo.phone && (
                  <div className="flex items-center gap-1">
                    <Phone className="w-4 h-4" />
                    <span>{contactInfo.phone}</span>
                  </div>
                )}
                {contactInfo.email && (
                  <div className="flex items-center gap-1">
                    <Mail className="w-4 h-4" />
                    <span>{contactInfo.email}</span>
                  </div>
                )}
                <div className="flex items-center gap-1">
                  <MapPin className="w-4 h-4" />
                  <span>{contactInfo.city}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="p-8">
        {/* About Section */}
        {aboutMe && (
          <div className="mb-8">
            <h2 className="text-xl font-medium text-gray-900 mb-3">About</h2>
            <p className="text-gray-700 leading-relaxed">{aboutMe}</p>
          </div>
        )}

        {/* Personal Details Grid */}
        <div className="mb-8">
          <h2 className="text-xl font-medium text-gray-900 mb-4">Personal Details</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="flex justify-between py-2 border-b border-gray-100">
              <span className="text-gray-600">Date of Birth</span>
              <span className="font-medium">{formatDate(personalInfo.dateOfBirth)}</span>
            </div>
            <div className="flex justify-between py-2 border-b border-gray-100">
              <span className="text-gray-600">Birth Place</span>
              <span className="font-medium">{personalInfo.birthPlace}</span>
            </div>
            <div className="flex justify-between py-2 border-b border-gray-100">
              <span className="text-gray-600">Height / Weight</span>
              <span className="font-medium">{personalInfo.height} / {personalInfo.weight}</span>
            </div>
            <div className="flex justify-between py-2 border-b border-gray-100">
              <span className="text-gray-600">Complexion</span>
              <span className="font-medium">{getComplexionLabel(personalInfo.complexion)}</span>
            </div>
            <div className="flex justify-between py-2 border-b border-gray-100">
              <span className="text-gray-600">Body Type</span>
              <span className="font-medium capitalize">{personalInfo.bodyType}</span>
            </div>
            <div className="flex justify-between py-2 border-b border-gray-100">
              <span className="text-gray-600">Mother Tongue</span>
              <span className="font-medium">{personalInfo.motherTongue}</span>
            </div>
            <div className="flex justify-between py-2 border-b border-gray-100">
              <span className="text-gray-600">Nationality</span>
              <span className="font-medium">{personalInfo.nationality}</span>
            </div>
            <div className="flex justify-between py-2 border-b border-gray-100">
              <span className="text-gray-600">Blood Group</span>
              <span className="font-medium">{personalInfo.bloodGroup}</span>
            </div>
          </div>
        </div>

        {/* Family Details */}
        <div className="mb-8">
          <h2 className="text-xl font-medium text-gray-900 mb-4">Family Details</h2>
          <div className="bg-gray-50 p-6 rounded-lg">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
              <div>
                <p className="text-sm text-gray-600 mb-1">Family Type</p>
                <p className="font-medium capitalize">{familyInfo.familyType}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600 mb-1">Family Status</p>
                <p className="font-medium capitalize">{familyInfo.familyStatus.replace('_', ' ')}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600 mb-1">Family Values</p>
                <p className="font-medium capitalize">{familyInfo.familyValues}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600 mb-1">Family Location</p>
                <p className="font-medium">{familyInfo.familyLocation}</p>
              </div>
            </div>

            <div className="border-t border-gray-200 pt-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-gray-600 mb-1">Father</p>
                  <p className="font-medium">{familyInfo.fatherName}</p>
                  <p className="text-sm text-gray-500">{familyInfo.fatherOccupation}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600 mb-1">Mother</p>
                  <p className="font-medium">{familyInfo.motherName}</p>
                  <p className="text-sm text-gray-500">{familyInfo.motherOccupation}</p>
                </div>
              </div>
            </div>

            <div className="border-t border-gray-200 pt-4 mt-4">
              <p className="text-sm text-gray-600 mb-1">Siblings</p>
              <p className="text-sm">
                Brothers: {familyInfo.brothers} ({familyInfo.marriedBrothers} married) •
                Sisters: {familyInfo.sisters} ({familyInfo.marriedSisters} married)
              </p>
            </div>
          </div>
        </div>

        {/* Education & Occupation */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
          <div>
            <h2 className="text-xl font-medium text-gray-900 mb-4">Education</h2>
            <div className="space-y-3">
              {education.map((edu) => (
                <div key={edu.id} className="border-l-2 border-gray-200 pl-4">
                  <h3 className="font-medium text-gray-900">{edu.degree}</h3>
                  <p className="text-sm text-gray-600">{edu.institution}</p>
                  <p className="text-sm text-gray-500">{edu.year}</p>
                  {(edu.percentage || edu.grade) && (
                    <p className="text-sm text-gray-500">Grade: {edu.percentage || edu.grade}</p>
                  )}
                </div>
              ))}
            </div>
          </div>

          <div>
            <h2 className="text-xl font-medium text-gray-900 mb-4">Occupation</h2>
            <div className="space-y-3">
              {occupation.map((occ) => (
                <div key={occ.id} className="border-l-2 border-gray-200 pl-4">
                  <h3 className="font-medium text-gray-900">{occ.occupation}</h3>
                  {occ.company && <p className="text-sm text-gray-600">{occ.company}</p>}
                  {occ.designation && <p className="text-sm text-gray-600">{occ.designation}</p>}
                  <p className="text-sm text-gray-500">{occ.annualIncome}</p>
                  <p className="text-sm text-gray-500">{occ.workLocation}</p>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Lifestyle */}
        <div className="mb-8">
          <h2 className="text-xl font-medium text-gray-900 mb-4">Lifestyle</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center">
              <p className="text-sm text-gray-600 mb-1">Diet</p>
              <p className="font-medium capitalize">{lifestyle.diet.replace('_', ' ')}</p>
            </div>
            <div className="text-center">
              <p className="text-sm text-gray-600 mb-1">Smoking</p>
              <p className="font-medium capitalize">{lifestyle.smoking}</p>
            </div>
            <div className="text-center">
              <p className="text-sm text-gray-600 mb-1">Drinking</p>
              <p className="font-medium capitalize">{lifestyle.drinking}</p>
            </div>
            <div className="text-center">
              <p className="text-sm text-gray-600 mb-1">Dress Style</p>
              <p className="font-medium capitalize">{lifestyle.dressStyle}</p>
            </div>
          </div>

          {lifestyle.hobbies.length > 0 && (
            <div className="mt-4">
              <p className="text-sm text-gray-600 mb-2">Hobbies & Interests</p>
              <div className="flex flex-wrap gap-2">
                {lifestyle.hobbies.map((hobby, index) => (
                  <span key={index} className="text-sm bg-gray-100 text-gray-700 px-2 py-1 rounded">
                    {hobby}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Horoscope */}
        {horoscope && horoscope.hasHoroscope && (
          <div className="mb-8">
            <h2 className="text-xl font-medium text-gray-900 mb-4">Horoscope</h2>
            <div className="bg-gray-50 p-6 rounded-lg">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div>
                  <p className="text-sm text-gray-600 mb-1">Star</p>
                  <p className="font-medium">{horoscope.star || 'N/A'}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600 mb-1">Rashi</p>
                  <p className="font-medium">{horoscope.rashi || 'N/A'}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600 mb-1">Nakshatra</p>
                  <p className="font-medium">{horoscope.nakshatra || 'N/A'}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600 mb-1">Manglik</p>
                  <p className="font-medium capitalize">{horoscope.manglik}</p>
                </div>
              </div>
              {horoscope.birthTime && (
                <div className="mt-4 pt-4 border-t border-gray-200">
                  <p className="text-sm text-gray-600">
                    Birth: {horoscope.birthTime} at {horoscope.birthPlace}
                  </p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Partner Expectations */}
        {expectations && (
          <div className="mb-8">
            <h2 className="text-xl font-medium text-gray-900 mb-4">Partner Expectations</h2>
            <div className="bg-gray-50 p-6 rounded-lg">
              <p className="text-gray-700 leading-relaxed">{expectations}</p>
            </div>
          </div>
        )}

        {/* Footer */}
        <div className="text-center text-sm text-gray-500 pt-8 border-t border-gray-200">
          <p>Matrimonial Profile</p>
        </div>
      </div>
    </div>
  );
};

export default MinimalContemporaryTemplate;