import React from 'react';
import { MarriageBiodata } from '@/types';
import { MapPin, Phone, Mail, Heart, GraduationCap, Briefcase, Star, Users, BookOpen, Camera, Crown, Gem, Sparkles, Shield } from 'lucide-react';
import { cn } from '@/lib/utils';

interface PremiumFamilyTemplateProps {
  data: MarriageBiodata;
  className?: string;
}

const PremiumFamilyTemplate: React.FC<PremiumFamilyTemplateProps> = ({ data, className }) => {
  const { personalInfo, contactInfo, familyInfo, education, occupation, lifestyle, horoscope, aboutMe, expectations, photos } = data;

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
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
      'w-full max-w-5xl mx-auto bg-white shadow-2xl print:shadow-none',
      'border-8 border-gradient-to-r from-yellow-400 via-yellow-300 to-yellow-400',
      className
    )}>
      {/* Premium Header */}
      <div className="relative bg-gradient-to-br from-amber-50 via-white to-yellow-50">
        {/* Premium Border Pattern */}
        <div className="absolute inset-0 border-4 border-transparent bg-gradient-to-r from-yellow-600 to-amber-600 opacity-20 m-1 rounded-lg"></div>

        {/* Crown Decoration */}
        <div className="absolute top-4 left-1/2 transform -translate-x-1/2">
          <Crown className="w-8 h-8 text-yellow-600" />
        </div>

        <div className="relative z-10 p-8">
          <div className="flex flex-col lg:flex-row items-center lg:items-start gap-8">
            {/* Profile Photos */}
            <div className="flex flex-col items-center gap-4">
              <div className="relative group">
                <div className="w-40 h-40 rounded-full overflow-hidden border-4 border-yellow-400 shadow-2xl transform group-hover:scale-105 transition-transform duration-300">
                  {photos.profile ? (
                    <img
                      src={photos.profile}
                      alt={personalInfo.fullName}
                      className="w-full h-full object-cover"
                    />
                  ) : (
                    <div className="w-full h-full bg-gradient-to-br from-yellow-200 to-yellow-400 flex items-center justify-center">
                      <Camera className="w-16 h-16 text-yellow-600" />
                    </div>
                  )}
                </div>
                <div className="absolute -bottom-2 -right-2 bg-yellow-500 text-white rounded-full p-3 shadow-lg">
                  <Heart className="w-6 h-6" />
                </div>
              </div>

              {/* Additional Photos */}
              {photos.additional.length > 0 && (
                <div className="flex gap-2">
                  {photos.additional.slice(0, 3).map((photo, index) => (
                    <div key={index} className="w-16 h-16 rounded-lg overflow-hidden border-2 border-yellow-300 shadow-md">
                      <img
                        src={photo}
                        alt={`Additional ${index + 1}`}
                        className="w-full h-full object-cover"
                      />
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Personal Information */}
            <div className="flex-1 text-center lg:text-left">
              <div className="mb-4">
                <div className="flex items-center justify-center lg:justify-start gap-2 mb-2">
                  <Gem className="w-5 h-5 text-yellow-600" />
                  <span className="bg-gradient-to-r from-yellow-400 to-amber-500 text-white px-4 py-1 rounded-full text-sm font-semibold shadow-lg">
                    Premium Profile
                  </span>
                </div>
                <h1 className="text-4xl font-bold text-gray-900 mb-2">{personalInfo.fullName}</h1>
                <p className="text-xl text-amber-600 font-medium mb-4">
                  {getAge(personalInfo.dateOfBirth)} Years • {personalInfo.height} • {personalInfo.gender === 'male' ? 'Groom' : 'Bride'}
                </p>
              </div>

              {/* Premium Badges */}
              <div className="flex flex-wrap justify-center lg:justify-start gap-2 mb-6">
                <span className="bg-gradient-to-r from-blue-500 to-blue-600 text-white px-3 py-1 rounded-full text-xs font-medium shadow-md">
                  {getMaritalStatusLabel(personalInfo.maritalStatus)}
                </span>
                <span className="bg-gradient-to-r from-green-500 to-green-600 text-white px-3 py-1 rounded-full text-xs font-medium shadow-md">
                  {getComplexionLabel(personalInfo.complexion)}
                </span>
                <span className="bg-gradient-to-r from-purple-500 to-purple-600 text-white px-3 py-1 rounded-full text-xs font-medium shadow-md">
                  {personalInfo.religion}
                </span>
                {personalInfo.caste && (
                  <span className="bg-gradient-to-r from-pink-500 to-pink-600 text-white px-3 py-1 rounded-full text-xs font-medium shadow-md">
                    {personalInfo.caste}
                  </span>
                )}
              </div>

              {/* Contact Information */}
              <div className="bg-gradient-to-r from-amber-50 to-yellow-50 p-4 rounded-xl border border-yellow-200">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
                  <div className="flex items-center gap-2">
                    <div className="w-8 h-8 bg-yellow-500 rounded-full flex items-center justify-center">
                      <Phone className="w-4 h-4 text-white" />
                    </div>
                    <span className="font-medium">{contactInfo.phone}</span>
                  </div>
                  {contactInfo.whatsapp && (
                    <div className="flex items-center gap-2">
                      <div className="w-8 h-8 bg-green-500 rounded-full flex items-center justify-center">
                        <span className="text-white text-xs font-bold">W</span>
                      </div>
                      <span className="font-medium">{contactInfo.whatsapp}</span>
                    </div>
                  )}
                  <div className="flex items-center gap-2">
                    <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center">
                      <Mail className="w-4 h-4 text-white" />
                    </div>
                    <span className="font-medium">{contactInfo.email}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-8 h-8 bg-red-500 rounded-full flex items-center justify-center">
                      <MapPin className="w-4 h-4 text-white" />
                    </div>
                    <span className="font-medium">{contactInfo.city}, {contactInfo.state}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Elegant Divider */}
        <div className="flex items-center justify-center gap-2 pb-4">
          <div className="flex-1 h-px bg-gradient-to-r from-transparent via-yellow-400 to-transparent"></div>
          <Heart className="w-6 h-6 text-yellow-500" />
          <div className="flex-1 h-px bg-gradient-to-r from-transparent via-yellow-400 to-transparent"></div>
        </div>
      </div>

      <div className="p-8">
        {/* About Me Section */}
        {aboutMe && (
          <div className="mb-8">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 bg-gradient-to-br from-amber-400 to-yellow-500 rounded-full flex items-center justify-center shadow-lg">
                <BookOpen className="w-5 h-5 text-white" />
              </div>
              <h2 className="text-2xl font-bold text-gray-900">About Me</h2>
              <div className="flex-1 h-px bg-gradient-to-r from-yellow-200 via-yellow-400 to-yellow-200"></div>
            </div>
            <div className="bg-gradient-to-br from-amber-50 via-white to-yellow-50 p-8 rounded-2xl border-l-4 border-yellow-400 shadow-lg">
              <p className="text-gray-700 leading-relaxed text-lg">{aboutMe}</p>
            </div>
          </div>
        )}

        {/* Premium Information Cards */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          {/* Personal Details Card */}
          <div className="bg-gradient-to-br from-blue-50 to-blue-100 p-6 rounded-2xl shadow-lg border border-blue-200">
            <div className="flex items-center gap-2 mb-4">
              <div className="w-10 h-10 bg-blue-500 rounded-full flex items-center justify-center">
                <Star className="w-5 h-5 text-white" />
              </div>
              <h3 className="text-xl font-bold text-blue-900">Personal Details</h3>
            </div>
            <div className="space-y-3">
              <div className="bg-white p-3 rounded-lg">
                <p className="text-xs text-blue-600 font-medium">Date of Birth</p>
                <p className="text-sm font-semibold text-gray-900">{formatDate(personalInfo.dateOfBirth)}</p>
              </div>
              <div className="bg-white p-3 rounded-lg">
                <p className="text-xs text-blue-600 font-medium">Birth Place</p>
                <p className="text-sm font-semibold text-gray-900">{personalInfo.birthPlace}</p>
              </div>
              <div className="bg-white p-3 rounded-lg">
                <p className="text-xs text-blue-600 font-medium">Physical Attributes</p>
                <p className="text-sm font-semibold text-gray-900">{personalInfo.height} / {personalInfo.weight}</p>
              </div>
              <div className="bg-white p-3 rounded-lg">
                <p className="text-xs text-blue-600 font-medium">Body Type</p>
                <p className="text-sm font-semibold text-gray-900 capitalize">{personalInfo.bodyType}</p>
              </div>
            </div>
          </div>

          {/* Family Background Card */}
          <div className="bg-gradient-to-br from-green-50 to-green-100 p-6 rounded-2xl shadow-lg border border-green-200">
            <div className="flex items-center gap-2 mb-4">
              <div className="w-10 h-10 bg-green-500 rounded-full flex items-center justify-center">
                <Users className="w-5 h-5 text-white" />
              </div>
              <h3 className="text-xl font-bold text-green-900">Family Background</h3>
            </div>
            <div className="space-y-3">
              <div className="bg-white p-3 rounded-lg">
                <p className="text-xs text-green-600 font-medium">Family Type</p>
                <p className="text-sm font-semibold text-gray-900 capitalize">{familyInfo.familyType}</p>
              </div>
              <div className="bg-white p-3 rounded-lg">
                <p className="text-xs text-green-600 font-medium">Family Status</p>
                <p className="text-sm font-semibold text-gray-900 capitalize">{familyInfo.familyStatus.replace('_', ' ')}</p>
              </div>
              <div className="bg-white p-3 rounded-lg">
                <p className="text-xs text-green-600 font-medium">Father</p>
                <p className="text-sm font-semibold text-gray-900">{familyInfo.fatherName}</p>
                <p className="text-xs text-gray-600">{familyInfo.fatherOccupation}</p>
              </div>
              <div className="bg-white p-3 rounded-lg">
                <p className="text-xs text-green-600 font-medium">Mother</p>
                <p className="text-sm font-semibold text-gray-900">{familyInfo.motherName}</p>
                <p className="text-xs text-gray-600">{familyInfo.motherOccupation}</p>
              </div>
            </div>
          </div>

          {/* Education & Career Card */}
          <div className="bg-gradient-to-br from-purple-50 to-purple-100 p-6 rounded-2xl shadow-lg border border-purple-200">
            <div className="flex items-center gap-2 mb-4">
              <div className="w-10 h-10 bg-purple-500 rounded-full flex items-center justify-center">
                <GraduationCap className="w-5 h-5 text-white" />
              </div>
              <h3 className="text-xl font-bold text-purple-900">Education & Career</h3>
            </div>
            <div className="space-y-3">
              {education.slice(0, 2).map((edu) => (
                <div key={edu.id} className="bg-white p-3 rounded-lg">
                  <p className="text-xs text-purple-600 font-medium">Education</p>
                  <p className="text-sm font-semibold text-gray-900">{edu.degree}</p>
                  <p className="text-xs text-gray-600">{edu.institution}</p>
                </div>
              ))}
              {occupation.slice(0, 2).map((occ) => (
                <div key={occ.id} className="bg-white p-3 rounded-lg">
                  <p className="text-xs text-purple-600 font-medium">Occupation</p>
                  <p className="text-sm font-semibold text-gray-900">{occ.occupation}</p>
                  <p className="text-xs text-gray-600">{occ.annualIncome}</p>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Detailed Sections */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          {/* Detailed Education */}
          <div>
            <div className="flex items-center gap-2 mb-4">
              <GraduationCap className="w-6 h-6 text-amber-600" />
              <h2 className="text-xl font-bold text-gray-900">Educational Qualifications</h2>
            </div>
            <div className="space-y-4">
              {education.map((edu) => (
                <div key={edu.id} className="bg-gradient-to-r from-amber-50 to-yellow-50 p-6 rounded-xl border border-amber-200 shadow-md">
                  <h3 className="text-lg font-bold text-gray-900 mb-2">{edu.degree}</h3>
                  <p className="text-gray-600 mb-1">{edu.institution}</p>
                  {edu.specialization && (
                    <p className="text-sm text-gray-500 mb-2">Specialization: {edu.specialization}</p>
                  )}
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-gray-500">{edu.year}</span>
                    {(edu.percentage || edu.grade) && (
                      <span className="bg-amber-500 text-white px-3 py-1 rounded-full text-xs font-medium">
                        {edu.percentage || edu.grade}
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Detailed Career */}
          <div>
            <div className="flex items-center gap-2 mb-4">
              <Briefcase className="w-6 h-6 text-amber-600" />
              <h2 className="text-xl font-bold text-gray-900">Professional Details</h2>
            </div>
            <div className="space-y-4">
              {occupation.map((occ) => (
                <div key={occ.id} className="bg-gradient-to-r from-green-50 to-emerald-50 p-6 rounded-xl border border-green-200 shadow-md">
                  <h3 className="text-lg font-bold text-gray-900 mb-2">{occ.occupation}</h3>
                  {occ.designation && (
                    <p className="text-gray-600 mb-1">{occ.designation}</p>
                  )}
                  {occ.company && (
                    <p className="text-gray-600 mb-1">{occ.company}</p>
                  )}
                  <div className="space-y-1 mt-3">
                    <p className="text-sm text-gray-600">Industry: {occ.industry}</p>
                    <p className="text-sm text-gray-600">Annual Income: {occ.annualIncome}</p>
                    <p className="text-sm text-gray-600">Work Location: {occ.workLocation}</p>
                    <p className="text-sm text-gray-600">Experience: {occ.workExperience || 'N/A'}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Lifestyle & Horoscope */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          {/* Lifestyle */}
          <div>
            <div className="flex items-center gap-2 mb-4">
              <Sparkles className="w-6 h-6 text-amber-600" />
              <h2 className="text-xl font-bold text-gray-900">Lifestyle & Interests</h2>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="bg-gradient-to-br from-pink-50 to-rose-50 p-4 rounded-xl border border-pink-200">
                <p className="text-sm font-medium text-pink-700 mb-2">Diet</p>
                <p className="text-lg font-bold text-pink-900 capitalize">{lifestyle.diet.replace('_', ' ')}</p>
              </div>
              <div className="bg-gradient-to-br from-blue-50 to-indigo-50 p-4 rounded-xl border border-blue-200">
                <p className="text-sm font-medium text-blue-700 mb-2">Smoking</p>
                <p className="text-lg font-bold text-blue-900 capitalize">{lifestyle.smoking}</p>
              </div>
              <div className="bg-gradient-to-br from-purple-50 to-violet-50 p-4 rounded-xl border border-purple-200">
                <p className="text-sm font-medium text-purple-700 mb-2">Drinking</p>
                <p className="text-lg font-bold text-purple-900 capitalize">{lifestyle.drinking}</p>
              </div>
              <div className="bg-gradient-to-br from-orange-50 to-amber-50 p-4 rounded-xl border border-orange-200">
                <p className="text-sm font-medium text-orange-700 mb-2">Dress Style</p>
                <p className="text-lg font-bold text-orange-900 capitalize">{lifestyle.dressStyle}</p>
              </div>
            </div>

            {lifestyle.hobbies.length > 0 && (
              <div className="mt-4">
                <h3 className="font-medium text-gray-700 mb-2">Hobbies & Interests</h3>
                <div className="flex flex-wrap gap-2">
                  {lifestyle.hobbies.map((hobby, index) => (
                    <span key={index} className="bg-amber-100 text-amber-700 px-3 py-1 rounded-full text-sm font-medium">
                      {hobby}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Horoscope */}
          {horoscope && horoscope.hasHoroscope && (
            <div>
              <div className="flex items-center gap-2 mb-4">
                <Star className="w-6 h-6 text-amber-600" />
                <h2 className="text-xl font-bold text-gray-900">Horoscope Details</h2>
              </div>
              <div className="bg-gradient-to-br from-indigo-50 to-purple-50 p-6 rounded-2xl border border-indigo-200 shadow-lg">
                <div className="grid grid-cols-2 gap-4 mb-4">
                  <div className="text-center bg-white p-4 rounded-xl shadow-sm">
                    <p className="text-sm text-indigo-600 font-medium mb-1">Star</p>
                    <p className="text-lg font-bold text-indigo-900">{horoscope.star || 'N/A'}</p>
                  </div>
                  <div className="text-center bg-white p-4 rounded-xl shadow-sm">
                    <p className="text-sm text-indigo-600 font-medium mb-1">Rashi</p>
                    <p className="text-lg font-bold text-indigo-900">{horoscope.rashi || 'N/A'}</p>
                  </div>
                  <div className="text-center bg-white p-4 rounded-xl shadow-sm">
                    <p className="text-sm text-indigo-600 font-medium mb-1">Nakshatra</p>
                    <p className="text-lg font-bold text-indigo-900">{horoscope.nakshatra || 'N/A'}</p>
                  </div>
                  <div className="text-center bg-white p-4 rounded-xl shadow-sm">
                    <p className="text-sm text-indigo-600 font-medium mb-1">Manglik</p>
                    <p className="text-lg font-bold text-indigo-900 capitalize">{horoscope.manglik}</p>
                  </div>
                </div>
                {horoscope.birthTime && (
                  <div className="bg-indigo-100 p-4 rounded-xl text-center">
                    <p className="text-sm text-indigo-700">
                      Birth Time: {horoscope.birthTime}
                    </p>
                    <p className="text-sm text-indigo-700">
                      Birth Place: {horoscope.birthPlace}
                    </p>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>

        {/* Partner Expectations */}
        {expectations && (
          <div className="mb-8">
            <div className="flex items-center gap-2 mb-4">
              <Heart className="w-6 h-6 text-amber-600" />
              <h2 className="text-xl font-bold text-gray-900">Partner Expectations</h2>
            </div>
            <div className="bg-gradient-to-r from-pink-50 via-rose-50 to-pink-50 p-8 rounded-2xl border border-pink-200 shadow-lg">
              <div className="bg-white p-6 rounded-xl">
                <p className="text-gray-700 leading-relaxed text-lg">{expectations}</p>
              </div>
            </div>
          </div>
        )}

        {/* Premium Footer */}
        <div className="text-center">
          <div className="flex items-center justify-center gap-2 mb-4">
            <Shield className="w-5 h-5 text-amber-600" />
            <span className="text-amber-600 font-medium">Verified Profile</span>
          </div>
          <p className="text-sm text-gray-500 mb-2">Premium Matrimonial Profile</p>
          <p className="text-xs text-gray-400">All information is verified and authentic</p>
        </div>
      </div>
    </div>
  );
};

export default PremiumFamilyTemplate;