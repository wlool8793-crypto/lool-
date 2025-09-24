import React from 'react';
import { useTranslation } from 'react-i18next';
import { MarriageBiodata } from '../../../../types/marriage';

interface NorthIndianTemplateProps {
  data: MarriageBiodata;
  className?: string;
}

export const NorthIndianTemplate: React.FC<NorthIndianTemplateProps> = ({
  data,
  className = ''
}) => {
  const { t } = useTranslation();

  return (
    <div
      className={`bg-gradient-to-br from-red-50 to-orange-50 p-8 min-h-screen ${className}`}
      style={{ fontFamily: "'Noto Sans Devanagari', sans-serif" }}
    >
      {/* Traditional North Indian Border */}
      <div className="border-4 border-red-800 border-double rounded-lg p-6 bg-white">

        {/* Header with Traditional Design */}
        <div className="text-center mb-8 relative">
          <div className="absolute inset-x-0 top-0 h-1 bg-gradient-to-r from-red-600 via-yellow-500 to-red-600"></div>
          <h1 className="text-3xl font-bold text-red-800 mt-6 mb-2">
            {t('marriage')} {t('biodata')}
          </h1>
          <p className="text-gray-600">शादी का बायोडाटा</p>
          <div className="absolute inset-x-0 bottom-0 h-1 bg-gradient-to-r from-red-600 via-yellow-500 to-red-600"></div>
        </div>

        {/* Personal Information */}
        <div className="mb-8">
          <div className="bg-red-100 p-3 rounded-t-lg">
            <h2 className="text-xl font-bold text-red-800 text-center">
              व्यक्तिगत जानकारी (Personal Information)
            </h2>
          </div>
          <div className="bg-gray-50 p-4 rounded-b-lg border-l-4 border-red-600">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <strong>पूरा नाम (Full Name):</strong> {data.personalInfo.fullName}
              </div>
              <div>
                <strong>आयु (Age):</strong> {data.personalInfo.age} वर्ष
              </div>
              <div>
                <strong>जन्म तिथि (Date of Birth):</strong> {data.personalInfo.dateOfBirth}
              </div>
              <div>
                <strong>ऊंचाई (Height):</strong> {data.personalInfo.height}
              </div>
              <div>
                <strong>रंगत (Complexion):</strong> {t(`personal.${data.personalInfo.complexion}`)}
              </div>
              <div>
                <strong>शारीरिक बनावट (Body Type):</strong> {t(`personal.${data.personalInfo.bodyType}`)}
              </div>
              <div>
                <strong>धर्म (Religion):</strong> {data.personalInfo.religion}
              </div>
              <div>
                <strong>जाति (Caste):</strong> {data.personalInfo.caste}
              </div>
            </div>
          </div>
        </div>

        {/* Family Information */}
        <div className="mb-8">
          <div className="bg-red-100 p-3 rounded-t-lg">
            <h2 className="text-xl font-bold text-red-800 text-center">
              पारिवारिक जानकारी (Family Information)
            </h2>
          </div>
          <div className="bg-gray-50 p-4 rounded-b-lg border-l-4 border-red-600">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <strong>पिता का नाम (Father's Name):</strong> {data.familyInfo.fatherName}
              </div>
              <div>
                <strong>पिता का व्यवसाय (Father's Occupation):</strong> {data.familyInfo.fatherOccupation}
              </div>
              <div>
                <strong>माता का नाम (Mother's Name):</strong> {data.familyInfo.motherName}
              </div>
              <div>
                <strong>माता का व्यवसाय (Mother's Occupation):</strong> {data.familyInfo.motherOccupation}
              </div>
              <div>
                <strong>भाई (Brothers):</strong> {data.familyInfo.brothers} ({data.familyInfo.marriedBrothers} विवाहित)
              </div>
              <div>
                <strong>बहनें (Sisters):</strong> {data.familyInfo.sisters} ({data.familyInfo.marriedSisters} विवाहित)
              </div>
              <div>
                <strong>पारिवारिक स्थिति (Family Status):</strong> {t(`family.${data.familyInfo.familyStatus}`)}
              </div>
              <div>
                <strong>परिवार का प्रकार (Family Type):</strong> {t(`family.${data.familyInfo.familyType}`)}
              </div>
            </div>
          </div>
        </div>

        {/* Education */}
        <div className="mb-8">
          <div className="bg-red-100 p-3 rounded-t-lg">
            <h2 className="text-xl font-bold text-red-800 text-center">
              शिक्षा (Education)
            </h2>
          </div>
          <div className="bg-gray-50 p-4 rounded-b-lg border-l-4 border-red-600">
            {data.education.map((edu, index) => (
              <div key={edu.id} className="mb-3 last:mb-0">
                <div className="font-semibold">{edu.degree} - {edu.institution}</div>
                <div className="text-sm text-gray-600">
                  {edu.year} | {edu.percentage || edu.grade}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Horoscope Section */}
        {data.horoscope && data.horoscope.hasHoroscope && (
          <div className="mb-8">
            <div className="bg-red-100 p-3 rounded-t-lg">
              <h2 className="text-xl font-bold text-red-800 text-center">
                कुंडली विवरण (Horoscope Details)
              </h2>
            </div>
            <div className="bg-gray-50 p-4 rounded-b-lg border-l-4 border-red-600">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <strong>जन्म समय (Birth Time):</strong> {data.horoscope.birthTime}
                </div>
                <div>
                  <strong>नक्षत्र (Nakshatra):</strong> {data.horoscope.nakshatra}
                </div>
                <div>
                  <strong>राशि (Rashi):</strong> {data.horoscope.rashi}
                </div>
                <div>
                  <strong>मंगलिक (Manglik):</strong> {t(`horoscope.${data.horoscope.manglik}`)}
                </div>
                <div>
                  <strong>गोत्र (Gotra):</strong> {data.horoscope.gotra}
                </div>
                <div>
                  <strong>नाड़ी (Nadi):</strong> {data.horoscope.nadi}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Partner Preferences */}
        <div className="mb-8">
          <div className="bg-red-100 p-3 rounded-t-lg">
            <h2 className="text-xl font-bold text-red-800 text-center">
              जीवनसाथी की अपेक्षाएं (Partner Expectations)
            </h2>
          </div>
          <div className="bg-gray-50 p-4 rounded-b-lg border-l-4 border-red-600">
            <div className="mb-3">
              <strong>आयु सीमा (Age Range):</strong> {data.partnerPreference.ageRange.min} - {data.partnerPreference.ageRange.max} वर्ष
            </div>
            <div className="mb-3">
              <strong>शिक्षा (Education):</strong> {data.partnerPreference.education.join(', ')}
            </div>
            <div className="mb-3">
              <strong>व्यवसाय (Occupation):</strong> {data.partnerPreference.occupation.join(', ')}
            </div>
            <div>
              <strong>अतिरिक्त प्राथमिकताएं:</strong>
              <p className="mt-2 text-gray-700">{data.partnerPreference.additionalPreferences}</p>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="text-center mt-8 pt-4 border-t-2 border-red-200">
          <p className="text-sm text-gray-600">
            भगवान करें आपको उपयुक्त जीवनसाथी मिले |
          </p>
          <p className="text-xs text-gray-500 mt-2">
            Generated on {new Date().toLocaleDateString()}
          </p>
        </div>

      </div>
    </div>
  );
};