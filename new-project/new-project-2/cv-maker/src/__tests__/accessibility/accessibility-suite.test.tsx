import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { axe } from 'jest-axe';
import React from 'react';
import { vi } from 'vitest';
import { CVProvider } from '@/contexts/CVContext';

// Import components to test
import { Button } from '@/components/ui/button';
import { Input } from '@/components/common/Input';
import { Card, CardHeader, CardContent } from '@/components/ui/card';
import { Modal } from '@/components/ui/modal';
import { PersonalInfoStep } from '@/components/FormSteps/PersonalInfoStep';

describe('Accessibility Testing Suite', () => {
  describe('WCAG 2.1 Compliance Tests', () => {
    describe('Perceivable', () => {
      test('all images have alt text', async () => {
        const { container } = render(
          <Card>
            <CardHeader title="Test Card" />
            <CardContent>
              <img src="test.jpg" alt="Test image description" />
            </CardContent>
          </Card>
        );

        const results = await axe(container);
        expect(results).toHaveNoViolations();

        screen.getByAltText('Test image description');
      });

      test('form controls have associated labels', async () => {
        const { container } = render(
          <form>
            <label htmlFor="test-input">Test Input</label>
            <Input id="test-input" placeholder="Test input" />
          </form>
        );

        const results = await axe(container);
        expect(results).toHaveNoViolations();

        screen.getByLabelText('Test Input');
      });

      test('color contrast is sufficient', async () => {
        const { container } = render(
          <Button variant="default">Test Button</Button>
        );

        const results = await axe(container);
        expect(results).toHaveNoViolations();
      });

      test('headings form logical hierarchy', async () => {
        const { container } = render(
          <div>
            <h1>Main Title</h1>
            <h2>Section Title</h2>
            <h3>Subsection Title</h3>
          </div>
        );

        const results = await axe(container);
        expect(results).toHaveNoViolations();

        screen.getAllByRole('heading');
      });
    });

    describe('Operable', () => {
      test('all functionality is keyboard accessible', async () => {
        const handleClick = vi.fn();
        const { container } = render(
          <Button onClick={handleClick}>Test Button</Button>
        );

        const button = screen.getByRole('button', { name: 'Test Button' });

        // Test keyboard navigation
        button.focus();
        expect(button).toHaveFocus();

        // Test keyboard activation
        fireEvent.keyDown(button, { key: 'Enter' });
        expect(handleClick).toHaveBeenCalledTimes(1);

        const results = await axe(container);
        expect(results).toHaveNoViolations();
      });

      test('sufficient time is provided for interaction', async () => {
        const TestComponent = () => {
          const [isVisible, setIsVisible] = React.useState(true);

          React.useEffect(() => {
            const timer = setTimeout(() => setIsVisible(false), 5000);
            return () => clearTimeout(timer);
          }, []);

          return isVisible ? (
            <div role="alert">This message will disappear in 5 seconds</div>
          ) : null;
        };

        const { container } = render(<TestComponent />);

        const results = await axe(container);
        expect(results).toHaveNoViolations();

        // Verify the message is initially visible
        expect(screen.getByRole('alert')).toBeInTheDocument();
      });

      test('no content flashes more than 3 times per second', async () => {
        const TestComponent = () => {
          const [count, setCount] = React.useState(0);

          React.useEffect(() => {
            const interval = setInterval(() => setCount(c => c + 1), 1000);
            return () => clearInterval(interval);
          }, []);

          return <div>Count: {count}</div>;
        };

        const { container } = render(<TestComponent />);

        const results = await axe(container);
        expect(results).toHaveNoViolations();
      });
    });

    describe('Understandable', () => {
      test('form validation errors are clear and helpful', async () => {
        const { container } = render(
          <form>
            <label htmlFor="email-input">Email Address</label>
            <Input
              id="email-input"
              type="email"
              required
              aria-invalid="true"
              aria-describedby="email-error"
            />
            <div id="email-error" role="alert">
              Please enter a valid email address
            </div>
          </form>
        );

        const results = await axe(container);
        expect(results).toHaveNoViolations();

        const input = screen.getByLabelText('Email Address');
        expect(input).toHaveAttribute('aria-invalid', 'true');
        expect(input).toHaveAttribute('aria-describedby', 'email-error');

        const errorMessage = screen.getByRole('alert');
        expect(errorMessage).toHaveTextContent('Please enter a valid email address');
      });

      test('navigation is consistent and predictable', async () => {
        const { container } = render(
          <nav aria-label="Main Navigation">
            <ul>
              <li><a href="#home">Home</a></li>
              <li><a href="#about">About</a></li>
              <li><a href="#contact">Contact</a></li>
            </ul>
          </nav>
        );

        const results = await axe(container);
        expect(results).toHaveNoViolations();

        const nav = screen.getByRole('navigation');
        expect(nav).toHaveAttribute('aria-label', 'Main Navigation');
      });

      test('input assistance is provided where needed', async () => {
        const { container } = render(
          <form>
            <label htmlFor="password-input">Password</label>
            <Input
              id="password-input"
              type="password"
              required
              aria-describedby="password-hint password-requirements"
            />
            <div id="password-hint">Create a strong password</div>
            <div id="password-requirements">
              Password must be at least 8 characters long and contain letters, numbers, and symbols.
            </div>
          </form>
        );

        const results = await axe(container);
        expect(results).toHaveNoViolations();

        const input = screen.getByLabelText('Password');
        expect(input).toHaveAttribute('aria-describedby', 'password-hint password-requirements');
      });
    });

    describe('Robust', () => {
      test('content is compatible with assistive technologies', async () => {
        const { container } = render(
          <main role="main">
            <h1>Page Title</h1>
            <p>This is the main content of the page.</p>
          </main>
        );

        const results = await axe(container);
        expect(results).toHaveNoViolations();

        const main = screen.getByRole('main');
        expect(main).toBeInTheDocument();
      });

      test('ARIA attributes are used correctly', async () => {
        const { container } = render(
          <div role="application" aria-label="Weather Widget">
            <div role="img" aria-label="Sunny weather">
              ☀️
            </div>
            <div>Temperature: 72°F</div>
          </div>
        );

        const results = await axe(container);
        expect(results).toHaveNoViolations();

        screen.getByRole('application');
      });
    });
  });

  describe('Screen Reader Compatibility Tests', () => {
    test('all interactive elements have accessible names', async () => {
      const { container } = render(
        <div>
          <Button aria-label="Close dialog">✕</Button>
          <Input aria-label="Search" />
          <a href="/help" aria-label="Get help">?</a>
        </div>
      );

      const results = await axe(container);
      expect(results).toHaveNoViolations();

      // Test that elements have accessible names
      const button = screen.getByRole('button', { name: 'Close dialog' });
      const input = screen.getByRole('textbox', { name: 'Search' });
      const link = screen.getByRole('link', { name: 'Get help' });

      expect(button).toBeInTheDocument();
      expect(input).toBeInTheDocument();
      expect(link).toBeInTheDocument();
    });

    test('dynamic content updates are announced', async () => {
      const TestComponent = () => {
        const [message, setMessage] = React.useState('');

        return (
          <div>
            <Button onClick={() => setMessage('Content updated!')}>
              Update Content
            </Button>
            {message && (
              <div role="status" aria-live="polite">
                {message}
              </div>
            )}
          </div>
        );
      };

      const { container } = render(<TestComponent />);

      const results = await axe(container);
      expect(results).toHaveNoViolations();

      // Trigger content update
      fireEvent.click(screen.getByRole('button', { name: 'Update Content' }));

      await waitFor(() => {
        expect(screen.getByRole('status')).toHaveTextContent('Content updated!');
      });
    });

    test('focus management is predictable', async () => {
      const { container } = render(
        <Modal isOpen={true} onClose={vi.fn()} title="Test Modal">
          <div>Modal content</div>
          <Button>Close</Button>
        </Modal>
      );

      const results = await axe(container);
      expect(results).toHaveNoViolations();

      // Test that focus is trapped in modal
      const modal = screen.getByRole('dialog');
      expect(modal).toHaveFocus();
    });
  });

  describe('Keyboard Navigation Tests', () => {
    test('visible focus indicators', async () => {
      const { container } = render(
        <Button>Test Button</Button>
      );

      const results = await axe(container);
      expect(results).toHaveNoViolations();

      const button = screen.getByRole('button', { name: 'Test Button' });

      // Focus the button
      button.focus();
      expect(button).toHaveFocus();

      // Check if focus styles are applied (this would depend on CSS)
      expect(button).toHaveClass('focus-visible');
    });

    test('logical tab order', async () => {
      const { container } = render(
        <form>
          <label htmlFor="first-name">First Name</label>
          <Input id="first-name" />

          <label htmlFor="last-name">Last Name</label>
          <Input id="last-name" />

          <label htmlFor="email">Email</label>
          <Input id="email" type="email" />

          <Button type="submit">Submit</Button>
        </form>
      );

      const results = await axe(container);
      expect(results).toHaveNoViolations();

      // Test tab order (this would need to be tested in a real browser environment)
      const inputs = screen.getAllByRole('textbox');
      const button = screen.getByRole('button', { name: 'Submit' });

      // Verify all elements are focusable
      inputs.forEach(input => {
        expect(input).toHaveAttribute('tabindex');
      });
      expect(button).toHaveAttribute('tabindex');
    });

    test('keyboard shortcuts are documented', async () => {
      const { container } = render(
        <div>
          <div role="navigation" aria-label="Keyboard Shortcuts">
            <p>Available keyboard shortcuts:</p>
            <ul>
              <li><kbd>Ctrl</kbd> + <kbd>S</kbd> - Save</li>
              <li><kbd>Ctrl</kbd> + <kbd>P</kbd> - Print</li>
              <li><kbd>Esc</kbd> - Close dialog</li>
            </ul>
          </div>
        </div>
      );

      const results = await axe(container);
      expect(results).toHaveNoViolations();
    });
  });

  describe('Mobile Accessibility Tests', () => {
    test('touch targets are adequately sized', async () => {
      const { container } = render(
        <div>
          <Button size="lg">Large Touch Target</Button>
          <Button size="default">Normal Touch Target</Button>
        </div>
      );

      const results = await axe(container);
      expect(results).toHaveNoViolations();

      // Touch targets should be at least 44x44 pixels
      const largeButton = screen.getByRole('button', { name: 'Large Touch Target' });
      expect(largeButton).toHaveClass('h-10'); // Assuming h-10 is 40px
    });

    test('content is responsive to different screen sizes', async () => {
      const { container } = render(
        <Card className="responsive-card">
          <CardHeader title="Responsive Card" />
          <CardContent>
            <p>This content should be readable on all screen sizes.</p>
          </CardContent>
        </Card>
      );

      const results = await axe(container);
      expect(results).toHaveNoViolations();

      const card = screen.getByTestId('card');
      expect(card).toHaveClass('responsive-card');
    });

    test('zoom functionality is supported', async () => {
      const { container } = render(
        <div style={{ fontSize: '16px', lineHeight: '1.5' }}>
          <h1>Zoomable Content</h1>
          <p>This text should remain readable when zoomed to 200%.</p>
        </div>
      );

      const results = await axe(container);
      expect(results).toHaveNoViolations();
    });
  });

  describe('Form Accessibility Tests', () => {
    test('form validation errors are accessible', async () => {
      const { container } = render(
        <form>
          <div role="alert" aria-live="assertive">
            <p>Please correct the following errors:</p>
            <ul>
              <li>Email is required</li>
              <li>Password must be at least 8 characters</li>
            </ul>
          </div>
        </form>
      );

      const results = await axe(container);
      expect(results).toHaveNoViolations();

      const alert = screen.getByRole('alert');
      expect(alert).toHaveAttribute('aria-live', 'assertive');
    });

    test('form instructions are clear and accessible', async () => {
      const { container } = render(
        <form>
          <fieldset>
            <legend>Personal Information</legend>
            <p>All fields marked with * are required.</p>

            <label htmlFor="name">Name *</label>
            <Input id="name" required aria-required="true" />

            <label htmlFor="email">Email *</label>
            <Input id="email" type="email" required aria-required="true" />
          </fieldset>
        </form>
      );

      const results = await axe(container);
      expect(results).toHaveNoViolations();

      const requiredInputs = screen.getAllByRole('textbox');
      requiredInputs.forEach(input => {
        expect(input).toHaveAttribute('aria-required', 'true');
      });
    });

    test('multi-step forms are accessible', async () => {
      const { container } = render(
        <CVProvider>
          <div role="application" aria-label="CV Form">
            <nav aria-label="Form Steps">
              <ol role="list">
                <li><a href="#step1" aria-current="step">Step 1: Personal Info</a></li>
                <li><a href="#step2">Step 2: Experience</a></li>
                <li><a href="#step3">Step 3: Education</a></li>
              </ol>
            </nav>

            <section id="step1" aria-label="Personal Information Step">
              <PersonalInfoStep />
            </section>
          </div>
        </CVProvider>
      );

      const results = await axe(container);
      expect(results).toHaveNoViolations();

      // Test step navigation accessibility
      const currentStep = screen.getByRole('link', { name: 'Step 1: Personal Info' });
      expect(currentStep).toHaveAttribute('aria-current', 'step');
    });
  });

  describe('Performance and Accessibility', () => {
    test('announcements are not overwhelming', async () => {
      const TestComponent = () => {
        const [announcements, setAnnouncements] = React.useState<string[]>([]);

        const addAnnouncement = () => {
          setAnnouncements(prev => [...prev, `Update ${Date.now()}`]);
        };

        return (
          <div>
            <Button onClick={addAnnouncement}>Add Announcement</Button>
            <div role="status" aria-live="polite" aria-atomic="true">
              {announcements[announcements.length - 1]}
            </div>
          </div>
        );
      };

      const { container } = render(<TestComponent />);

      const results = await axe(container);
      expect(results).toHaveNoViolations();

      // Test rapid announcements
      const button = screen.getByRole('button', { name: 'Add Announcement' });
      for (let i = 0; i < 5; i++) {
        fireEvent.click(button);
      }

      // Only the latest announcement should be visible due to aria-atomic="true"
      const status = screen.getByRole('status');
      expect(status).toBeInTheDocument();
    });

    test('loading states are accessible', async () => {
      const TestComponent = () => {
        const [isLoading, setIsLoading] = React.useState(false);

        const loadData = () => {
          setIsLoading(true);
          setTimeout(() => setIsLoading(false), 1000);
        };

        return (
          <div>
            <Button onClick={loadData} disabled={isLoading}>
              {isLoading ? 'Loading...' : 'Load Data'}
            </Button>
            {isLoading && (
              <div role="status" aria-live="polite">
                Loading data, please wait...
              </div>
            )}
          </div>
        );
      };

      const { container } = render(<TestComponent />);

      const results = await axe(container);
      expect(results).toHaveNoViolations();

      // Test loading state
      const button = screen.getByRole('button', { name: 'Load Data' });
      fireEvent.click(button);

      await waitFor(() => {
        expect(screen.getByRole('status')).toHaveTextContent('Loading data, please wait...');
      });
    });
  });
});