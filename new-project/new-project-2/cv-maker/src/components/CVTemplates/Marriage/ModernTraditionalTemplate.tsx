import React from 'react';
import { MarriageBiodata } from '@/types';
import { MapPin, Phone, Mail, Heart, GraduationCap, Briefcase, Star, Users, BookOpen, Camera, Globe, Sparkles } from 'lucide-react';
import { cn } from '@/lib/utils';

interface ModernTraditionalTemplateProps {
  data: MarriageBiodata;
  className?: string;
}

const ModernTraditionalTemplate: React.FC<ModernTraditionalTemplateProps> = ({ data, className }) => {
  const { personalInfo, contactInfo, familyInfo, education, occupation, lifestyle, horoscope, aboutMe, expectations, photos } = data;

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
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
      'w-full max-w-4xl mx-auto bg-white shadow-xl print:shadow-none',
      'border border-gray-100 rounded-lg overflow-hidden',
      className
    )}>
      {/* Modern Header with Traditional Elements */}
      <div className="relative">
        {/* Background Pattern */}
        <div className="absolute inset-0 bg-gradient-to-br from-marriage-50 via-white to-marriage-100"></div>

        {/* Profile Section */}
        <div className="relative z-10 p-8">
          <div className="flex flex-col md:flex-row items-center md:items-start gap-8">
            {/* Profile Photo */}
            <div className="flex-shrink-0 relative">
              <div className="w-32 h-32 rounded-full overflow-hidden border-4 border-marriage-200 shadow-lg">
                {photos.profile ? (
                  <img
                    src={photos.profile}
                    alt={personalInfo.fullName}
                    className="w-full h-full object-cover"
                  />
                ) : (
                  <div className="w-full h-full bg-marriage-200 flex items-center justify-center">
                    <Camera className="w-12 h-12 text-marriage-400" />
                  </div>
                )}
              </div>
              <div className="absolute -bottom-2 -right-2 bg-marriage-600 text-white rounded-full p-2">
                <Heart className="w-4 h-4" />
              </div>
            </div>

            {/* Personal Details */}
            <div className="flex-1 text-center md:text-left">
              <div className="mb-2">
                <span className="inline-block bg-marriage-100 text-marriage-700 px-3 py-1 rounded-full text-xs font-medium mb-2">
                  Seeking Life Partner
                </span>
                <h1 className="text-3xl font-bold text-gray-900 mb-2">{personalInfo.fullName}</h1>
                <p className="text-lg text-marriage-600 font-medium mb-4">
                  {getAge(personalInfo.dateOfBirth)} Years • {personalInfo.height} • {personalInfo.gender === 'male' ? 'Boy' : 'Girl'}
                </p>
              </div>

              {/* Quick Info */}
              <div className="flex flex-wrap justify-center md:justify-start gap-2 mb-4">
                <span className="bg-blue-50 text-blue-700 px-3 py-1 rounded-full text-xs font-medium">
                  {getMaritalStatusLabel(personalInfo.maritalStatus)}
                </span>
                <span className="bg-green-50 text-green-700 px-3 py-1 rounded-full text-xs font-medium">
                  {getComplexionLabel(personalInfo.complexion)}
                </span>
                <span className="bg-purple-50 text-purple-700 px-3 py-1 rounded-full text-xs font-medium">
                  {personalInfo.religion}
                </span>
                {personalInfo.caste && (
                  <span className="bg-orange-50 text-orange-700 px-3 py-1 rounded-full text-xs font-medium">
                    {personalInfo.caste}
                  </span>
                )}
              </div>

              {/* Contact */}
              <div className="flex flex-wrap justify-center md:justify-start gap-4 text-sm">
                <div className="flex items-center gap-1 text-gray-600">
                  <Phone className="w-4 h-4 text-marriage-600" />
                  <span>{contactInfo.phone}</span>
                </div>
                {contactInfo.whatsapp && (
                  <div className="flex items-center gap-1 text-gray-600">
                    <div className="w-4 h-4 bg-green-500 rounded flex items-center justify-center text-white text-xs">W</div>
                    <span>{contactInfo.whatsapp}</span>
                  </div>
                )}
                <div className="flex items-center gap-1 text-gray-600">
                  <Mail className="w-4 h-4 text-marriage-600" />
                  <span>{contactInfo.email}</span>
                </div>
                <div className="flex items-center gap-1 text-gray-600">
                  <MapPin className="w-4 h-4 text-marriage-600" />
                  <span>{contactInfo.city}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Decorative Border */}
        <div className="h-1 bg-gradient-to-r from-marriage-400 via-marriage-600 to-marriage-400"></div>
      </div>

      <div className="p-8">
        {/* About Me */}
        {aboutMe && (
          <div className="mb-8">
            <div className="flex items-center gap-2 mb-4">
              <div className="w-8 h-8 bg-marriage-100 rounded-full flex items-center justify-center">
                <BookOpen className="w-4 h-4 text-marriage-600" />
              </div>
              <h2 className="text-xl font-semibold text-gray-900">About Me</h2>
              <div className="flex-1 h-px bg-gray-200"></div>
            </div>
            <div className="bg-marriage-50 p-6 rounded-xl border-l-4 border-marriage-400">
              <p className="text-gray-700 leading-relaxed">{aboutMe}</p>
            </div>
          </div>
        )}

        {/* Personal Information */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
          <div className="bg-white border border-gray-200 rounded-lg p-4 shadow-sm">
            <h3 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
              <Star className="w-4 h-4 text-marriage-600" />
              Basic Details
            </h3>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-600">Date of Birth:</span>
                <span className="font-medium">{formatDate(personalInfo.dateOfBirth)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Birth Place:</span>
                <span className="font-medium">{personalInfo.birthPlace}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Height/Weight:</span>
                <span className="font-medium">{personalInfo.height} / {personalInfo.weight}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Body Type:</span>
                <span className="font-medium capitalize">{personalInfo.bodyType}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Blood Group:</span>
                <span className="font-medium">{personalInfo.bloodGroup}</span>
              </div>
            </div>
          </div>

          <div className="bg-white border border-gray-200 rounded-lg p-4 shadow-sm">
            <h3 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
              <Globe className="w-4 h-4 text-marriage-600" />
              Background
            </h3>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-600">Nationality:</span>
                <span className="font-medium">{personalInfo.nationality}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Religion:</span>
                <span className="font-medium">{personalInfo.religion}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Caste:</span>
                <span className="font-medium">{personalInfo.caste || 'General'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Mother Tongue:</span>
                <span className="font-medium">{personalInfo.motherTongue}</span>
              </div>
              {personalInfo.subCaste && (
                <div className="flex justify-between">
                  <span className="text-gray-600">Sub Caste:</span>
                  <span className="font-medium">{personalInfo.subCaste}</span>
                </div>
              )}
            </div>
          </div>

          <div className="bg-white border border-gray-200 rounded-lg p-4 shadow-sm">
            <h3 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
              <Users className="w-4 h-4 text-marriage-600" />
              Family
            </h3>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-600">Family Type:</span>
                <span className="font-medium capitalize">{familyInfo.familyType}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Family Status:</span>
                <span className="font-medium capitalize">{familyInfo.familyStatus.replace('_', ' ')}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Family Values:</span>
                <span className="font-medium capitalize">{familyInfo.familyValues}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Brothers:</span>
                <span className="font-medium">{familyInfo.brothers} ({familyInfo.marriedBrothers} married)</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Sisters:</span>
                <span className="font-medium">{familyInfo.sisters} ({familyInfo.marriedSisters} married)</span>
              </div>
            </div>
          </div>
        </div>

        {/* Education & Career */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          <div>
            <div className="flex items-center gap-2 mb-4">
              <div className="w-8 h-8 bg-marriage-100 rounded-full flex items-center justify-center">
                <GraduationCap className="w-4 h-4 text-marriage-600" />
              </div>
              <h2 className="text-xl font-semibold text-gray-900">Education</h2>
            </div>
            <div className="space-y-3">
              {education.map((edu) => (
                <div key={edu.id} className="bg-gray-50 p-4 rounded-lg border border-gray-200">
                  <h3 className="font-semibold text-gray-900">{edu.degree}</h3>
                  <p className="text-gray-600 text-sm">{edu.institution}</p>
                  {edu.specialization && (
                    <p className="text-gray-500 text-xs mt-1">Specialization: {edu.specialization}</p>
                  )}
                  <div className="flex justify-between items-center mt-2">
                    <span className="text-xs text-gray-500">{edu.year}</span>
                    {(edu.percentage || edu.grade) && (
                      <span className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded">
                        {edu.percentage || edu.grade}
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div>
            <div className="flex items-center gap-2 mb-4">
              <div className="w-8 h-8 bg-marriage-100 rounded-full flex items-center justify-center">
                <Briefcase className="w-4 h-4 text-marriage-600" />
              </div>
              <h2 className="text-xl font-semibold text-gray-900">Career</h2>
            </div>
            <div className="space-y-3">
              {occupation.map((occ) => (
                <div key={occ.id} className="bg-gray-50 p-4 rounded-lg border border-gray-200">
                  <h3 className="font-semibold text-gray-900">{occ.occupation}</h3>
                  {occ.designation && (
                    <p className="text-gray-600 text-sm">{occ.designation}</p>
                  )}
                  {occ.company && (
                    <p className="text-gray-500 text-xs">{occ.company}</p>
                  )}
                  <div className="mt-2 space-y-1">
                    <p className="text-xs text-gray-600">Industry: {occ.industry}</p>
                    <p className="text-xs text-gray-600">Income: {occ.annualIncome}</p>
                    <p className="text-xs text-gray-600">Location: {occ.workLocation}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Lifestyle & Interests */}
        <div className="mb-8">
          <div className="flex items-center gap-2 mb-4">
            <div className="w-8 h-8 bg-marriage-100 rounded-full flex items-center justify-center">
              <Sparkles className="w-4 h-4 text-marriage-600" />
            </div>
            <h2 className="text-xl font-semibold text-gray-900">Lifestyle & Interests</h2>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="bg-gradient-to-br from-green-50 to-green-100 p-4 rounded-lg">
              <h3 className="font-medium text-green-800 mb-2">Diet</h3>
              <p className="text-green-700 capitalize">{lifestyle.diet.replace('_', ' ')}</p>
            </div>
            <div className="bg-gradient-to-br from-blue-50 to-blue-100 p-4 rounded-lg">
              <h3 className="font-medium text-blue-800 mb-2">Smoking</h3>
              <p className="text-blue-700 capitalize">{lifestyle.smoking}</p>
            </div>
            <div className="bg-gradient-to-br from-purple-50 to-purple-100 p-4 rounded-lg">
              <h3 className="font-medium text-purple-800 mb-2">Drinking</h3>
              <p className="text-purple-700 capitalize">{lifestyle.drinking}</p>
            </div>
            <div className="bg-gradient-to-br from-orange-50 to-orange-100 p-4 rounded-lg">
              <h3 className="font-medium text-orange-800 mb-2">Dress Style</h3>
              <p className="text-orange-700 capitalize">{lifestyle.dressStyle}</p>
            </div>
          </div>

          {lifestyle.hobbies.length > 0 && (
            <div className="mt-4">
              <h3 className="font-medium text-gray-700 mb-2">Hobbies & Interests</h3>
              <div className="flex flex-wrap gap-2">
                {lifestyle.hobbies.map((hobby, index) => (
                  <span key={index} className="bg-marriage-100 text-marriage-700 px-3 py-1 rounded-full text-sm">
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
            <div className="flex items-center gap-2 mb-4">
              <div className="w-8 h-8 bg-marriage-100 rounded-full flex items-center justify-center">
                <Star className="w-4 h-4 text-marriage-600" />
              </div>
              <h2 className="text-xl font-semibold text-gray-900">Horoscope Details</h2>
            </div>
            <div className="bg-gradient-to-br from-marriage-50 to-white p-6 rounded-xl border border-marriage-200">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="text-center">
                  <p className="text-sm text-gray-600 mb-1">Star</p>
                  <p className="font-semibold text-marriage-700">{horoscope.star || 'N/A'}</p>
                </div>
                <div className="text-center">
                  <p className="text-sm text-gray-600 mb-1">Rashi</p>
                  <p className="font-semibold text-marriage-700">{horoscope.rashi || 'N/A'}</p>
                </div>
                <div className="text-center">
                  <p className="text-sm text-gray-600 mb-1">Nakshatra</p>
                  <p className="font-semibold text-marriage-700">{horoscope.nakshatra || 'N/A'}</p>
                </div>
                <div className="text-center">
                  <p className="text-sm text-gray-600 mb-1">Manglik</p>
                  <p className="font-semibold text-marriage-700 capitalize">{horoscope.manglik}</p>
                </div>
              </div>
              {horoscope.birthTime && (
                <div className="mt-4 pt-4 border-t border-marriage-200 text-center">
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
            <div className="flex items-center gap-2 mb-4">
              <div className="w-8 h-8 bg-marriage-100 rounded-full flex items-center justify-center">
                <Heart className="w-4 h-4 text-marriage-600" />
              </div>
              <h2 className="text-xl font-semibold text-gray-900">Partner Expectations</h2>
            </div>
            <div className="bg-gradient-to-r from-marriage-50 to-pink-50 p-6 rounded-xl border border-marriage-200">
              <p className="text-gray-700 leading-relaxed">{expectations}</p>
            </div>
          </div>
        )}

        {/* Footer */}
        <div className="text-center text-sm text-gray-500 mt-8 pt-6 border-t border-gray-200">
          <p>Generated with ❤️ for matrimonial purposes</p>
          <p className="text-xs mt-1">All information provided is authentic to the best of our knowledge</p>
        </div>
      </div>
    </div>
  );
};

export default ModernTraditionalTemplate;