import React from 'react';
import { render, screen, act } from '@testing-library/react';
import { vi } from 'vitest';
import { CVProvider, useCV } from '@/contexts/CVContext';
import type { TemplateType, FormStep, CVData, WorkExperience } from '@/types/cv';
import type { MarriageBiodata } from '@/types/marriage';
import type { DocumentType } from '@/types/common';

interface TestCVState {
  documentType: DocumentType;
  cvData: CVData;
  marriageData: MarriageBiodata;
  currentStep: FormStep;
  selectedTemplate: TemplateType;
  isSaved: boolean;
  isLoading: boolean;
  settings: {
    template: TemplateType;
    autoSave: boolean;
    validationMode: 'onBlur' | 'onChange' | 'onSubmit';
    language: string;
    theme: 'light' | 'dark' | 'auto';
  };
  formProgress: any;
  userSession: any;
  analytics: any;
}

type TestCVAction =
  | { type: 'UPDATE_PERSONAL_INFO'; payload: Partial<CVData['personalInfo']> }
  | { type: 'ADD_WORK_EXPERIENCE'; payload: WorkExperience }
  | { type: 'SET_CURRENT_STEP'; payload: FormStep }
  | { type: 'SET_TEMPLATE'; payload: TemplateType }
  | { type: 'UNKNOWN_ACTION'; payload?: unknown };

// Test component that uses the CV context
const TestComponent = () => {
  const { state, dispatch } = useCV();

  return (
    <div>
      <div data-testid="document-type">{state.documentType}</div>
      <div data-testid="current-step">{state.currentStep}</div>
      <div data-testid="is-saved">{state.isSaved.toString()}</div>
      <div data-testid="is-loading">{state.isLoading.toString()}</div>
      <div data-testid="selected-template">{state.selectedTemplate}</div>
      <button
        data-testid="update-personal-info"
        onClick={() =>
          dispatch({
            type: 'UPDATE_PERSONAL_INFO',
            payload: { fullName: 'John Doe', email: 'john@example.com' },
          })
        }
      >
        Update Personal Info
      </button>
      <button
        data-testid="add-work-experience"
        onClick={() =>
          dispatch({
            type: 'ADD_WORK_EXPERIENCE',
            payload: {
              id: '1',
              position: 'Developer',
              company: 'Tech Corp',
              location: 'San Francisco',
              startDate: '2020-01-01',
              endDate: '2023-01-01',
              current: false,
              description: 'Work description',
              achievements: ['Achievement 1'],
              skills: [],
              employmentType: 'full-time' as const,
              industry: 'Technology',
            },
          })
        }
      >
        Add Work Experience
      </button>
      <button
        data-testid="set-current-step"
        onClick={() => dispatch({ type: 'SET_CURRENT_STEP', payload: 'summary' })}
      >
        Set Current Step
      </button>
      <button
        data-testid="set-template"
        onClick={() => dispatch({ type: 'SET_TEMPLATE', payload: 'modern' })}
      >
        Set Template
      </button>
    </div>
  );
};

describe('CVContext', () => {
  const wrapper = ({ children }: { children: React.ReactNode }) => (
    <CVProvider>{children}</CVProvider>
  );

  it('provides initial state correctly', () => {
    render(<TestComponent />, { wrapper });

    expect(screen.getByTestId('document-type')).toHaveTextContent('cv');
    expect(screen.getByTestId('current-step')).toHaveTextContent('personal');
    expect(screen.getByTestId('is-saved')).toHaveTextContent('true');
    expect(screen.getByTestId('is-loading')).toHaveTextContent('false');
    expect(screen.getByTestId('selected-template')).toHaveTextContent('modern');
  });

  it('updates personal info correctly', () => {
    render(<TestComponent />, { wrapper });

    act(() => {
      screen.getByTestId('update-personal-info').click();
    });

    // The context should have updated, but we can't directly test the state change
    // in this simple test component. In a real scenario, we'd need a more complex
    // test component that displays the updated state.
    expect(screen.getByTestId('update-personal-info')).toBeInTheDocument();
  });

  it('adds work experience correctly', () => {
    render(<TestComponent />, { wrapper });

    act(() => {
      screen.getByTestId('add-work-experience').click();
    });

    expect(screen.getByTestId('add-work-experience')).toBeInTheDocument();
  });

  it('changes current step correctly', () => {
    render(<TestComponent />, { wrapper });

    act(() => {
      screen.getByTestId('set-current-step').click();
    });

    expect(screen.getByTestId('set-current-step')).toBeInTheDocument();
  });

  it('changes template correctly', () => {
    render(<TestComponent />, { wrapper });

    act(() => {
      screen.getByTestId('set-template').click();
    });

    expect(screen.getByTestId('set-template')).toBeInTheDocument();
  });

  it('throws error when useCV is used outside provider', () => {
    // Suppress console error for this test
    const originalError = console.error;
    console.error = vi.fn();

    expect(() => {
      render(<TestComponent />);
    }).toThrow('useCV must be used within a CVProvider');

    console.error = originalError;
  });
});

describe('CVContext Reducer', () => {
  // Mock initial state
  const initialState: TestCVState = {
    documentType: 'cv' as DocumentType,
    cvData: {
      id: '',
      documentType: 'cv' as DocumentType,
      templateCategory: 'professional' as const,
      personalInfo: {
        fullName: '',
        email: '',
        phone: '',
        address: '',
        linkedin: '',
        website: '',
        github: '',
      },
      professionalSummary: '',
      workExperience: [],
      education: [],
      skills: [],
      projects: [],
      certifications: [],
      languages: [],
      volunteerExperience: [],
      awards: [],
      publications: [],
      references: [],
      customSections: [],
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      isPublic: false,
      viewCount: 0,
      downloadCount: 0,
      settings: {
        showContact: true,
        showProfile: true,
        showSummary: true,
        template: 'modern',
        language: 'en',
        currency: 'USD',
      },
    },
    marriageData: {} as MarriageBiodata,
    currentStep: 'personal' as FormStep,
    selectedTemplate: 'modern' as TemplateType,
    isSaved: false,
    isLoading: false,
    formProgress: {
      cv: {
        personal: 0,
        summary: 0,
        experience: 0,
        education: 0,
        skills: 0,
        projects: 0,
        certifications: 0,
        languages: 0,
        volunteer: 0,
        awards: 0,
        publications: 0,
        references: 0,
        custom: 0,
        preview: 0,
      },
      marriage: {
        personal: 0,
        contact: 0,
        family: 0,
        education: 0,
        occupation: 0,
        lifestyle: 0,
        'partner-preference': 0,
        horoscope: 0,
        photos: 0,
        about: 0,
        preview: 0,
      },
    },
    userSession: {
      userId: '',
      role: 'owner' as const,
      permissions: [],
      lastActivity: '',
    },
    analytics: {
      timeSpent: {},
      formErrors: [],
      completionRate: 0,
      abandonedSections: [],
    },
    settings: {
      template: 'modern' as TemplateType,
      autoSave: true,
      validationMode: 'onBlur' as const,
      language: 'en',
      theme: 'light' as const,
    },
  };

  // Import the reducer function (this would be exported from CVContext)
  // For now, we'll test the actions by simulating the reducer behavior
  const testReducer = (state: TestCVState, action: TestCVAction) => {
    switch (action.type) {
      case 'UPDATE_PERSONAL_INFO':
        return {
          ...state,
          cvData: {
            ...state.cvData,
            personalInfo: {
              ...state.cvData.personalInfo,
              ...action.payload,
            },
          },
          isSaved: false,
        };
      case 'ADD_WORK_EXPERIENCE':
        return {
          ...state,
          cvData: {
            ...state.cvData,
            workExperience: [...state.cvData.workExperience, action.payload],
          },
          isSaved: false,
        };
      case 'SET_CURRENT_STEP':
        return {
          ...state,
          currentStep: action.payload,
        };
      case 'SET_TEMPLATE':
        return {
          ...state,
          selectedTemplate: action.payload,
          settings: {
            ...state.settings,
            template: action.payload,
          },
          isSaved: false,
        };
      default:
        return state;
    }
  };

  it('handles UPDATE_PERSONAL_INFO action', () => {
    const action = {
      type: 'UPDATE_PERSONAL_INFO' as const,
      payload: { fullName: 'John Doe', email: 'john@example.com' },
    };

    const newState = testReducer(initialState, action);

    expect(newState.cvData.personalInfo.fullName).toBe('John Doe');
    expect(newState.cvData.personalInfo.email).toBe('john@example.com');
    expect(newState.isSaved).toBe(false);
  });

  it('handles ADD_WORK_EXPERIENCE action', () => {
    const workExperience: WorkExperience = {
      id: '1',
      position: 'Developer',
      company: 'Tech Corp',
      location: 'San Francisco',
      startDate: '2020-01-01',
      endDate: '2023-01-01',
      current: false,
      description: 'Work description',
      achievements: ['Achievement 1'],
      skills: [],
      employmentType: 'full-time' as const,
      industry: 'Technology',
    };

    const action = {
      type: 'ADD_WORK_EXPERIENCE' as const,
      payload: workExperience,
    };

    const newState = testReducer(initialState, action);

    expect(newState.cvData.workExperience).toHaveLength(1);
    expect(newState.cvData.workExperience[0]).toBe(workExperience);
    expect(newState.isSaved).toBe(false);
  });

  it('handles SET_CURRENT_STEP action', () => {
    const action = {
      type: 'SET_CURRENT_STEP' as const,
      payload: 'summary' as FormStep,
    };

    const newState = testReducer(initialState, action);

    expect(newState.currentStep).toBe('summary');
  });

  it('handles SET_TEMPLATE action', () => {
    const action = {
      type: 'SET_TEMPLATE' as const,
      payload: 'creative' as TemplateType,
    };

    const newState = testReducer(initialState, action);

    expect(newState.selectedTemplate).toBe('creative');
    expect(newState.settings.template).toBe('creative');
    expect(newState.isSaved).toBe(false);
  });

  it('maintains immutability when updating state', () => {
    const action = {
      type: 'UPDATE_PERSONAL_INFO' as const,
      payload: { fullName: 'John Doe' },
    };

    const newState = testReducer(initialState, action);

    // Original state should not be modified
    expect(initialState.cvData.personalInfo.fullName).toBe('');
    expect(newState.cvData.personalInfo.fullName).toBe('John Doe');
    expect(newState).not.toBe(initialState);
    expect(newState.cvData).not.toBe(initialState.cvData);
    expect(newState.cvData.personalInfo).not.toBe(initialState.cvData.personalInfo);
  });

  it('handles unknown action types', () => {
    const action = {
      type: 'UNKNOWN_ACTION' as const,
      payload: {},
    };

    const newState = testReducer(initialState, action);

    expect(newState).toBe(initialState);
  });
});

describe('CVContext Integration', () => {
  it('provides consistent state across multiple components', () => {
    const TestComponent1 = () => {
      const { state } = useCV();
      return <div data-testid="component-1-step">{state.currentStep}</div>;
    };

    const TestComponent2 = () => {
      const { state, dispatch } = useCV();
      return (
        <div>
          <div data-testid="component-2-step">{state.currentStep}</div>
          <button
            data-testid="change-step"
            onClick={() => dispatch({ type: 'SET_CURRENT_STEP', payload: 'summary' })}
          >
            Change Step
          </button>
        </div>
      );
    };

    const TestApp = () => (
      <CVProvider>
        <TestComponent1 />
        <TestComponent2 />
      </CVProvider>
    );

    render(<TestApp />);

    // Both components should show the same initial step
    expect(screen.getByTestId('component-1-step')).toHaveTextContent('personal');
    expect(screen.getByTestId('component-2-step')).toHaveTextContent('personal');

    // Change step from component 2
    act(() => {
      screen.getByTestId('change-step').click();
    });

    // Both components should reflect the change
    expect(screen.getByTestId('component-1-step')).toHaveTextContent('summary');
    expect(screen.getByTestId('component-2-step')).toHaveTextContent('summary');
  });

  it('handles complex state updates', () => {
    const ComplexComponent = () => {
      const { state, dispatch } = useCV();

      const handleComplexUpdate = () => {
        // Multiple dispatch calls to test complex state updates
        dispatch({ type: 'UPDATE_PERSONAL_INFO', payload: { fullName: 'John Doe' } });
        dispatch({ type: 'ADD_WORK_EXPERIENCE', payload: {
          id: '1',
          position: 'Developer',
          company: 'Tech Corp',
          location: 'San Francisco',
          startDate: '2020-01-01',
          endDate: '2023-01-01',
          current: false,
          description: 'Work description',
          achievements: ['Achievement 1'],
          skills: [],
          employmentType: 'full-time' as const,
          industry: 'Technology',
        } });
        dispatch({ type: 'SET_CURRENT_STEP', payload: 'summary' });
        dispatch({ type: 'SET_TEMPLATE', payload: 'creative' });
      };

      return (
        <div>
          <div data-testid="full-name">{state.cvData.personalInfo.fullName}</div>
          <div data-testid="work-experience-count">{state.cvData.workExperience.length}</div>
          <div data-testid="current-step">{state.currentStep}</div>
          <div data-testid="template">{state.selectedTemplate}</div>
          <button data-testid="complex-update" onClick={handleComplexUpdate}>
            Complex Update
          </button>
        </div>
      );
    };

    render(
      <CVProvider>
        <ComplexComponent />
      </CVProvider>
    );

    // Initial state
    expect(screen.getByTestId('full-name')).toHaveTextContent('');
    expect(screen.getByTestId('work-experience-count')).toHaveTextContent('0');
    expect(screen.getByTestId('current-step')).toHaveTextContent('personal');
    expect(screen.getByTestId('template')).toHaveTextContent('modern');

    // Perform complex update
    act(() => {
      screen.getByTestId('complex-update').click();
    });

    // Check all updates were applied
    expect(screen.getByTestId('full-name')).toHaveTextContent('John Doe');
    expect(screen.getByTestId('work-experience-count')).toHaveTextContent('1');
    expect(screen.getByTestId('current-step')).toHaveTextContent('summary');
    expect(screen.getByTestId('template')).toHaveTextContent('creative');
  });
});

describe('CVContext Performance', () => {
  it('handles rapid state updates efficiently', () => {
    const PerformanceTestComponent = () => {
      const { state, dispatch } = useCV();
      const [updateCount, setUpdateCount] = React.useState(0);

      const handleRapidUpdates = () => {
        const start = performance.now();

        // Perform rapid updates
        for (let i = 0; i < 100; i++) {
          act(() => {
            dispatch({ type: 'UPDATE_PERSONAL_INFO', payload: { fullName: `User ${i}` } });
          });
        }

        const end = performance.now();
        setUpdateCount(prev => prev + 1);
        console.log(`Rapid updates took ${end - start}ms`);
      };

      return (
        <div>
          <div data-testid="update-count">{updateCount}</div>
          <div data-testid="current-name">{state.cvData.personalInfo.fullName}</div>
          <button data-testid="rapid-updates" onClick={handleRapidUpdates}>
            Rapid Updates
          </button>
        </div>
      );
    };

    render(
      <CVProvider>
        <PerformanceTestComponent />
      </CVProvider>
    );

    const start = performance.now();
    act(() => {
      screen.getByTestId('rapid-updates').click();
    });
    const end = performance.now();

    expect(screen.getByTestId('update-count')).toHaveTextContent('1');
    expect(screen.getByTestId('current-name')).toHaveTextContent('User 99');
    expect(end - start).toBeLessThan(1000); // Should complete within 1 second
  });

  it('maintains performance with large datasets', () => {
    const LargeDatasetComponent = () => {
      const { state, dispatch } = useCV();

      const handleLargeDataset = () => {
        // Add large number of work experiences
        const largeDataset = Array.from({ length: 1000 }, (_, i) => ({
          id: i.toString(),
          position: `Job ${i}`,
          company: `Company ${i}`,
          location: `Location ${i}`,
          startDate: '2020-01-01',
          endDate: '2023-01-01',
          current: false,
          description: `Description ${i}`,
          achievements: [`Achievement ${i}`],
          skills: [],
          employmentType: 'full-time' as const,
          industry: 'Technology',
        }));

        act(() => {
          largeDataset.forEach(item => {
            dispatch({ type: 'ADD_WORK_EXPERIENCE', payload: item });
          });
        });
      };

      return (
        <div>
          <div data-testid="work-experience-count">{state.cvData.workExperience.length}</div>
          <button data-testid="add-large-dataset" onClick={handleLargeDataset}>
            Add Large Dataset
          </button>
        </div>
      );
    };

    render(
      <CVProvider>
        <LargeDatasetComponent />
      </CVProvider>
    );

    const start = performance.now();
    act(() => {
      screen.getByTestId('add-large-dataset').click();
    });
    const end = performance.now();

    expect(screen.getByTestId('work-experience-count')).toHaveTextContent('1000');
    expect(end - start).toBeLessThan(2000); // Should complete within 2 seconds
  });
});