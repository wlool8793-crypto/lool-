import React, { useState, useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import { Upload, Moon, Star, Zap, Calendar, MapPin, Calculator, Heart } from 'lucide-react';
import { Button } from '../ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Input } from '../ui/Input';
import { MarriageHoroscope } from '../../types/marriage';
import { cn } from '../../lib/utils';

interface HoroscopeIntegrationProps {
  data: MarriageHoroscope;
  onChange: (data: MarriageHoroscope) => void;
  className?: string;
}

interface KundliMatch {
  varna: number;
  vashya: number;
  tara: number;
  yoni: number;
  grahaMaitri: number;
  gana: number;
  bhakoot: number;
  nadi: number;
  total: number;
  compatibility: string;
  manglikStatus: string;
}

const nakshatras = [
  'Ashwini', 'Bharani', 'Krittika', 'Rohini', 'Mrigashira', 'Ardra',
  'Punarvasu', 'Pushya', 'Ashlesha', 'Magha', 'Purva Phalguni', 'Uttara Phalguni',
  'Hasta', 'Chitra', 'Swati', 'Vishakha', 'Anuradha', 'Jyeshtha',
  'Mula', 'Purva Ashadha', 'Uttara Ashadha', 'Shravana', 'Dhanishta', 'Shatabhisha',
  'Purva Bhadrapada', 'Uttara Bhadrapada', 'Revati'
];

const rashis = [
  'Mesha (Aries)', 'Vrishabha (Taurus)', 'Mithuna (Gemini)', 'Karka (Cancer)',
  'Simha (Leo)', 'Kanya (Virgo)', 'Tula (Libra)', 'Vrishchika (Scorpio)',
  'Dhanu (Sagittarius)', 'Makara (Capricorn)', 'Kumbha (Aquarius)', 'Meena (Pisces)'
];

const gotras = [
  'Kashyapa', 'Vasistha', 'Bharadvaja', 'Gautama', 'Atri', 'Vishvamitra',
  'Jamadagni', 'Bhrigu', 'Angirasa', 'Atri', 'Pulastya', 'Pulaha', 'Kratu'
];

export const HoroscopeIntegration: React.FC<HoroscopeIntegrationProps> = ({
  data,
  onChange,
  className = ''
}) => {
  const { t } = useTranslation();
  const [kundliFile, setKundliFile] = useState<File | null>(null);
  const [kundliPreview, setKundliPreview] = useState<string>('');
  const [compatibilityScore, setCompatibilityScore] = useState<KundliMatch | null>(null);

  const handleFileUpload = useCallback(async (file: File) => {
    if (!file.type.startsWith('image/')) {
      alert('Please upload an image file');
      return;
    }

    setKundliFile(file);

    // Create preview
    const reader = new FileReader();
    reader.onload = (e) => {
      setKundliPreview(e.target?.result as string);
    };
    reader.readAsDataURL(file);
  }, []);

  const calculateHoroscope = useCallback(() => {
    // Mock horoscope calculation based on birth details
    if (data.birthTime && data.birthPlace) {
      const randomNakshatra = nakshatras[Math.floor(Math.random() * nakshatras.length)];
      const randomRashi = rashis[Math.floor(Math.random() * rashis.length)];
      const randomGotra = gotras[Math.floor(Math.random() * gotras.length)];

      onChange({
        ...data,
        nakshatra: randomNakshatra,
        rashi: randomRashi,
        gotra: randomGotra,
        star: randomNakshatra,
        nadi: Math.random() > 0.5 ? 'Aadi' : 'Madhya'
      });
    }
  }, [data, onChange]);

  const calculateKundliMatch = useCallback(() => {
    // Mock Kundli matching calculation
    const match: KundliMatch = {
      varna: Math.floor(Math.random() * 3) + 1,
      vashya: Math.floor(Math.random() * 3) + 1,
      tara: Math.floor(Math.random() * 3) + 1,
      yoni: Math.floor(Math.random() * 3) + 1,
      grahaMaitri: Math.floor(Math.random() * 3) + 1,
      gana: Math.floor(Math.random() * 3) + 1,
      bhakoot: Math.floor(Math.random() * 3) + 1,
      nadi: Math.floor(Math.random() * 3) + 1,
      total: 0,
      compatibility: '',
      manglikStatus: data.manglik
    };

    match.total = match.varna + match.vashya + match.tara + match.yoni +
                   match.grahaMaitri + match.gana + match.bhakoot + match.nadi;

    match.compatibility = match.total >= 24 ? 'Excellent' :
                        match.total >= 18 ? 'Very Good' :
                        match.total >= 12 ? 'Good' : 'Poor';

    setCompatibilityScore(match);
  }, [data.manglik]);

  return (
    <div className={cn('space-y-6', className)}>
      {/* Horoscope Toggle */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Moon className="h-5 w-5" />
            {t('horoscope.has_horoscope')}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center space-x-4">
            <label className="flex items-center space-x-2">
              <input
                type="radio"
                name="hasHoroscope"
                checked={data.hasHoroscope}
                onChange={() => onChange({ ...data, hasHoroscope: true })}
                className="text-primary"
              />
              <span>{t('horoscope.yes')}</span>
            </label>
            <label className="flex items-center space-x-2">
              <input
                type="radio"
                name="hasHoroscope"
                checked={!data.hasHoroscope}
                onChange={() => onChange({ ...data, hasHoroscope: false })}
                className="text-primary"
              />
              <span>{t('horoscope.no')}</span>
            </label>
          </div>
        </CardContent>
      </Card>

      {data.hasHoroscope && (
        <>
          {/* Kundli Upload */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Upload className="h-5 w-5" />
                Upload Kundli/Horoscope Chart
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
                {kundliPreview ? (
                  <div className="space-y-4">
                    <img
                      src={kundliPreview}
                      alt="Kundli Chart"
                      className="max-w-sm mx-auto rounded-lg shadow-md"
                    />
                    <div className="flex justify-center space-x-2">
                      <Button
                        variant="outline"
                        onClick={() => {
                          setKundliFile(null);
                          setKundliPreview('');
                        }}
                      >
                        Remove
                      </Button>
                      <Button variant="outline">
                        Change
                      </Button>
                    </div>
                  </div>
                ) : (
                  <div className="space-y-4">
                    <Upload className="h-12 w-12 mx-auto text-gray-400" />
                    <div>
                      <label className="cursor-pointer">
                        <span className="mt-2 block text-sm font-medium text-gray-900">
                          Upload Kundli Image
                        </span>
                        <input
                          type="file"
                          className="sr-only"
                          accept="image/*"
                          onChange={(e) => {
                            const file = e.target.files?.[0];
                            if (file) handleFileUpload(file);
                          }}
                        />
                      </label>
                      <p className="mt-1 text-xs text-gray-500">
                        PNG, JPG, GIF up to 10MB
                      </p>
                    </div>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Birth Details */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Calendar className="h-5 w-5" />
                Birth Details
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-1">
                    Birth Time
                  </label>
                  <Input
                    type="time"
                    value={data.birthTime || ''}
                    onChange={(e) => onChange({ ...data, birthTime: e.target.value })}
                    placeholder="HH:MM"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">
                    Birth Place
                  </label>
                  <Input
                    type="text"
                    value={data.birthPlace || ''}
                    onChange={(e) => onChange({ ...data, birthPlace: e.target.value })}
                    placeholder="City, State, Country"
                  />
                </div>
              </div>

              <div className="flex justify-center">
                <Button onClick={calculateHoroscope} className="flex items-center gap-2">
                  <Calculator className="h-4 w-4" />
                  Calculate Horoscope Details
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Horoscope Details */}
          {(data.nakshatra || data.rashi || data.gotra) && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Star className="h-5 w-5" />
                  Horoscope Details
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      {t('horoscope.nakshatra')}
                    </label>
                    <div className="text-lg font-semibold">{data.nakshatra || 'Not calculated'}</div>
                  </div>

                  <div className="bg-gray-50 p-4 rounded-lg">
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      {t('horoscope.rashi')}
                    </label>
                    <div className="text-lg font-semibold">{data.rashi || 'Not calculated'}</div>
                  </div>

                  <div className="bg-gray-50 p-4 rounded-lg">
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      {t('horoscope.gotra')}
                    </label>
                    <div className="text-lg font-semibold">{data.gotra || 'Not calculated'}</div>
                  </div>

                  <div className="bg-gray-50 p-4 rounded-lg">
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      {t('horoscope.star')}
                    </label>
                    <div className="text-lg font-semibold">{data.star || data.nakshatra}</div>
                  </div>

                  <div className="bg-gray-50 p-4 rounded-lg">
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      {t('horoscope.nadi')}
                    </label>
                    <div className="text-lg font-semibold">{data.nadi || 'Not calculated'}</div>
                  </div>

                  <div className="bg-gray-50 p-4 rounded-lg">
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      {t('horoscope.manglik')}
                    </label>
                    <select
                      value={data.manglik}
                      onChange={(e) => onChange({ ...data, manglik: e.target.value as any })}
                      className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm"
                    >
                      <option value="yes">{t('horoscope.yes')}</option>
                      <option value="no">{t('horoscope.no')}</option>
                      <option value="partial">{t('horoscope.partial')}</option>
                      <option value="unknown">{t('horoscope.unknown')}</option>
                    </select>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Kundli Matching */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Heart className="h-5 w-5" />
                {t('horoscope.kundli_matching')}
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {!compatibilityScore ? (
                <div className="text-center py-8">
                  <Zap className="h-12 w-12 mx-auto text-gray-400 mb-4" />
                  <p className="text-gray-600 mb-4">
                    Calculate Kundli matching to check compatibility
                  </p>
                  <Button onClick={calculateKundliMatch}>
                    Calculate Kundli Match
                  </Button>
                </div>
              ) : (
                <div className="space-y-4">
                  {/* Overall Score */}
                  <div className="text-center p-6 bg-gradient-to-r from-pink-50 to-purple-50 rounded-lg">
                    <div className="text-3xl font-bold text-purple-600 mb-2">
                      {compatibilityScore.total}/36
                    </div>
                    <div className="text-lg font-semibold text-purple-700">
                      {compatibilityScore.compatibility} Match
                    </div>
                    <div className="text-sm text-gray-600 mt-1">
                      Manglik Status: {compatibilityScore.manglikStatus}
                    </div>
                  </div>

                  {/* Detailed Scores */}
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div className="text-center p-3 bg-gray-50 rounded-lg">
                      <div className="font-semibold">Varna</div>
                      <div className="text-2xl font-bold text-blue-600">{compatibilityScore.varna}/1</div>
                    </div>
                    <div className="text-center p-3 bg-gray-50 rounded-lg">
                      <div className="font-semibold">Vashya</div>
                      <div className="text-2xl font-bold text-green-600">{compatibilityScore.vashya}/2</div>
                    </div>
                    <div className="text-center p-3 bg-gray-50 rounded-lg">
                      <div className="font-semibold">Tara</div>
                      <div className="text-2xl font-bold text-yellow-600">{compatibilityScore.tara}/3</div>
                    </div>
                    <div className="text-center p-3 bg-gray-50 rounded-lg">
                      <div className="font-semibold">Yoni</div>
                      <div className="text-2xl font-bold text-red-600">{compatibilityScore.yoni}/4</div>
                    </div>
                    <div className="text-center p-3 bg-gray-50 rounded-lg">
                      <div className="font-semibold">Graha Maitri</div>
                      <div className="text-2xl font-bold text-purple-600">{compatibilityScore.grahaMaitri}/5</div>
                    </div>
                    <div className="text-center p-3 bg-gray-50 rounded-lg">
                      <div className="font-semibold">Gana</div>
                      <div className="text-2xl font-bold text-indigo-600">{compatibilityScore.gana}/6</div>
                    </div>
                    <div className="text-center p-3 bg-gray-50 rounded-lg">
                      <div className="font-semibold">Bhakoot</div>
                      <div className="text-2xl font-bold text-pink-600">{compatibilityScore.bhakoot}/7</div>
                    </div>
                    <div className="text-center p-3 bg-gray-50 rounded-lg">
                      <div className="font-semibold">Nadi</div>
                      <div className="text-2xl font-bold text-orange-600">{compatibilityScore.nadi}/8</div>
                    </div>
                  </div>

                  {/* Compatibility Analysis */}
                  <div className="bg-blue-50 p-4 rounded-lg">
                    <h4 className="font-semibold text-blue-800 mb-2">Compatibility Analysis</h4>
                    {compatibilityScore.total >= 24 ? (
                      <p className="text-green-700">
                        Excellent compatibility! This match has very strong prospects for a successful marriage.
                      </p>
                    ) : compatibilityScore.total >= 18 ? (
                      <p className="text-blue-700">
                        Very good compatibility with positive indicators for marital harmony.
                      </p>
                    ) : compatibilityScore.total >= 12 ? (
                      <p className="text-yellow-700">
                        Moderate compatibility. Consider matching other aspects as well.
                      </p>
                    ) : (
                      <p className="text-red-700">
                        Low compatibility score. It's recommended to consult with an astrologer.
                      </p>
                    )}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </>
      )}
    </div>
  );
};