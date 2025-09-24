import React from 'react';
import { useTranslation } from 'react-i18next';
import { MarriageBiodata } from '../../../../types/marriage';

interface BengaliTemplateProps {
  data: MarriageBiodata;
  className?: string;
}

export const BengaliTemplate: React.FC<BengaliTemplateProps> = ({
  data,
  className = ''
}) => {
  const { t } = useTranslation();

  return (
    <div
      className={`bg-gradient-to-br from-pink-50 to-red-50 p-8 min-h-screen ${className}`}
      style={{ fontFamily: "'Noto Sans Bengali', sans-serif" }}
    >
      {/* Traditional Bengali Border with Alpona Design */}
      <div className="border-4 border-red-700 rounded-lg p-6 bg-white relative overflow-hidden">

        {/* Alpona Pattern */}
        <div className="absolute top-0 left-0 w-full h-full opacity-3">
          <div className="text-6xl text-red-200 transform rotate-12">
            বিবাহ
          </div>
        </div>

        {/* Header with Bengali Traditional Design */}
        <div className="text-center mb-8 relative z-10">
          <div className="bg-red-600 text-white py-4 rounded-lg mb-4">
            <h1 className="text-3xl font-bold">
              বিবাহ বাযোডাটা
            </h1>
            <p className="text-lg mt-1">Marriage Biodata</p>
          </div>
          <div className="flex justify-center space-x-1">
            <div className="w-20 h-1 bg-red-600"></div>
            <div className="w-3 h-1 bg-yellow-400"></div>
            <div className="w-20 h-1 bg-red-600"></div>
          </div>
        </div>

        {/* Personal Information */}
        <div className="mb-8 relative z-10">
          <div className="bg-red-100 p-3 rounded-t-lg border-l-4 border-red-600">
            <h2 className="text-xl font-bold text-red-800">
              ব্যক্তিগত তথ্য (Personal Information)
            </h2>
          </div>
          <div className="bg-red-50 p-4 rounded-b-lg">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="bg-white p-3 rounded shadow-sm border-l-4 border-red-400">
                <strong className="text-red-700">পূর্ণ নাম (Name):</strong> {data.personalInfo.fullName}
              </div>
              <div className="bg-white p-3 rounded shadow-sm border-l-4 border-red-400">
                <strong className="text-red-700">বয়স (Age):</strong> {data.personalInfo.age} বছর
              </div>
              <div className="bg-white p-3 rounded shadow-sm border-l-4 border-red-400">
                <strong className="text-red-700">জন্ম তারিখ (DOB):</strong> {data.personalInfo.dateOfBirth}
              </div>
              <div className="bg-white p-3 rounded shadow-sm border-l-4 border-red-400">
                <strong className="text-red-700">উচ্চতা (Height):</strong> {data.personalInfo.height}
              </div>
              <div className="bg-white p-3 rounded shadow-sm border-l-4 border-red-400">
                <strong className="text-red-700">গাত্রবর্ণ (Complexion):</strong> {t(`personal.${data.personalInfo.complexion}`)}
              </div>
              <div className="bg-white p-3 rounded shadow-sm border-l-4 border-red-400">
                <strong className="text-red-700">ধর্ম (Religion):</strong> {data.personalInfo.religion}
              </div>
              <div className="bg-white p-3 rounded shadow-sm border-l-4 border-red-400">
                <strong className="text-red-700">সম্প্রদায় (Caste):</strong> {data.personalInfo.caste}
              </div>
              <div className="bg-white p-3 rounded shadow-sm border-l-4 border-red-400">
                <strong className="text-red-700">পেশা (Occupation):</strong> {data.occupation[0]?.occupation || 'N/A'}
              </div>
            </div>
          </div>
        </div>

        {/* Family Information */}
        <div className="mb-8 relative z-10">
          <div className="bg-red-100 p-3 rounded-t-lg border-l-4 border-red-600">
            <h2 className="text-xl font-bold text-red-800">
              পারিবারিক তথ্য (Family Information)
            </h2>
          </div>
          <div className="bg-red-50 p-4 rounded-b-lg">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="bg-white p-3 rounded shadow-sm border-l-4 border-red-400">
                <strong className="text-red-700">পিতার নাম (Father):</strong> {data.familyInfo.fatherName}
              </div>
              <div className="bg-white p-3 rounded shadow-sm border-l-4 border-red-400">
                <strong className="text-red-700">পিতার পেশা (Father's Occ.):</strong> {data.familyInfo.fatherOccupation}
              </div>
              <div className="bg-white p-3 rounded shadow-sm border-l-4 border-red-400">
                <strong className="text-red-700">মাতার নাম (Mother):</strong> {data.familyInfo.motherName}
              </div>
              <div className="bg-white p-3 rounded shadow-sm border-l-4 border-red-400">
                <strong className="text-red-700">মাতার পেশা (Mother's Occ.):</strong> {data.familyInfo.motherOccupation}
              </div>
              <div className="bg-white p-3 rounded shadow-sm border-l-4 border-red-400">
                <strong className="text-red-700">ভাই (Brothers):</strong> {data.familyInfo.brothers} জন
              </div>
              <div className="bg-white p-3 rounded shadow-sm border-l-4 border-red-400">
                <strong className="text-red-700">বোন (Sisters):</strong> {data.familyInfo.sisters} জন
              </div>
              <div className="bg-white p-3 rounded shadow-sm border-l-4 border-red-400">
                <strong className="text-red-700">পারিবারিক অবস্থা (Status):</strong> {t(`family.${data.familyInfo.familyStatus}`)}
              </div>
              <div className="bg-white p-3 rounded shadow-sm border-l-4 border-red-400">
                <strong className="text-red-700">বসবাস (Location):</strong> {data.familyInfo.familyLocation}
              </div>
            </div>
          </div>
        </div>

        {/* Education */}
        <div className="mb-8 relative z-10">
          <div className="bg-red-100 p-3 rounded-t-lg border-l-4 border-red-600">
            <h2 className="text-xl font-bold text-red-800">
              শিক্ষাগত যোগ্যতা (Education)
            </h2>
          </div>
          <div className="bg-red-50 p-4 rounded-b-lg">
            {data.education.map((edu) => (
              <div key={edu.id} className="bg-white p-4 rounded shadow-sm mb-3 border-l-4 border-red-400">
                <div className="flex justify-between items-start">
                  <div>
                    <div className="font-bold text-lg text-red-800">{edu.degree}</div>
                    <div className="text-gray-600">{edu.institution}</div>
                    <div className="text-sm text-gray-500">{edu.board} • {edu.year}</div>
                  </div>
                  <div className="text-right">
                    <div className="bg-red-100 text-red-800 px-2 py-1 rounded text-sm font-semibold">
                      {edu.percentage || edu.grade}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Horoscope with Bengali Astrology */}
        {data.horoscope && data.horoscope.hasHoroscope && (
          <div className="mb-8 relative z-10">
            <div className="bg-red-100 p-3 rounded-t-lg border-l-4 border-red-600">
              <h2 className="text-xl font-bold text-red-800">
                রাশিফলের বিবরণ (Horoscope Details)
              </h2>
            </div>
            <div className="bg-red-50 p-4 rounded-b-lg">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="bg-white p-3 rounded shadow-sm border-l-4 border-red-400">
                  <strong className="text-red-700">জন্ম সময় (Birth Time):</strong> {data.horoscope.birthTime}
                </div>
                <div className="bg-white p-3 rounded shadow-sm border-l-4 border-red-400">
                  <strong className="text-red-700">জন্মস্থান (Birth Place):</strong> {data.horoscope.birthPlace || data.personalInfo.birthPlace}
                </div>
                <div className="bg-white p-3 rounded shadow-sm border-l-4 border-red-400">
                  <strong className="text-red-700">নক্ষত্র (Nakshatra):</strong> {data.horoscope.nakshatra}
                </div>
                <div className="bg-white p-3 rounded shadow-sm border-l-4 border-red-400">
                  <strong className="text-red-700">রাশি (Rashi):</strong> {data.horoscope.rashi}
                </div>
                <div className="bg-white p-3 rounded shadow-sm border-l-4 border-red-400">
                  <strong className="text-red-700">গণণা (Ganana):</strong> {data.horoscope.manglik}
                </div>
                <div className="bg-white p-3 rounded shadow-sm border-l-4 border-red-400">
                  <strong className="text-red-700">দোষ (Dosha):</strong> {data.horoscope.dosh?.join(', ') || 'নেই'}
                </div>
              </div>

              {/* Bengali Match Making */}
              <div className="mt-4 p-4 bg-yellow-50 rounded-lg border border-yellow-200">
                <h3 className="font-bold text-red-700 mb-2">গুণ মিলান (Gun Milan)</h3>
                <p className="text-sm text-gray-700">
                  বর্ণ, বশ্য, তুষ্টি, দীন, যোগ, গণ, ভক্ত, নাড়ী - এই আটটি গুণের উপর ভিত্তি করে কুণ্ডলী মিলন করা হয়।
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Partner Preferences */}
        <div className="mb-8 relative z-10">
          <div className="bg-red-100 p-3 rounded-t-lg border-l-4 border-red-600">
            <h2 className="text-xl font-bold text-red-800">
              জীবনসঙ্গীর পছন্দ (Partner Preferences)
            </h2>
          </div>
          <div className="bg-red-50 p-4 rounded-b-lg">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="bg-white p-3 rounded shadow-sm border-l-4 border-red-400">
                <strong className="text-red-700">বয়স (Age):</strong> {data.partnerPreference.ageRange.min} - {data.partnerPreference.ageRange.max} বছর
              </div>
              <div className="bg-white p-3 rounded shadow-sm border-l-4 border-red-400">
                <strong className="text-red-700">উচ্চতা (Height):</strong> {data.partnerPreference.heightRange.min} - {data.partnerPreference.heightRange.max}
              </div>
              <div className="bg-white p-3 rounded shadow-sm border-l-4 border-red-400">
                <strong className="text-red-700">শিক্ষা (Education):</strong> {data.partnerPreference.education.join(', ')}
              </div>
              <div className="bg-white p-3 rounded shadow-sm border-l-4 border-red-400">
                <strong className="text-red-700">পেশা (Occupation):</strong> {data.partnerPreference.occupation.join(', ')}
              </div>
            </div>
            <div className="mt-4 bg-white p-3 rounded shadow-sm border-l-4 border-red-400">
              <strong className="text-red-700">অন্যান্য পছন্দ:</strong>
              <p className="mt-2 text-gray-700">{data.partnerPreference.additionalPreferences}</p>
            </div>
          </div>
        </div>

        {/* Contact Information */}
        <div className="mb-8 relative z-10">
          <div className="bg-red-100 p-3 rounded-t-lg border-l-4 border-red-600">
            <h2 className="text-xl font-bold text-red-800">
              যোগাযোগের ঠিকানা (Contact Information)
            </h2>
          </div>
          <div className="bg-red-50 p-4 rounded-b-lg">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="bg-white p-3 rounded shadow-sm border-l-4 border-red-400">
                <strong className="text-red-700">ফোন (Phone):</strong> {data.contactInfo.phone}
              </div>
              <div className="bg-white p-3 rounded shadow-sm border-l-4 border-red-400">
                <strong className="text-red-700">ইমেল (Email):</strong> {data.contactInfo.email}
              </div>
              <div className="bg-white p-3 rounded shadow-sm border-l-4 border-red-400">
                <strong className="text-red-700">ঠিকানা (Address):</strong> {data.contactInfo.address}
              </div>
              <div className="bg-white p-3 rounded shadow-sm border-l-4 border-red-400">
                <strong className="text-red-700">জেলা/শহর (District/City):</strong> {data.contactInfo.city}
              </div>
            </div>
          </div>
        </div>

        {/* Traditional Bengali Footer */}
        <div className="text-center mt-8 pt-6 border-t-2 border-red-300 relative z-10">
          <div className="bg-red-600 text-white py-3 px-6 rounded-lg inline-block mb-3">
            <p className="text-lg font-semibold">
              সুখী দাম্পত্য জীবন হোক
            </p>
            <p className="text-sm">শুভ বিবাহ</p>
          </div>
          <p className="text-xs text-gray-500">
            তৈরির তারিখ: {new Date().toLocaleDateString('bn-BD', { year: 'numeric', month: 'long', day: 'numeric' })}
          </p>
        </div>

      </div>
    </div>
  );
};