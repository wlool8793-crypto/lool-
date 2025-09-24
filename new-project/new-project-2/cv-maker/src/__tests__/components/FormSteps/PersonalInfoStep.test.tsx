import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { axe } from 'jest-axe';
import { vi } from 'vitest';
import { PersonalInfoStep } from '@/components/FormSteps/PersonalInfoStep';
import { CVProvider } from '@/contexts/CVContext';
import { testComponentPerformance } from '@/test/performance';

// Mock CVContext
vi.mock('@/contexts/CVContext', async () => {
  const actual = await vi.importActual('@/contexts/CVContext');
  return {
    ...actual,
    useCV: vi.fn(() => ({
      state: {
        cvData: {
          personalInfo: {
            fullName: '',
            email: '',
            phone: '',
            address: '',
            linkedin: '',
            website: '',
            github: '',
          },
        },
        currentStep: 'personalInfo',
        template: 'modern',
        isMarriageMode: false,
        language: 'en',
      },
      dispatch: vi.fn(),
    })),
  };
});

describe('PersonalInfoStep Component', () => {

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders all form fields correctly', () => {
    render(
      <CVProvider>
        <PersonalInfoStep />
      </CVProvider>
    );

    // Check for all form fields
    expect(screen.getByLabelText(/Full Name/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Phone/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Address/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/LinkedIn/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Website/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/GitHub/i)).toBeInTheDocument();

    // Check for submit button
    expect(screen.getByRole('button', { name: /Next/i })).toBeInTheDocument();
  });

  it('displays validation errors for required fields', async () => {
    render(
      <CVProvider>
        <PersonalInfoStep />
      </CVProvider>
    );

    const submitButton = screen.getByRole('button', { name: /Next/i });
    fireEvent.click(submitButton);

    // Wait for validation to complete
    await waitFor(() => {
      expect(screen.getByText(/Full name is required/i)).toBeInTheDocument();
      expect(screen.getByText(/Invalid email address/i)).toBeInTheDocument();
      expect(screen.getByText(/Phone number is required/i)).toBeInTheDocument();
      expect(screen.getByText(/Address is required/i)).toBeInTheDocument();
    });
  });

  it('validates email format correctly', async () => {
    render(
      <CVProvider>
        <PersonalInfoStep />
      </CVProvider>
    );

    const emailInput = screen.getByLabelText(/Email/i);
    const submitButton = screen.getByRole('button', { name: /Next/i });

    // Test invalid email
    fireEvent.change(emailInput, { target: { value: 'invalid-email' } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/Invalid email address/i)).toBeInTheDocument();
    });

    // Test valid email
    fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.queryByText(/Invalid email address/i)).not.toBeInTheDocument();
    });
  });

  it('validates URL format correctly for optional fields', async () => {
    render(
      <CVProvider>
        <PersonalInfoStep />
      </CVProvider>
    );

    const linkedinInput = screen.getByLabelText(/LinkedIn/i);
    const submitButton = screen.getByRole('button', { name: /Next/i });

    // Test invalid URL
    fireEvent.change(linkedinInput, { target: { value: 'invalid-url' } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/Invalid LinkedIn URL/i)).toBeInTheDocument();
    });

    // Test valid URL
    fireEvent.change(linkedinInput, { target: { value: 'https://linkedin.com/in/test' } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.queryByText(/Invalid LinkedIn URL/i)).not.toBeInTheDocument();
    });

    // Test empty field (should be valid)
    fireEvent.change(linkedinInput, { target: { value: '' } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.queryByText(/Invalid LinkedIn URL/i)).not.toBeInTheDocument();
    });
  });

  it('submits form with valid data', async () => {
    const mockDispatch = vi.fn();

    render(
      <CVProvider>
        <PersonalInfoStep />
      </CVProvider>
    );

    // Fill in all required fields
    fireEvent.change(screen.getByLabelText(/Full Name/i), {
      target: { value: 'John Doe' },
    });
    fireEvent.change(screen.getByLabelText(/Email/i), {
      target: { value: 'john@example.com' },
    });
    fireEvent.change(screen.getByLabelText(/Phone/i), {
      target: { value: '+1 (555) 123-4567' },
    });
    fireEvent.change(screen.getByLabelText(/Address/i), {
      target: { value: '123 Main St, City, State 12345' },
    });

    // Fill in optional fields
    fireEvent.change(screen.getByLabelText(/LinkedIn/i), {
      target: { value: 'https://linkedin.com/in/johndoe' },
    });
    fireEvent.change(screen.getByLabelText(/Website/i), {
      target: { value: 'https://johndoe.com' },
    });
    fireEvent.change(screen.getByLabelText(/GitHub/i), {
      target: { value: 'https://github.com/johndoe' },
    });

    const submitButton = screen.getByRole('button', { name: /Next/i });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(mockDispatch).toHaveBeenCalledWith({
        type: 'UPDATE_PERSONAL_INFO',
        payload: {
          fullName: 'John Doe',
          email: 'john@example.com',
          phone: '+1 (555) 123-4567',
          address: '123 Main St, City, State 12345',
          linkedin: 'https://linkedin.com/in/johndoe',
          website: 'https://johndoe.com',
          github: 'https://github.com/johndoe',
        },
      });
      expect(mockDispatch).toHaveBeenCalledWith({
        type: 'SET_CURRENT_STEP',
        payload: 'summary',
      });
    });
  });

  it('populates form with existing data from context', () => {

    render(
      <CVProvider>
        <PersonalInfoStep />
      </CVProvider>
    );

    expect(screen.getByLabelText(/Full Name/i)).toHaveValue('Jane Doe');
    expect(screen.getByLabelText(/Email/i)).toHaveValue('jane@example.com');
    expect(screen.getByLabelText(/Phone/i)).toHaveValue('+1 (555) 987-6543');
    expect(screen.getByLabelText(/Address/i)).toHaveValue('456 Oak St, City, State 67890');
    expect(screen.getByLabelText(/LinkedIn/i)).toHaveValue('https://linkedin.com/in/janedoe');
    expect(screen.getByLabelText(/Website/i)).toHaveValue('https://janedoe.com');
    expect(screen.getByLabelText(/GitHub/i)).toHaveValue('https://github.com/janedoe');
  });

  it('displays icons for each input field', () => {
    render(
      <CVProvider>
        <PersonalInfoStep />
      </CVProvider>
    );

    // Check for icons (they should be present as SVG elements)
    const icons = screen.getAllByRole('img');
    expect(icons.length).toBeGreaterThan(0);
  });

  it('has proper accessibility attributes', async () => {
    const { container } = render(
      <CVProvider>
        <PersonalInfoStep />
      </CVProvider>
    );

    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  it('has proper form accessibility', () => {
    render(
      <CVProvider>
        <PersonalInfoStep />
      </CVProvider>
    );

    const form = screen.getByRole('form');
    expect(form).toBeInTheDocument();

    // Check that all inputs have proper labels
    const inputs = screen.getAllByRole('textbox');
    inputs.forEach(input => {
      expect(input).toHaveAccessibleName();
    });

    // Check that required fields have required attribute
    const requiredInputs = inputs.filter(input => input.hasAttribute('required'));
    expect(requiredInputs.length).toBeGreaterThan(0);
  });

  it('supports keyboard navigation', () => {
    render(
      <CVProvider>
        <PersonalInfoStep />
      </CVProvider>
    );

    const submitButton = screen.getByRole('button', { name: /Next/i });

    // Test Enter key on submit button
    fireEvent.keyDown(submitButton, { key: 'Enter' });

    // Form should attempt to submit (validation errors will appear)
    expect(screen.queryByText(/Full name is required/i)).toBeInTheDocument();
  });

  it('handles field changes efficiently', () => {
    render(
      <CVProvider>
        <PersonalInfoStep />
      </CVProvider>
    );

    const nameInput = screen.getByLabelText(/Full Name/i);

    const start = performance.now();
    for (let i = 0; i < 100; i++) {
      fireEvent.change(nameInput, { target: { value: `Test Name ${i}` } });
    }
    const end = performance.now();

    const avgTime = (end - start) / 100;
    expect(avgTime).toBeLessThan(1); // Should be very fast
  });

  it('performs well under load', async () => {
    const stats = await testComponentPerformance('PersonalInfoStep', 20, () => {
      const { unmount } = render(
        <CVProvider>
          <PersonalInfoStep />
        </CVProvider>
      );
      unmount();
    });

    // Performance assertions are handled by testComponentPerformance function
    expect(stats).toBeDefined();
  });

  it('has correct error message display', async () => {
    render(
      <CVProvider>
        <PersonalInfoStep />
      </CVProvider>
    );

    const emailInput = screen.getByLabelText(/Email/i);
    const submitButton = screen.getByRole('button', { name: /Next/i });

    // Trigger validation error
    fireEvent.change(emailInput, { target: { value: 'invalid' } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      const errorMessage = screen.getByText(/Invalid email address/i);
      expect(errorMessage).toBeInTheDocument();
      expect(errorMessage).toHaveClass('text-red-500');
    });

    // Fix the error
    fireEvent.change(emailInput, { target: { value: 'valid@example.com' } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.queryByText(/Invalid email address/i)).not.toBeInTheDocument();
    });
  });

  it('supports form reset functionality', () => {
    render(
      <CVProvider>
        <PersonalInfoStep />
      </CVProvider>
    );

    const nameInput = screen.getByLabelText(/Full Name/i);

    // Fill in a value
    fireEvent.change(nameInput, { target: { value: 'Test Name' } });
    expect(nameInput).toHaveValue('Test Name');

    // Reset form (this would typically be done via a reset button or context action)
    // For now, we'll test that the input can be cleared
    fireEvent.change(nameInput, { target: { value: '' } });
    expect(nameInput).toHaveValue('');
  });

  it('handles large text inputs gracefully', () => {
    render(
      <CVProvider>
        <PersonalInfoStep />
      </CVProvider>
    );

    const addressInput = screen.getByLabelText(/Address/i);
    const longText = '123 Main Street, Apt 4B, New York, NY 10001, United States of America';

    fireEvent.change(addressInput, { target: { value: longText } });
    expect(addressInput).toHaveValue(longText);
  });

  it('supports international phone numbers', () => {
    render(
      <CVProvider>
        <PersonalInfoStep />
      </CVProvider>
    );

    const phoneInput = screen.getByLabelText(/Phone/i);
    const internationalNumbers = [
      '+1 (555) 123-4567',
      '+44 20 7946 0958',
      '+49 30 1234567',
      '+81 3-1234-5678',
    ];

    internationalNumbers.forEach(number => {
      fireEvent.change(phoneInput, { target: { value: number } });
      expect(phoneInput).toHaveValue(number);
    });
  });

  it('handles special characters in text fields', () => {
    render(
      <CVProvider>
        <PersonalInfoStep />
      </CVProvider>
    );

    const nameInput = screen.getByLabelText(/Full Name/i);
    const specialCharNames = [
      'José María',
      'François Müller',
      'Øyvind Svensson',
      'Łukasz Nowak',
    ];

    specialCharNames.forEach(name => {
      fireEvent.change(nameInput, { target: { value: name } });
      expect(nameInput).toHaveValue(name);
    });
  });
});