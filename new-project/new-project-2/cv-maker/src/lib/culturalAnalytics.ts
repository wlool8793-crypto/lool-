import { MarriageBiodata } from '../types/marriage';

interface AnalyticsEvent {
  id: string;
  timestamp: Date;
  eventType: string;
  category: string;
  action: string;
  label?: string;
  value?: number;
  metadata?: Record<string, any>;
}

interface CulturalMetrics {
  regionalUsage: Record<string, number>;
  languageUsage: Record<string, number>;
  templatePopularity: Record<string, number>;
  culturalFeatureAdoption: Record<string, number>;
  matchingTrends: {
    averageScore: number;
    topMatchingFactors: string[];
    compatibilityDistribution: Record<string, number>;
  };
  religiousDistribution: Record<string, number>;
  casteDistribution: Record<string, number>;
  lifestyleTrends: Record<string, number>;
  horoscopeUsage: {
    percentage: number;
    regionalBreakdown: Record<string, number>;
  };
  userEngagement: {
    averageTimeSpent: number;
    completionRates: Record<string, number>;
    dropOffPoints: string[];
  };
}

interface CulturalInsights {
  popularCombinations: Array<{
    religion: string;
    region: string;
    count: number;
  }>;
  emergingTrends: Array<{
    feature: string;
    growth: number;
    description: string;
  }>;
  recommendations: string[];
  culturalShifts: Array<{
    category: string;
    from: string;
    to: string;
    changePercentage: number;
  }>;
}

export class CulturalAnalyticsEngine {
  private events: AnalyticsEvent[] = [];
  private profiles: MarriageBiodata[] = [];
  private storageKey = 'cv_maker_cultural_analytics';

  constructor() {
    this.loadFromStorage();
  }

  // Event tracking
  trackEvent(event: Omit<AnalyticsEvent, 'id' | 'timestamp'>): void {
    const analyticsEvent: AnalyticsEvent = {
      ...event,
      id: this.generateEventId(),
      timestamp: new Date()
    };

    this.events.push(analyticsEvent);
    this.saveToStorage();
  }

  trackProfileCreated(profile: MarriageBiodata): void {
    this.trackEvent({
      eventType: 'profile_created',
      category: 'user',
      action: 'create_profile',
      metadata: {
        religion: profile.personalInfo.religion,
        region: this.extractRegion(profile),
        language: profile.personalInfo.motherTongue,
        hasHoroscope: profile.horoscope?.hasHoroscope
      }
    });

    this.profiles.push(profile);
    this.saveToStorage();
  }

  trackTemplateUsed(templateId: string, profile: MarriageBiodata): void {
    this.trackEvent({
      eventType: 'template_used',
      category: 'template',
      action: 'select_template',
      label: templateId,
      metadata: {
        region: this.extractRegion(profile),
        religion: profile.personalInfo.religion
      }
    });
  }

  trackLanguageChanged(language: string, previousLanguage: string): void {
    this.trackEvent({
      eventType: 'language_changed',
      category: 'localization',
      action: 'change_language',
      label: `${previousLanguage} -> ${language}`
    });
  }

  trackFeatureUsed(feature: string, profile: MarriageBiodata): void {
    this.trackEvent({
      eventType: 'feature_used',
      category: 'feature',
      action: 'use_feature',
      label: feature,
      metadata: {
        region: this.extractRegion(profile),
        religion: profile.personalInfo.religion
      }
    });
  }

  trackMatchingAttempt(profile1: MarriageBiodata, profile2: MarriageBiodata, score: number): void {
    this.trackEvent({
      eventType: 'matching_attempt',
      category: 'matching',
      action: 'calculate_match',
      value: score,
      metadata: {
        profile1Region: this.extractRegion(profile1),
        profile2Region: this.extractRegion(profile2),
        sameReligion: profile1.personalInfo.religion === profile2.personalInfo.religion,
        sameRegion: this.extractRegion(profile1) === this.extractRegion(profile2)
      }
    });
  }

  // Analytics calculations
  generateMetrics(): CulturalMetrics {
    return {
      regionalUsage: this.calculateRegionalUsage(),
      languageUsage: this.calculateLanguageUsage(),
      templatePopularity: this.calculateTemplatePopularity(),
      culturalFeatureAdoption: this.calculateFeatureAdoption(),
      matchingTrends: this.calculateMatchingTrends(),
      religiousDistribution: this.calculateReligiousDistribution(),
      casteDistribution: this.calculateCasteDistribution(),
      lifestyleTrends: this.calculateLifestyleTrends(),
      horoscopeUsage: this.calculateHoroscopeUsage(),
      userEngagement: this.calculateUserEngagement()
    };
  }

  generateInsights(): CulturalInsights {
    return {
      popularCombinations: this.calculatePopularCombinations(),
      emergingTrends: this.calculateEmergingTrends(),
      recommendations: this.generateRecommendations(),
      culturalShifts: this.calculateCulturalShifts()
    };
  }

  private calculateRegionalUsage(): Record<string, number> {
    const usage: Record<string, number> = {};

    this.profiles.forEach(profile => {
      const region = this.extractRegion(profile);
      usage[region] = (usage[region] || 0) + 1;
    });

    return usage;
  }

  private calculateLanguageUsage(): Record<string, number> {
    const usage: Record<string, number> = {};

    this.profiles.forEach(profile => {
      const language = profile.personalInfo.motherTongue;
      usage[language] = (usage[language] || 0) + 1;
    });

    return usage;
  }

  private calculateTemplatePopularity(): Record<string, number> {
    const usage: Record<string, number> = {};

    this.events
      .filter(event => event.eventType === 'template_used')
      .forEach(event => {
        const templateId = event.label || 'unknown';
        usage[templateId] = (usage[templateId] || 0) + 1;
      });

    return usage;
  }

  private calculateFeatureAdoption(): Record<string, number> {
    const adoption: Record<string, number> = {};

    this.events
      .filter(event => event.eventType === 'feature_used')
      .forEach(event => {
        const feature = event.label || 'unknown';
        adoption[feature] = (adoption[feature] || 0) + 1;
      });

    return adoption;
  }

  private calculateMatchingTrends() {
    const matchingEvents = this.events.filter(event => event.eventType === 'matching_attempt');
    const scores = matchingEvents.map(event => event.value || 0);

    const averageScore = scores.length > 0 ? scores.reduce((a, b) => a + b, 0) / scores.length : 0;

    const compatibilityDistribution = {
      excellent: scores.filter(s => s >= 85).length,
      'very-good': scores.filter(s => s >= 70 && s < 85).length,
      good: scores.filter(s => s >= 55 && s < 70).length,
      average: scores.filter(s => s >= 40 && s < 55).length,
      poor: scores.filter(s => s < 40).length
    };

    const factors = ['religion', 'region', 'caste', 'education', 'lifestyle'];
    const factorCounts: Record<string, number> = {};

    factors.forEach(factor => {
      factorCounts[factor] = matchingEvents.filter(event =>
        event.metadata?.[`same${factor.charAt(0).toUpperCase() + factor.slice(1)}`]
      ).length;
    });

    const topMatchingFactors = Object.entries(factorCounts)
      .sort(([, a], [, b]) => b - a)
      .slice(0, 3)
      .map(([factor]) => factor);

    return {
      averageScore,
      topMatchingFactors,
      compatibilityDistribution
    };
  }

  private calculateReligiousDistribution(): Record<string, number> {
    const distribution: Record<string, number> = {};

    this.profiles.forEach(profile => {
      const religion = profile.personalInfo.religion;
      distribution[religion] = (distribution[religion] || 0) + 1;
    });

    return distribution;
  }

  private calculateCasteDistribution(): Record<string, number> {
    const distribution: Record<string, number> = {};

    this.profiles.forEach(profile => {
      const caste = profile.personalInfo.caste || 'Not specified';
      distribution[caste] = (distribution[caste] || 0) + 1;
    });

    return distribution;
  }

  private calculateLifestyleTrends(): Record<string, number> {
    const trends: Record<string, number> = {};

    this.profiles.forEach(profile => {
      if (profile.lifestyle) {
        const diet = profile.lifestyle.diet;
        trends[diet] = (trends[diet] || 0) + 1;

        const smoking = profile.lifestyle.smoking;
        trends[`smoking_${smoking}`] = (trends[`smoking_${smoking}`] || 0) + 1;

        const drinking = profile.lifestyle.drinking;
        trends[`drinking_${drinking}`] = (trends[`drinking_${drinking}`] || 0) + 1;
      }
    });

    return trends;
  }

  private calculateHoroscopeUsage() {
    const totalProfiles = this.profiles.length;
    const horoscopeProfiles = this.profiles.filter(p => p.horoscope?.hasHoroscope).length;

    const regionalBreakdown: Record<string, number> = {};
    this.profiles.forEach(profile => {
      if (profile.horoscope?.hasHoroscope) {
        const region = this.extractRegion(profile);
        regionalBreakdown[region] = (regionalBreakdown[region] || 0) + 1;
      }
    });

    return {
      percentage: totalProfiles > 0 ? (horoscopeProfiles / totalProfiles) * 100 : 0,
      regionalBreakdown
    };
  }

  private calculateUserEngagement() {
    // This would typically be calculated from session data
    // For now, we'll return mock data
    return {
      averageTimeSpent: 15, // minutes
      completionRates: {
        personal: 95,
        family: 90,
        education: 85,
        horoscope: 60,
        lifestyle: 80
      },
      dropOffPoints: ['horoscope', 'additional_preferences']
    };
  }

  private calculatePopularCombinations() {
    const combinations: Record<string, number> = {};

    this.profiles.forEach(profile => {
      const key = `${profile.personalInfo.religion}_${this.extractRegion(profile)}`;
      combinations[key] = (combinations[key] || 0) + 1;
    });

    return Object.entries(combinations)
      .map(([combination, count]) => {
        const [religion, region] = combination.split('_');
        return { religion, region, count };
      })
      .sort((a, b) => b.count - a.count)
      .slice(0, 10);
  }

  private calculateEmergingTrends() {
    // Analyze feature adoption growth over time
    const thirtyDaysAgo = new Date();
    thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);

    const recentEvents = this.events.filter(event => event.timestamp >= thirtyDaysAgo);

    const features = [
      'horoscope_upload',
      'cultural_customization',
      'language_switch',
      'regional_template'
    ];

    return features.map(feature => {
      const recentUsage = recentEvents.filter(e => e.label?.includes(feature)).length;
      const growth = Math.random() * 50 - 25; // Mock growth percentage

      return {
        feature,
        growth,
        description: this.getTrendDescription(feature, growth)
      };
    }).filter(trend => Math.abs(trend.growth) > 10);
  }

  private generateRecommendations(): string[] {
    const recommendations: string[] = [];
    const metrics = this.generateMetrics();

    // Language usage recommendations
    const topLanguages = Object.entries(metrics.languageUsage)
      .sort(([, a], [, b]) => b - a)
      .slice(0, 3);

    recommendations.push(`Focus on supporting ${topLanguages.map(([lang]) => lang).join(', ')} languages for better user experience`);

    // Regional template recommendations
    const topRegions = Object.entries(metrics.regionalUsage)
      .sort(([, a], [, b]) => b - a)
      .slice(0, 3);

    recommendations.push(`Develop more specialized templates for ${topRegions.map(([region]) => region).join(', ')} regions`);

    // Horoscope usage recommendations
    if (metrics.horoscopeUsage.percentage > 70) {
      recommendations.push('Enhance horoscope features as they are highly used');
    } else if (metrics.horoscopeUsage.percentage < 30) {
      recommendations.push('Improve horoscope feature discoverability and user education');
    }

    // Matching improvements
    if (metrics.matchingTrends.averageScore < 60) {
      recommendations.push('Consider improving matching algorithm or user preference settings');
    }

    return recommendations;
  }

  private calculateCulturalShifts() {
    // This would analyze changes over time
    // For now, return mock data
    return [
      {
        category: 'Dietary Preferences',
        from: 'non_vegetarian',
        to: 'vegetarian',
        changePercentage: 15
      },
      {
        category: 'Family Values',
        from: 'traditional',
        to: 'moderate',
        changePercentage: 25
      },
      {
        category: 'Education',
        from: 'bachelors',
        to: 'masters',
        changePercentage: 20
      }
    ];
  }

  private extractRegion(profile: MarriageBiodata): string {
    // Simple region extraction based on country and state
    const { country, state } = profile.contactInfo;

    if (country === 'India') {
      if (['Punjab', 'Haryana', 'Delhi', 'Rajasthan'].includes(state || '')) {
        return 'north_indian';
      } else if (['Tamil Nadu', 'Karnataka', 'Kerala', 'Andhra Pradesh'].includes(state || '')) {
        return 'south_indian';
      } else if (['West Bengal', 'Bihar', 'Jharkhand'].includes(state || '')) {
        return 'bengali';
      } else if (['Gujarat', 'Maharashtra'].includes(state || '')) {
        return 'gujarati';
      }
    }

    if (country === 'Pakistan') {
      return 'pakistani';
    }

    if (country === 'Bangladesh') {
      return 'bangladeshi';
    }

    if (['USA', 'UK', 'Canada', 'Australia'].includes(country || '')) {
      return 'western';
    }

    return 'other';
  }

  private getTrendDescription(feature: string, growth: number): string {
    if (growth > 20) {
      return `Significant increase in ${feature.replace('_', ' ')} usage`;
    } else if (growth < -20) {
      return `Decreasing interest in ${feature.replace('_', ' ')}`;
    } else {
      return `Stable usage of ${feature.replace('_', ' ')}`;
    }
  }

  private generateEventId(): string {
    return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }

  private saveToStorage(): void {
    try {
      localStorage.setItem(this.storageKey, JSON.stringify({
        events: this.events,
        profiles: this.profiles
      }));
    } catch (error) {
      console.warn('Failed to save analytics data:', error);
    }
  }

  private loadFromStorage(): void {
    try {
      const stored = localStorage.getItem(this.storageKey);
      if (stored) {
        const data = JSON.parse(stored);
        this.events = data.events?.map((e: any) => ({
          ...e,
          timestamp: new Date(e.timestamp)
        })) || [];
        this.profiles = data.profiles || [];
      }
    } catch (error) {
      console.warn('Failed to load analytics data:', error);
    }
  }

  // Public methods for data export
  exportData(): { events: AnalyticsEvent[]; profiles: MarriageBiodata[] } {
    return {
      events: this.events,
      profiles: this.profiles
    };
  }

  clearData(): void {
    this.events = [];
    this.profiles = [];
    localStorage.removeItem(this.storageKey);
  }

  getEventsByType(eventType: string): AnalyticsEvent[] {
    return this.events.filter(event => event.eventType === eventType);
  }

  getEventsByDateRange(startDate: Date, endDate: Date): AnalyticsEvent[] {
    return this.events.filter(event =>
      event.timestamp >= startDate && event.timestamp <= endDate
    );
  }
}