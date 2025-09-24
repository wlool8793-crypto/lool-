import React from 'react';
import { useTranslation } from 'react-i18next';
import { MarriageBiodata } from '../../../../types/marriage';

interface SouthIndianTemplateProps {
  data: MarriageBiodata;
  className?: string;
}

export const SouthIndianTemplate: React.FC<SouthIndianTemplateProps> = ({
  data,
  className = ''
}) => {
  const { t } = useTranslation();

  return (
    <div
      className={`bg-gradient-to-br from-yellow-50 to-orange-50 p-8 min-h-screen ${className}`}
      style={{ fontFamily: "'Noto Sans Tamil', sans-serif" }}
    >
      {/* Traditional South Indian Border with Kolam Design */}
      <div className="border-4 border-orange-700 rounded-lg p-6 bg-white relative overflow-hidden">

        {/* Kolam Pattern */}
        <div className="absolute top-0 left-0 w-full h-full opacity-5">
          <div className="grid grid-cols-8 gap-4">
            {Array.from({ length: 64 }).map((_, i) => (
              <div key={i} className="w-8 h-8 border border-orange-300 rounded-full"></div>
            ))}
          </div>
        </div>

        {/* Header with Traditional South Indian Design */}
        <div className="text-center mb-8 relative z-10">
          <div className="bg-orange-700 text-white py-3 rounded-lg mb-4">
            <h1 className="text-3xl font-bold">
              {t('marriage')} {t('biodata')}
            </h1>
            <p className="text-lg mt-1">திருமண விளக்கப்பட்டியல்</p>
          </div>
          <div className="flex justify-center space-x-2">
            <div className="w-16 h-1 bg-orange-600"></div>
            <div className="w-8 h-1 bg-yellow-500"></div>
            <div className="w-16 h-1 bg-orange-600"></div>
          </div>
        </div>

        {/* Personal Information */}
        <div className="mb-8 relative z-10">
          <div className="bg-orange-100 p-3 rounded-t-lg border-l-4 border-orange-600">
            <h2 className="text-xl font-bold text-orange-800">
              தனிப்பட்ட தகவல்கள் (Personal Information)
            </h2>
          </div>
          <div className="bg-orange-50 p-4 rounded-b-lg">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="bg-white p-3 rounded shadow-sm">
                <strong className="text-orange-700">பெயர் (Name):</strong> {data.personalInfo.fullName}
              </div>
              <div className="bg-white p-3 rounded shadow-sm">
                <strong className="text-orange-700">வயது (Age):</strong> {data.personalInfo.age}
              </div>
              <div className="bg-white p-3 rounded shadow-sm">
                <strong className="text-orange-700">பிறந்த தேதி (DOB):</strong> {data.personalInfo.dateOfBirth}
              </div>
              <div className="bg-white p-3 rounded shadow-sm">
                <strong className="text-orange-700">உயரம் (Height):</strong> {data.personalInfo.height}
              </div>
              <div className="bg-white p-3 rounded shadow-sm">
                <strong className="text-orange-700">சமூகம் (Caste):</strong> {data.personalInfo.caste}
              </div>
              <div className="bg-white p-3 rounded shadow-sm">
                <strong className="text-orange-700">கோத்திரம் (Gotra):</strong> {data.horoscope?.gotra || 'N/A'}
              </div>
              <div className="bg-white p-3 rounded shadow-sm">
                <strong className="text-orange-700">நட்சத்திரம் (Star):</strong> {data.horoscope?.nakshatra || 'N/A'}
              </div>
              <div className="bg-white p-3 rounded shadow-sm">
                <strong className="text-orange-700">ராசி (Rashi):</strong> {data.horoscope?.rashi || 'N/A'}
              </div>
            </div>
          </div>
        </div>

        {/* Family Information */}
        <div className="mb-8 relative z-10">
          <div className="bg-orange-100 p-3 rounded-t-lg border-l-4 border-orange-600">
            <h2 className="text-xl font-bold text-orange-800">
              குடும்பத் தகவல்கள் (Family Information)
            </h2>
          </div>
          <div className="bg-orange-50 p-4 rounded-b-lg">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="bg-white p-3 rounded shadow-sm">
                <strong className="text-orange-700">தந்தை பெயர் (Father):</strong> {data.familyInfo.fatherName}
              </div>
              <div className="bg-white p-3 rounded shadow-sm">
                <strong className="text-orange-700">தொழில் (Occupation):</strong> {data.familyInfo.fatherOccupation}
              </div>
              <div className="bg-white p-3 rounded shadow-sm">
                <strong className="text-orange-700">தாய் பெயர் (Mother):</strong> {data.familyInfo.motherName}
              </div>
              <div className="bg-white p-3 rounded shadow-sm">
                <strong className="text-orange-700">தொழில் (Occupation):</strong> {data.familyInfo.motherOccupation}
              </div>
              <div className="bg-white p-3 rounded shadow-sm">
                <strong className="text-orange-700">சகோதரர்கள் (Brothers):</strong> {data.familyInfo.brothers}
              </div>
              <div className="bg-white p-3 rounded shadow-sm">
                <strong className="text-orange-700">சகோதரிகள் (Sisters):</strong> {data.familyInfo.sisters}
              </div>
              <div className="bg-white p-3 rounded shadow-sm">
                <strong className="text-orange-700">குடும்ப நிலை (Status):</strong> {t(`family.${data.familyInfo.familyStatus}`)}
              </div>
              <div className="bg-white p-3 rounded shadow-sm">
                <strong className="text-orange-700">வகை (Type):</strong> {t(`family.${data.familyInfo.familyType}`)}
              </div>
            </div>
          </div>
        </div>

        {/* Education and Career */}
        <div className="mb-8 relative z-10">
          <div className="bg-orange-100 p-3 rounded-t-lg border-l-4 border-orange-600">
            <h2 className="text-xl font-bold text-orange-800">
              கல்வி மற்றும் தொழில் (Education & Career)
            </h2>
          </div>
          <div className="bg-orange-50 p-4 rounded-b-lg">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Education */}
              <div>
                <h3 className="font-semibold text-orange-700 mb-3">கல்வி (Education)</h3>
                {data.education.map((edu) => (
                  <div key={edu.id} className="bg-white p-3 rounded shadow-sm mb-2">
                    <div className="font-semibold">{edu.degree}</div>
                    <div className="text-sm text-gray-600">{edu.institution}</div>
                    <div className="text-xs text-gray-500">{edu.year} | {edu.percentage || edu.grade}</div>
                  </div>
                ))}
              </div>

              {/* Occupation */}
              <div>
                <h3 className="font-semibold text-orange-700 mb-3">தொழில் (Occupation)</h3>
                {data.occupation.map((occ) => (
                  <div key={occ.id} className="bg-white p-3 rounded shadow-sm mb-2">
                    <div className="font-semibold">{occ.designation || occ.occupation}</div>
                    <div className="text-sm text-gray-600">{occ.company || occ.industry}</div>
                    <div className="text-xs text-gray-500">{occ.workLocation}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Detailed Horoscope */}
        {data.horoscope && data.horoscope.hasHoroscope && (
          <div className="mb-8 relative z-10">
            <div className="bg-orange-100 p-3 rounded-t-lg border-l-4 border-orange-600">
              <h2 className="text-xl font-bold text-orange-800">
                ஜாதக விவரங்கள் (Horoscope Details)
              </h2>
            </div>
            <div className="bg-orange-50 p-4 rounded-b-lg">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="bg-white p-3 rounded shadow-sm">
                  <strong className="text-orange-700">பிறந்த நேரம் (Birth Time):</strong> {data.horoscope.birthTime}
                </div>
                <div className="bg-white p-3 rounded shadow-sm">
                  <strong className="text-orange-700">பிறந்த இடம் (Birth Place):</strong> {data.horoscope.birthPlace || data.personalInfo.birthPlace}
                </div>
                <div className="bg-white p-3 rounded shadow-sm">
                  <strong className="text-orange-700">நட்சத்திரம் (Nakshatra):</strong> {data.horoscope.nakshatra}
                </div>
                <div className="bg-white p-3 rounded shadow-sm">
                  <strong className="text-orange-700">ராசி (Rashi):</strong> {data.horoscope.rashi}
                </div>
                <div className="bg-white p-3 rounded shadow-sm">
                  <strong className="text-orange-700">லக்னம் (Lagnam):</strong> {data.horoscope.star}
                </div>
                <div className="bg-white p-3 rounded shadow-sm">
                  <strong className="text-orange-700">சேவை/தோஷம் (Dosham):</strong> {data.horoscope.dosh?.join(', ') || 'இல்லை'}
                </div>
              </div>

              {/* Jathagam Matching Details */}
              <div className="mt-4 p-4 bg-yellow-50 rounded-lg border border-yellow-200">
                <h3 className="font-semibold text-orange-700 mb-2">ஜாதக பொருத்தம் (Horoscope Matching)</h3>
                <p className="text-sm text-gray-700">
                  தசை: குரு, ரேவதி, யோனி, ராசி, ரச்யாதிபதி, வேதை, வசிய, மகேந்திரம், ஸ்திரீ தீர்க்கம், புத்திர பாக்கியம் ஆகியவற்றின் அடிப்படையில் பொருத்தம் பார்க்கப்படும்.
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Contact Information */}
        <div className="mb-8 relative z-10">
          <div className="bg-orange-100 p-3 rounded-t-lg border-l-4 border-orange-600">
            <h2 className="text-xl font-bold text-orange-800">
              தொடர்பு தகவல்கள் (Contact Information)
            </h2>
          </div>
          <div className="bg-orange-50 p-4 rounded-b-lg">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="bg-white p-3 rounded shadow-sm">
                <strong className="text-orange-700">தொலைபேசி (Phone):</strong> {data.contactInfo.phone}
              </div>
              <div className="bg-white p-3 rounded shadow-sm">
                <strong className="text-orange-700">மின்னஞ்சல் (Email):</strong> {data.contactInfo.email}
              </div>
              <div className="bg-white p-3 rounded shadow-sm">
                <strong className="text-orange-700">முகவரி (Address):</strong> {data.contactInfo.address}
              </div>
              <div className="bg-white p-3 rounded shadow-sm">
                <strong className="text-orange-700">வாட்ஸ்அப் (WhatsApp):</strong> {data.contactInfo.whatsapp || data.contactInfo.phone}
              </div>
            </div>
          </div>
        </div>

        {/* Traditional Footer */}
        <div className="text-center mt-8 pt-6 border-t-2 border-orange-300 relative z-10">
          <div className="bg-orange-700 text-white py-2 px-4 rounded-lg inline-block">
            <p className="text-sm">
              வாழ்க வளமுடன்! | வாழ்க வளமுடன்!
            </p>
          </div>
          <p className="text-xs text-gray-500 mt-3">
            Generated on {new Date().toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })}
          </p>
        </div>

      </div>
    </div>
  );
};