import React from 'react';
import type { MarriageBiodata } from '../types/marriage';

export interface TemplateLibrary {
  id: string;
  name: string;
  category: 'marriage' | 'professional';
  culture: string;
  region?: string;
  religion?: string;
  description: string;
  features: string[];
  previewImage?: string;
  component: React.ComponentType<{ data: MarriageBiodata; customizations?: any }>;
  customizations: TemplateCustomization[];
  popularity: number;
  isPremium: boolean;
}

export interface TemplateCustomization {
  name: string;
  type: 'color' | 'font' | 'layout' | 'image' | 'symbol';
  options: string[];
  defaultValue: string;
  description: string;
}

export interface CulturalTemplate {
  id: string;
  name: string;
  culture: string;
  description: string;
  components: {
    header: React.ComponentType<{ data: MarriageBiodata; customizations?: any }>;
    personal: React.ComponentType<{ data: MarriageBiodata; customizations?: any }>;
    family: React.ComponentType<{ data: MarriageBiodata; customizations?: any }>;
    horoscope: React.ComponentType<{ data: MarriageBiodata; customizations?: any }>;
    footer: React.ComponentType<{ data: MarriageBiodata; customizations?: any }>;
  };
  styling: {
    colors: Record<string, string>;
    fonts: Record<string, string>;
    patterns: string[];
    symbols: string[];
  };
  customizations: TemplateCustomization[];
}

// Simple placeholder components for now
const PlaceholderHeader: React.FC<{ data: MarriageBiodata }> = ({ data }) => {
  return (
    <div className="text-center p-4">
      <h1 className="text-2xl font-bold">{data.personalInfo.fullName}</h1>
      <p>Marriage Biodata</p>
    </div>
  );
};

const PlaceholderSection: React.FC<{ data: MarriageBiodata; title: string }> = ({ data, title }) => {
  return (
    <div className="p-4">
      <h2 className="text-xl font-semibold mb-2">{title}</h2>
      <p>Content for {title} section</p>
    </div>
  );
};

// Marriage Biodata Templates
export const marriageTemplates: TemplateLibrary[] = [
  {
    id: 'traditional-hindi',
    name: 'Traditional Hindi',
    category: 'marriage',
    culture: 'Indian',
    region: 'North India',
    religion: 'Hindu',
    description: 'Traditional Hindi marriage biodata with classical Indian design elements',
    features: ['Traditional Design', 'Hindi Text', 'Cultural Elements'],
    component: PlaceholderHeader,
    customizations: [
      {
        name: 'Primary Color',
        type: 'color',
        options: ['#DC2626', '#B91C1C', '#991B1B'],
        defaultValue: '#DC2626',
        description: 'Main color for headings and borders'
      }
    ],
    popularity: 85,
    isPremium: false
  }
];

// Cultural Template Registry
export const culturalTemplateRegistry: Record<string, CulturalTemplate> = {
  'traditional-hindi': {
    id: 'traditional-hindi',
    name: 'Traditional Hindi',
    culture: 'Indian',
    description: 'Traditional Hindi marriage biodata with classical Indian design elements',
    components: {
      header: PlaceholderHeader,
      personal: ({ data }: { data: MarriageBiodata }) => <PlaceholderSection data={data} title="Personal Information" />,
      family: ({ data }: { data: MarriageBiodata }) => <PlaceholderSection data={data} title="Family Information" />,
      horoscope: ({ data }: { data: MarriageBiodata }) => <PlaceholderSection data={data} title="Horoscope Details" />,
      footer: PlaceholderHeader
    },
    styling: {
      colors: {
        primary: '#DC2626',
        secondary: '#F59E0B',
        background: '#FEF3C7'
      },
      fonts: {
        heading: 'serif',
        body: 'sans-serif'
      },
      patterns: ['traditional', 'floral', 'geometric'],
      symbols: ['om', 'swastika', 'lotus']
    },
    customizations: [
      {
        name: 'Primary Color',
        type: 'color',
        options: ['#DC2626', '#B91C1C', '#991B1B'],
        defaultValue: '#DC2626',
        description: 'Main color for headings and borders'
      },
      {
        name: 'Secondary Color',
        type: 'color',
        options: ['#F59E0B', '#D97706', '#B45309'],
        defaultValue: '#F59E0B',
        description: 'Secondary color for accents'
      }
    ]
  }
};

// Template utilities
export const getTemplateById = (id: string): TemplateLibrary | undefined => {
  return marriageTemplates.find(template => template.id === id);
};

export const getCulturalTemplateById = (id: string): CulturalTemplate | undefined => {
  return culturalTemplateRegistry[id];
};

export const getTemplatesByCulture = (culture: string): TemplateLibrary[] => {
  return marriageTemplates.filter(template => template.culture === culture);
};

export const filterTemplates = (templates: TemplateLibrary[], filters: {
  culture?: string;
  religion?: string;
  isPremium?: boolean;
  minPopularity?: number;
}): TemplateLibrary[] => {
  return templates.filter(template => {
    if (filters.culture && template.culture !== filters.culture) return false;
    if (filters.religion && template.religion !== filters.religion) return false;
    if (filters.isPremium !== undefined && template.isPremium !== filters.isPremium) return false;
    if (filters.minPopularity && template.popularity < filters.minPopularity) return false;
    return true;
  });
};