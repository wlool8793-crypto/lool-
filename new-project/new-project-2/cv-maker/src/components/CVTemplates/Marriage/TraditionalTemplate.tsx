import React from 'react';
import { MarriageBiodata } from '@/types';
import { MapPin, Phone, Mail, Heart, GraduationCap, Briefcase, Star, Users, BookOpen } from 'lucide-react';
import { cn } from '@/lib/utils';

interface TraditionalTemplateProps {
  data: MarriageBiodata;
  className?: string;
}

const TraditionalTemplate: React.FC<TraditionalTemplateProps> = ({ data, className }) => {
  const { personalInfo, contactInfo, familyInfo, education, occupation, lifestyle, horoscope, aboutMe, expectations } = data;

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
      'w-full max-w-3xl mx-auto bg-white border-8 border-marriage-600 shadow-lg print:shadow-none',
      'bg-gradient-to-br from-white to-marriage-50',
      className
    )}>
      {/* Traditional Header with Religious Elements */}
      <div className="relative bg-gradient-to-r from-marriage-600 via-marriage-700 to-marriage-800 text-white overflow-hidden">
        {/* Decorative Pattern */}
        <div className="absolute inset-0 opacity-10">
          <div className="absolute top-0 left-0 w-full h-full bg-repeat"
               style={{ backgroundImage: 'url("data:image/svg+xml,%3Csvg width=\'40\' height=\'40\' viewBox=\'0 0 40 40\' xmlns=\'http://www.w3.org/2000/svg\'%3E%3Cg fill=\'%23fff\' fill-opacity=\'0.4\'%3E%3Cpath d=\'M0 40L40 0H20L0 20M40 40V20L20 40\'/%3E%3C/g%3E%3C/svg%3E")' }}>
          </div>
        </div>

        <div className="relative z-10 p-8 text-center">
          {/* Religious Symbol */}
          <div className="mb-4">
            <div className="w-16 h-16 mx-auto bg-white/20 rounded-full flex items-center justify-center">
              <Heart className="w-8 h-8 text-white" />
            </div>
          </div>

          <h1 className="text-3xl font-bold mb-2">{personalInfo.fullName}</h1>
          <div className="flex justify-center items-center gap-4 text-lg mb-4">
            <span>{getAge(personalInfo.dateOfBirth)} Years</span>
            <span>•</span>
            <span className="capitalize">{personalInfo.gender}</span>
            <span>•</span>
            <span>{personalInfo.height}</span>
          </div>
          <div className="flex justify-center gap-2 mb-4">
            <span className="bg-white/20 px-3 py-1 rounded-full text-sm">
              {getMaritalStatusLabel(personalInfo.maritalStatus)}
            </span>
            <span className="bg-white/20 px-3 py-1 rounded-full text-sm">
              {getComplexionLabel(personalInfo.complexion)}
            </span>
          </div>
          <div className="text-marriage-100 text-sm">
            <p className="capitalize">{personalInfo.religion} • {personalInfo.caste || 'General'}</p>
          </div>
        </div>

        {/* Traditional Border */}
        <div className="absolute bottom-0 left-0 right-0 h-4 bg-gradient-to-r from-yellow-400 via-yellow-300 to-yellow-400"></div>
      </div>

      <div className="p-6">
        {/* Basic Information */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          <div className="bg-marriage-50 p-4 rounded-lg border border-marriage-200">
            <h3 className="font-semibold text-marriage-800 mb-3 flex items-center gap-2">
              <Star className="w-4 h-4" /> Personal Details
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
              <div className="flex justify-between">
                <span className="text-gray-600">Mother Tongue:</span>
                <span className="font-medium">{personalInfo.motherTongue}</span>
              </div>
            </div>
          </div>

          <div className="bg-marriage-50 p-4 rounded-lg border border-marriage-200">
            <h3 className="font-semibold text-marriage-800 mb-3 flex items-center gap-2">
              <Home className="w-4 h-4" /> Contact Information
            </h3>
            <div className="space-y-2 text-sm">
              <div className="flex items-center gap-2">
                <Phone className="w-4 h-4 text-marriage-600" />
                <span>{contactInfo.phone}</span>
              </div>
              {contactInfo.whatsapp && (
                <div className="flex items-center gap-2">
                  <span className="w-4 h-4 bg-green-500 rounded flex items-center justify-center text-white text-xs">W</span>
                  <span>{contactInfo.whatsapp}</span>
                </div>
              )}
              <div className="flex items-center gap-2">
                <Mail className="w-4 h-4 text-marriage-600" />
                <span>{contactInfo.email}</span>
              </div>
              <div className="flex items-start gap-2">
                <MapPin className="w-4 h-4 text-marriage-600 mt-0.5" />
                <span>{contactInfo.address}, {contactInfo.city}</span>
              </div>
            </div>
          </div>
        </div>

        {/* About Me */}
        {aboutMe && (
          <div className="mb-6">
            <h3 className="font-semibold text-marriage-800 mb-3 flex items-center gap-2">
              <BookOpen className="w-4 h-4" /> About Me
            </h3>
            <div className="bg-marriage-50 p-4 rounded-lg border border-marriage-200">
              <p className="text-gray-700 leading-relaxed text-sm">{aboutMe}</p>
            </div>
          </div>
        )}

        {/* Family Details */}
        <div className="mb-6">
          <h3 className="font-semibold text-marriage-800 mb-3 flex items-center gap-2">
            <Users className="w-4 h-4" /> Family Details
          </h3>
          <div className="bg-marriage-50 p-4 rounded-lg border border-marriage-200">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
              <div>
                <p className="text-gray-600 mb-1">Family Type:</p>
                <p className="font-medium capitalize">{familyInfo.familyType}</p>
              </div>
              <div>
                <p className="text-gray-600 mb-1">Family Status:</p>
                <p className="font-medium capitalize">{familyInfo.familyStatus.replace('_', ' ')}</p>
              </div>
              <div>
                <p className="text-gray-600 mb-1">Family Values:</p>
                <p className="font-medium capitalize">{familyInfo.familyValues}</p>
              </div>
              <div>
                <p className="text-gray-600 mb-1">Family Location:</p>
                <p className="font-medium">{familyInfo.familyLocation}</p>
              </div>
            </div>

            <div className="mt-4 pt-4 border-t border-marriage-200">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                <div>
                  <p className="font-medium text-marriage-700 mb-2">Father</p>
                  <p className="text-gray-700">{familyInfo.fatherName}</p>
                  <p className="text-gray-600 text-xs">{familyInfo.fatherOccupation}</p>
                </div>
                <div>
                  <p className="font-medium text-marriage-700 mb-2">Mother</p>
                  <p className="text-gray-700">{familyInfo.motherName}</p>
                  <p className="text-gray-600 text-xs">{familyInfo.motherOccupation}</p>
                </div>
              </div>
            </div>

            <div className="mt-4 pt-4 border-t border-marriage-200">
              <p className="font-medium text-marriage-700 mb-2">Siblings</p>
              <div className="flex gap-4 text-sm">
                <span>Brothers: {familyInfo.brothers} ({familyInfo.marriedBrothers} married)</span>
                <span>Sisters: {familyInfo.sisters} ({familyInfo.marriedSisters} married)</span>
              </div>
            </div>
          </div>
        </div>

        {/* Education & Occupation */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          <div>
            <h3 className="font-semibold text-marriage-800 mb-3 flex items-center gap-2">
              <GraduationCap className="w-4 h-4" /> Education
            </h3>
            <div className="space-y-3">
              {education.map((edu) => (
                <div key={edu.id} className="bg-marriage-50 p-3 rounded-lg border border-marriage-200 text-sm">
                  <p className="font-medium text-gray-900">{edu.degree}</p>
                  <p className="text-gray-600">{edu.institution}</p>
                  <p className="text-gray-500 text-xs">{edu.year} • {edu.percentage || edu.grade || ''}</p>
                </div>
              ))}
            </div>
          </div>

          <div>
            <h3 className="font-semibold text-marriage-800 mb-3 flex items-center gap-2">
              <Briefcase className="w-4 h-4" /> Occupation
            </h3>
            <div className="space-y-3">
              {occupation.map((occ) => (
                <div key={occ.id} className="bg-marriage-50 p-3 rounded-lg border border-marriage-200 text-sm">
                  <p className="font-medium text-gray-900">{occ.occupation}</p>
                  {occ.company && <p className="text-gray-600">{occ.company}</p>}
                  {occ.designation && <p className="text-gray-600 text-xs">{occ.designation}</p>}
                  <p className="text-gray-500 text-xs">{occ.annualIncome}</p>
                  <p className="text-gray-500 text-xs">{occ.workLocation}</p>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Horoscope */}
        {horoscope && horoscope.hasHoroscope && (
          <div className="mb-6">
            <h3 className="font-semibold text-marriage-800 mb-3 flex items-center gap-2">
              <Star className="w-4 h-4" /> Horoscope Details
            </h3>
            <div className="bg-marriage-50 p-4 rounded-lg border border-marriage-200">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                <div>
                  <p className="text-gray-600">Star:</p>
                  <p className="font-medium">{horoscope.star || 'N/A'}</p>
                </div>
                <div>
                  <p className="text-gray-600">Rashi:</p>
                  <p className="font-medium">{horoscope.rashi || 'N/A'}</p>
                </div>
                <div>
                  <p className="text-gray-600">Nakshatra:</p>
                  <p className="font-medium">{horoscope.nakshatra || 'N/A'}</p>
                </div>
                <div>
                  <p className="text-gray-600">Manglik:</p>
                  <p className="font-medium capitalize">{horoscope.manglik}</p>
                </div>
              </div>
              {horoscope.birthTime && (
                <div className="mt-3 pt-3 border-t border-marriage-200">
                  <p className="text-gray-600 text-sm">Birth Time: {horoscope.birthTime}</p>
                  <p className="text-gray-600 text-sm">Birth Place: {horoscope.birthPlace}</p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Lifestyle */}
        <div className="mb-6">
          <h3 className="font-semibold text-marriage-800 mb-3">Lifestyle & Preferences</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
            <div className="bg-marriage-50 p-3 rounded-lg border border-marriage-200">
              <p className="text-gray-600 mb-1">Diet:</p>
              <p className="font-medium capitalize">{lifestyle.diet.replace('_', ' ')}</p>
            </div>
            <div className="bg-marriage-50 p-3 rounded-lg border border-marriage-200">
              <p className="text-gray-600 mb-1">Smoking:</p>
              <p className="font-medium capitalize">{lifestyle.smoking}</p>
            </div>
            <div className="bg-marriage-50 p-3 rounded-lg border border-marriage-200">
              <p className="text-gray-600 mb-1">Drinking:</p>
              <p className="font-medium capitalize">{lifestyle.drinking}</p>
            </div>
            <div className="bg-marriage-50 p-3 rounded-lg border border-marriage-200">
              <p className="text-gray-600 mb-1">Dress Style:</p>
              <p className="font-medium capitalize">{lifestyle.dressStyle}</p>
            </div>
          </div>
        </div>

        {/* Expectations */}
        {expectations && (
          <div className="mb-6">
            <h3 className="font-semibold text-marriage-800 mb-3">Partner Expectations</h3>
            <div className="bg-marriage-50 p-4 rounded-lg border border-marriage-200">
              <p className="text-gray-700 leading-relaxed text-sm">{expectations}</p>
            </div>
          </div>
        )}

        {/* Traditional Footer */}
        <div className="text-center text-xs text-marriage-600 mt-8 pt-4 border-t border-marriage-200">
          <p>॥ सूचना: यह जानकारी केवल विवाह हेतु है ॥</p>
          <p className="mt-1">Information for matrimonial purposes only</p>
        </div>
      </div>
    </div>
  );
};

export default TraditionalTemplate;