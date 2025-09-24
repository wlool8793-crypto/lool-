import { MarriageBiodata } from '../types/marriage';

interface MatchScore {
  totalScore: number;
  maxScore: number;
  percentage: number;
  category: 'excellent' | 'very-good' | 'good' | 'average' | 'poor';
  breakdown: {
    religious: { score: number; max: number; details: string[] };
    cultural: { score: number; max: number; details: string[] };
    family: { score: number; max: number; details: string[] };
    lifestyle: { score: number; max: number; details: string[] };
    educational: { score: number; max: number; details: string[] };
    regional: { score: number; max: number; details: string[] };
    horoscope: { score: number; max: number; details: string[] };
  };
  recommendations: string[];
  potentialChallenges: string[];
}

interface CulturalMatchConfig {
  weights: {
    religious: number;
    cultural: number;
    family: number;
    lifestyle: number;
    educational: number;
    regional: number;
    horoscope: number;
  };
  importance: {
    sameReligion: number;
    sameCaste: number;
    sameRegion: number;
    similarEducation: number;
    similarValues: number;
    horoscopeMatch: number;
  };
}

export class CulturalMatchingEngine {
  private config: CulturalMatchConfig;

  constructor(config?: Partial<CulturalMatchConfig>) {
    this.config = {
      weights: {
        religious: 0.25,
        cultural: 0.20,
        family: 0.15,
        lifestyle: 0.15,
        educational: 0.10,
        regional: 0.10,
        horoscope: 0.05,
        ...config?.weights
      },
      importance: {
        sameReligion: 0.4,
        sameCaste: 0.3,
        sameRegion: 0.2,
        similarEducation: 0.3,
        similarValues: 0.35,
        horoscopeMatch: 0.25,
        ...config?.importance
      }
    };
  }

  calculateMatch(profile1: MarriageBiodata, profile2: MarriageBiodata): MatchScore {
    const religiousScore = this.calculateReligiousMatch(profile1, profile2);
    const culturalScore = this.calculateCulturalMatch(profile1, profile2);
    const familyScore = this.calculateFamilyMatch(profile1, profile2);
    const lifestyleScore = this.calculateLifestyleMatch(profile1, profile2);
    const educationalScore = this.calculateEducationalMatch(profile1, profile2);
    const regionalScore = this.calculateRegionalMatch(profile1, profile2);
    const horoscopeScore = this.calculateHoroscopeMatch(profile1, profile2);

    const totalWeightedScore =
      (religiousScore.score * this.config.weights.religious) +
      (culturalScore.score * this.config.weights.cultural) +
      (familyScore.score * this.config.weights.family) +
      (lifestyleScore.score * this.config.weights.lifestyle) +
      (educationalScore.score * this.config.weights.educational) +
      (regionalScore.score * this.config.weights.regional) +
      (horoscopeScore.score * this.config.weights.horoscope);

    const maxScore = 100;
    const percentage = Math.round((totalWeightedScore / maxScore) * 100);

    return {
      totalScore: Math.round(totalWeightedScore),
      maxScore,
      percentage,
      category: this.getMatchCategory(percentage),
      breakdown: {
        religious: religiousScore,
        cultural: culturalScore,
        family: familyScore,
        lifestyle: lifestyleScore,
        educational: educationalScore,
        regional: regionalScore,
        horoscope: horoscopeScore,
      },
      recommendations: this.generateRecommendations(profile1, profile2),
      potentialChallenges: this.identifyChallenges(profile1, profile2)
    };
  }

  private calculateReligiousMatch(profile1: MarriageBiodata, profile2: MarriageBiodata) {
    let score = 0;
    const maxScore = 100;
    const details: string[] = [];

    // Same religion (high importance)
    if (profile1.personalInfo.religion === profile2.personalInfo.religion) {
      score += this.config.importance.sameReligion * 100;
      details.push(`Same religion: ${profile1.personalInfo.religion}`);
    } else {
      details.push(`Different religions: ${profile1.personalInfo.religion} vs ${profile2.personalInfo.religion}`);
    }

    // Same caste (medium importance)
    if (profile1.personalInfo.caste && profile2.personalInfo.caste) {
      if (profile1.personalInfo.caste === profile2.personalInfo.caste) {
        score += this.config.importance.sameCaste * 100;
        details.push(`Same caste: ${profile1.personalInfo.caste}`);
      } else {
        details.push(`Different castes: ${profile1.personalInfo.caste} vs ${profile2.personalInfo.caste}`);
      }
    }

    // Religious practice compatibility
    if (profile1.lifestyle && profile2.lifestyle) {
      const sameDiet = profile1.lifestyle.diet === profile2.lifestyle.diet;
      if (sameDiet) {
        score += 20;
        details.push(`Same dietary preference: ${profile1.lifestyle.diet}`);
      } else {
        details.push(`Different dietary preferences: ${profile1.lifestyle.diet} vs ${profile2.lifestyle.diet}`);
      }

      // Smoking/drinking compatibility
      const sameSmoking = profile1.lifestyle.smoking === profile2.lifestyle.smoking;
      const sameDrinking = profile1.lifestyle.drinking === profile2.lifestyle.drinking;
      if (sameSmoking && sameDrinking) {
        score += 15;
        details.push('Compatible lifestyle habits');
      }
    }

    return {
      score: Math.min(score, maxScore),
      maxScore,
      details
    };
  }

  private calculateCulturalMatch(profile1: MarriageBiodata, profile2: MarriageBiodata) {
    let score = 0;
    const maxScore = 100;
    const details: string[] = [];

    // Mother tongue compatibility
    if (profile1.personalInfo.motherTongue === profile2.personalInfo.motherTongue) {
      score += 30;
      details.push(`Same mother tongue: ${profile1.personalInfo.motherTongue}`);
    }

    // Nationality
    if (profile1.personalInfo.nationality === profile2.personalInfo.nationality) {
      score += 25;
      details.push(`Same nationality: ${profile1.personalInfo.nationality}`);
    }

    // Language compatibility
    const profile1Languages = profile1.personalInfo.languages.map(l => l.name);
    const profile2Languages = profile2.personalInfo.languages.map(l => l.name);
    const commonLanguages = profile1Languages.filter(lang => profile2Languages.includes(lang));
    if (commonLanguages.length > 0) {
      score += 20;
      details.push(`Common languages: ${commonLanguages.join(', ')}`);
    }

    // Values compatibility based on family values
    if (profile1.familyInfo.familyValues === profile2.familyInfo.familyValues) {
      score += 25;
      details.push(`Similar family values: ${profile1.familyInfo.familyValues}`);
    }

    return {
      score: Math.min(score, maxScore),
      maxScore,
      details
    };
  }

  private calculateFamilyMatch(profile1: MarriageBiodata, profile2: MarriageBiodata) {
    let score = 0;
    const maxScore = 100;
    const details: string[] = [];

    // Family type compatibility
    if (profile1.familyInfo.familyType === profile2.familyInfo.familyType) {
      score += 25;
      details.push(`Same family type: ${profile1.familyInfo.familyType}`);
    }

    // Family status compatibility
    if (profile1.familyInfo.familyStatus === profile2.familyInfo.familyStatus) {
      score += 25;
      details.push(`Similar family status: ${profile1.familyInfo.familyStatus}`);
    }

    // Family values compatibility
    if (profile1.familyInfo.familyValues === profile2.familyInfo.familyValues) {
      score += 30;
      details.push(`Similar family values: ${profile1.familyInfo.familyValues}`);
    }

    // Regional proximity
    if (profile1.familyInfo.familyLocation === profile2.familyInfo.familyLocation) {
      score += 20;
      details.push(`Same family region: ${profile1.familyInfo.familyLocation}`);
    }

    return {
      score: Math.min(score, maxScore),
      maxScore,
      details
    };
  }

  private calculateLifestyleMatch(profile1: MarriageBiodata, profile2: MarriageBiodata) {
    let score = 0;
    const maxScore = 100;
    const details: string[] = [];

    if (!profile1.lifestyle || !profile2.lifestyle) {
      return { score: 0, maxScore, details: ['Lifestyle data not available'] };
    }

    // Diet compatibility
    if (profile1.lifestyle.diet === profile2.lifestyle.diet) {
      score += 30;
      details.push(`Same diet preference: ${profile1.lifestyle.diet}`);
    }

    // Smoking compatibility
    if (profile1.lifestyle.smoking === profile2.lifestyle.smoking) {
      score += 25;
      details.push(`Compatible smoking habits`);
    }

    // Drinking compatibility
    if (profile1.lifestyle.drinking === profile2.lifestyle.drinking) {
      score += 25;
      details.push(`Compatible drinking habits`);
    }

    // Hobbies/interests overlap
    const profile1Hobbies = new Set(profile1.lifestyle.hobbies || []);
    const profile2Hobbies = new Set(profile2.lifestyle.hobbies || []);
    const commonHobbies = [...profile1Hobbies].filter(hobby => profile2Hobbies.has(hobby));
    if (commonHobbies.length > 0) {
      score += 20;
      details.push(`Common interests: ${commonHobbies.join(', ')}`);
    }

    return {
      score: Math.min(score, maxScore),
      maxScore,
      details
    };
  }

  private calculateEducationalMatch(profile1: MarriageBiodata, profile2: MarriageBiodata) {
    let score = 0;
    const maxScore = 100;
    const details: string[] = [];

    // Find highest education level for both profiles
    const getEducationLevel = (edu: any) => {
      const levels = ['primary', 'secondary', 'higher_secondary', 'bachelors', 'masters', 'phd'];
      return levels.indexOf(edu.level);
    };

    const profile1Highest = Math.max(...profile1.education.map(getEducationLevel));
    const profile2Highest = Math.max(...profile2.education.map(getEducationLevel));

    const educationDiff = Math.abs(profile1Highest - profile2Highest);
    if (educationDiff === 0) {
      score += 50;
      details.push('Same education level');
    } else if (educationDiff === 1) {
      score += 35;
      details.push('Similar education levels');
    } else if (educationDiff === 2) {
      score += 20;
      details.push('Different but acceptable education levels');
    } else {
      details.push('Significant education level difference');
    }

    // Field of study overlap
    const profile1Fields = profile1.education.map(e => e.specialization || e.degree);
    const profile2Fields = profile2.education.map(e => e.specialization || e.degree);
    const commonFields = profile1Fields.filter(field =>
      profile2Fields.some(field2 =>
        field.toLowerCase().includes(field2.toLowerCase()) ||
        field2.toLowerCase().includes(field.toLowerCase())
      )
    );

    if (commonFields.length > 0) {
      score += 30;
      details.push(`Related fields of study: ${commonFields.join(', ')}`);
    }

    // Occupation similarity
    if (profile1.occupation.length > 0 && profile2.occupation.length > 0) {
      const profile1Occupations = profile1.occupation.map(o => o.industry);
      const profile2Occupations = profile2.occupation.map(o => o.industry);
      const commonIndustries = profile1Occupations.filter(industry =>
        profile2Occupations.includes(industry)
      );

      if (commonIndustries.length > 0) {
        score += 20;
        details.push(`Similar industries: ${commonIndustries.join(', ')}`);
      }
    }

    return {
      score: Math.min(score, maxScore),
      maxScore,
      details
    };
  }

  private calculateRegionalMatch(profile1: MarriageBiodata, profile2: MarriageBiodata) {
    let score = 0;
    const maxScore = 100;
    const details: string[] = [];

    // Same city
    if (profile1.contactInfo.city === profile2.contactInfo.city) {
      score += 40;
      details.push(`Same city: ${profile1.contactInfo.city}`);
    }

    // Same state
    if (profile1.contactInfo.state === profile2.contactInfo.state) {
      score += 30;
      details.push(`Same state: ${profile1.contactInfo.state}`);
    }

    // Same country
    if (profile1.contactInfo.country === profile2.contactInfo.country) {
      score += 20;
      details.push(`Same country: ${profile1.contactInfo.country}`);
    }

    // Birth place proximity
    if (profile1.personalInfo.birthPlace === profile2.personalInfo.birthPlace) {
      score += 10;
      details.push(`Same birth place: ${profile1.personalInfo.birthPlace}`);
    }

    return {
      score: Math.min(score, maxScore),
      maxScore,
      details
    };
  }

  private calculateHoroscopeMatch(profile1: MarriageBiodata, profile2: MarriageBiodata) {
    let score = 0;
    const maxScore = 100;
    const details: string[] = [];

    if (!profile1.horoscope?.hasHoroscope || !profile2.horoscope?.hasHoroscope) {
      return { score: 50, maxScore, details: ['Horoscope data not available for both profiles'] };
    }

    // Same nakshatra (rare but highly compatible)
    if (profile1.horoscope.nakshatra === profile2.horoscope.nakshatra) {
      score += 30;
      details.push(`Same nakshatra: ${profile1.horoscope.nakshatra}`);
    }

    // Compatible rashi
    const compatibleRashis = this.getCompatibleRashis(profile1.horoscope.rashi || '');
    if (compatibleRashis.includes(profile2.horoscope.rashi || '')) {
      score += 25;
      details.push(`Compatible rashis: ${profile1.horoscope.rashi} & ${profile2.horoscope.rashi}`);
    }

    // Same gotra (avoid)
    if (profile1.horoscope.gotra === profile2.horoscope.gotra) {
      score -= 20;
      details.push(`Same gotra - traditionally not recommended`);
    }

    // Manglik compatibility
    if (profile1.horoscope.manglik === profile2.horoscope.manglik) {
      score += 25;
      details.push(`Matching manglik status: ${profile1.horoscope.manglik}`);
    }

    // Nadi compatibility
    if (profile1.horoscope.nadi && profile2.horoscope.nadi) {
      if (profile1.horoscope.nadi !== profile2.horoscope.nadi) {
        score += 20;
        details.push(`Compatible nadi: ${profile1.horoscope.nadi} & ${profile2.horoscope.nadi}`);
      } else {
        score -= 10;
        details.push(`Same nadi - may indicate health issues`);
      }
    }

    return {
      score: Math.max(0, Math.min(score, maxScore)),
      maxScore,
      details
    };
  }

  private getCompatibleRashis(rashi: string): string[] {
    const compatibilityMap: Record<string, string[]> = {
      'Mesha': ['Simha', 'Dhanu', 'Mithuna', 'Kumbha'],
      'Vrishabha': ['Kanya', 'Makara', 'Karka', 'Meena'],
      'Mithuna': ['Tula', 'Kumbha', 'Simha', 'Dhanu'],
      'Karka': ['Vrishchika', 'Meena', 'Vrishabha', 'Kanya'],
      'Simha': ['Mesha', 'Dhanu', 'Mithuna', 'Tula'],
      'Kanya': ['Vrishabha', 'Makara', 'Karka', 'Vrishchika'],
      'Tula': ['Mithuna', 'Kumbha', 'Simha', 'Dhanu'],
      'Vrishchika': ['Karka', 'Meena', 'Vrishabha', 'Kanya'],
      'Dhanu': ['Mesha', 'Simha', 'Mithuna', 'Tula'],
      'Makara': ['Vrishabha', 'Kanya', 'Karka', 'Vrishchika'],
      'Kumbha': ['Mithuna', 'Tula', 'Simha', 'Dhanu'],
      'Meena': ['Karka', 'Vrishchika', 'Vrishabha', 'Kanya']
    };

    return compatibilityMap[rashi] || [];
  }

  private getMatchCategory(percentage: number): 'excellent' | 'very-good' | 'good' | 'average' | 'poor' {
    if (percentage >= 85) return 'excellent';
    if (percentage >= 70) return 'very-good';
    if (percentage >= 55) return 'good';
    if (percentage >= 40) return 'average';
    return 'poor';
  }

  private generateRecommendations(profile1: MarriageBiodata, profile2: MarriageBiodata): string[] {
    const recommendations: string[] = [];

    // Religious recommendations
    if (profile1.personalInfo.religion !== profile2.personalInfo.religion) {
      recommendations.push('Consider discussing religious practices and future plans for religious ceremonies');
    }

    // Cultural recommendations
    if (profile1.personalInfo.motherTongue !== profile2.personalInfo.motherTongue) {
      recommendations.push('Plan for language learning and communication strategies');
    }

    // Family recommendations
    if (profile1.familyInfo.familyType !== profile2.familyInfo.familyType) {
      recommendations.push('Discuss expectations regarding family involvement and living arrangements');
    }

    // Lifestyle recommendations
    if (profile1.lifestyle?.diet !== profile2.lifestyle?.diet) {
      recommendations.push('Plan for household dietary arrangements and meal preparation');
    }

    // Educational recommendations
    const edu1 = Math.max(...profile1.education.map(e => {
          const levels = ['primary', 'secondary', 'higher_secondary', 'bachelors', 'masters', 'phd'];
          return levels.indexOf(e.level);
        }));
    const edu2 = Math.max(...profile2.education.map(e => {
          const levels = ['primary', 'secondary', 'higher_secondary', 'bachelors', 'masters', 'phd'];
          return levels.indexOf(e.level);
        }));

    if (Math.abs(edu1 - edu2) > 2) {
      recommendations.push('Ensure mutual respect for educational backgrounds and intellectual interests');
    }

    return recommendations;
  }

  private identifyChallenges(profile1: MarriageBiodata, profile2: MarriageBiodata): string[] {
    const challenges: string[] = [];

    // Religious challenges
    if (profile1.personalInfo.religion !== profile2.personalInfo.religion) {
      challenges.push('Different religious backgrounds may require additional planning');
    }

    // Caste challenges
    if (profile1.personalInfo.caste !== profile2.personalInfo.caste) {
      challenges.push('Family resistance due to caste differences may occur');
    }

    // Geographic challenges
    if (profile1.contactInfo.country !== profile2.contactInfo.country) {
      challenges.push('Long-distance relationship or relocation may be necessary');
    }

    // Lifestyle challenges
    if (profile1.lifestyle?.diet !== profile2.lifestyle?.diet) {
      challenges.push('Different dietary preferences may require compromise');
    }

    // Age difference challenges
    const ageDiff = Math.abs(profile1.personalInfo.age - profile2.personalInfo.age);
    if (ageDiff > 10) {
      challenges.push('Significant age difference may impact life stage compatibility');
    }

    return challenges;
  }
}